import json
try:
	from urllib.request import urlopen
	from urllib.request import Request
except:
	from urllib2 import urlopen
	from urllib2.request import Request

import contextlib
import ssl
import os
import platform
import zipfile
import distutils.dir_util
import hou
import shutil
import traceback
from PySide2 import QtWidgets

import mops_tools

# github URL
MOPS_URL = 'https://api.github.com/repos/toadstorm/MOPS'
# branches (only filters the filenames of the .ZIP files attached as assets for each release!)
BRANCHES = ['stable', 'experimental']
# paths to download zip files to before extraction
if platform.system() == "Windows":
    HOU_TEMP_PATH = os.path.join(os.getenv("APPDATA"), "MOPS")
    HOU_TEMP_PATH_STR = "$APPDATA\\MOPS"
else:
    HOU_TEMP_PATH = os.path.join(os.getenv("HOUDINI_USER_PREF_DIR"), "MOPS")
    HOU_TEMP_PATH_STR = HOU_TEMP_PATH

# local record of branch/version
MOPS_SETTINGS = os.path.join(os.getenv("HOUDINI_USER_PREF_DIR"), "mops_version.json")
HOUDINI_ENV = os.path.join(os.getenv("HOUDINI_USER_PREF_DIR"), "houdini.env")
DEFAULT_SETTINGS = {'branch': "N/A", 'release': "N/A"}

# TODO: urllib is deprecated in python3
# TODO: function to glue this shit together and create the json MOPS_SETTINGS file
# TODO: UI for choosing install path if MOPS env var doesn't exist
# TODO: UI to select releases, install progress window

def get_install_info():
    info = DEFAULT_SETTINGS
    if not os.path.exists(MOPS_SETTINGS):
        return info
    with open(MOPS_SETTINGS, 'r') as f:
        jdata = json.load(f)
    if not jdata:
        jdata = info
    if jdata.get('branch'):
        info['branch'] = jdata['branch']
    if jdata.get('release'):
        info['release'] = jdata['release']
    return info
    
def update_info(branch, release):
    settings = DEFAULT_SETTINGS
    if os.path.exists(MOPS_SETTINGS):
        with open(MOPS_SETTINGS, 'r') as f:
            settings = json.load(f)
    if settings is None:
        settings = DEFAULT_SETTINGS
    info = {'branch': branch, 'release': release}
    settings.update(info)
    with open(MOPS_SETTINGS, 'w') as f:
        json.dump(settings, f)
    # print(settings)
    return(settings)

def get_releases():
    """
    get a list of all MOPS releases on github.
    :return: a list of releases (version numbers).
    """
    releases = list()
    with contextlib.closing(urlopen(Request(MOPS_URL + "/releases"), context=ssl._create_unverified_context())) as response:
        data = response.read()
        # print(data)
        if data == "":
            raise ValueError("No response from release server: {}".format(MOPS_URL + "/releases"))
        j_data = json.loads(data.decode('utf-8'))
        try:
            for release in j_data:
                releases.append(release["tag_name"])
        except TypeError:
            raise ValueError("Rate limit reached. Please try again later.")
    return releases

def filter_releases(releases, type=None):
    if type == 'stable':
        releases = [f for f in releases if not f.endswith('e')]
    elif type == 'experimental':
        releases = [f for f in releases if f.endswith('e')]
    return releases

def get_download_path(release):
    """
    get the .ZIP download URL given a version and branch.
    :param release: the release version
    :return: the download URL
    """
    # response = urllib.urlopen(MOPS_URL + "/releases/tags/" + release)
    jdata = dict()
    with contextlib.closing(urlopen(Request(MOPS_URL + "/releases/tags/" + release), context=ssl._create_unverified_context())) as response:
        data = response.read()
        # print(data)
        if data == "":
            raise ValueError("No response from release server: {}".format(MOPS_URL + "/releases/tags"  + release))
        j_data = json.loads(data.decode('utf-8'))
    return j_data.get('zipball_url')

def download_url(source):
    """
    Download the url source to the local temp folder.
    :param source: the source URL
    :return: the local file path
    """
    filename = 'MOPS_' + os.path.basename(source) + '.zip'
    local_path = os.path.join(HOU_TEMP_PATH, filename)
    # print(local_path)
    if not os.path.exists(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path))
    try:
        zipfile = urlopen(source, context=ssl._create_unverified_context())
        with open(local_path, 'wb') as output:
            output.write(zipfile.read())
    except:
        raise ValueError("Unable to download release from server: {}".format(traceback.format_exc()))
        return
    return local_path
    
def extract_update(zip_file):
    """
    Unzip the downloaded file and copy it to the appropriate install directory.
    :param zipfile: the downloaded zip file location on disk.
    :return: the install directory.
    """
    # the destination is based on the users' local MOPS install directory.
    # hopefully they followed the install instructions...
    extract_path = os.path.join(os.path.dirname(zip_file), os.path.splitext(os.path.basename(zip_file))[0])
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    install_path = hou.getenv('MOPS')
    if install_path is None:
        # prompt user for proper install path...
        install_path = QtWidgets.QFileDialog.getExistingDirectory(hou.qt.mainWindow(), 'Choose install parent directory...', HOUDINI_USER_PREF_DIR)
        install_path = os.path.join(install_path, "MOPS")
    if install_path is None:
        return
    # unzip the folder, then copy the contents of the folder to install_path.
    zip = zipfile.ZipFile(zip_file, 'r', zipfile.ZIP_DEFLATED)
    zip.extractall(extract_path)
    # the extracted item contains another folder, we want the contents
    actual_path = os.path.join(extract_path, os.listdir(extract_path)[0])
    # before we copy everything over, remove the old HDAs to prevent distutils from freaking out.
    if os.path.exists(install_path):
        otls_path = os.path.join(install_path, 'otls')
        if os.path.exists(otls_path):
            otls = [os.path.join(otls_path, f) for f in os.listdir(otls_path) if os.path.splitext(f)[-1] == '.hda']
            if otls:
                for otl in otls:
                    try:
                        if not os.path.isdir(otl):
                            os.remove(otl)
                        else:
                            shutil.rmtree(otl)
                    except:
                        print("unable to remove old HDA file: {}".format(otl))
                        print(traceback.format_exc())

    distutils.dir_util.copy_tree(actual_path, install_path)
    return install_path
    

# environment auto-update

def update_houdini_env(env_file, analytics=False):
    # try to patch houdini.env to use the latest goodies.
    if os.path.exists(env_file):
        env_text = None
        with open(env_file, 'r') as f:
            env_text = f.readlines()
        # check HOUDINI_OTLSCAN_PATH, HOUDINI_TOOLBAR_PATH.
        # if $MOPS/otls or $MOPS/toolbar is in those entries, excise it.
        # add $MOPS to the HOUDINI_PATH. be sure to use the right separator!
        # only do this if "auto-update environment" is enabled!!
        has_mops_var = False
        has_houdini_path = False
        has_analytics_var = False
        separator = ':'
        if platform.system() == 'Windows':
            separator = ';'

        if env_text:
            for index, line in enumerate(env_text):
                if line.lower().startswith('mops ') or line.lower().startswith('mops='):
                    #print('found $MOPS variable')
                    has_mops_var = True
                    continue
                if line.lower().startswith('mops_allow_analytics'):
                    has_analytics_var = True
                    continue
                if line.lower().startswith('houdini_otlscan_path') or line.lower().startswith('houdini_toolbar_path'):
                    if has_mops_var:
                        line_start = line.split('=')[0].strip()
                        #print('found old environment var: {}'.format(line_start))
                        paths = line.split('=')[-1].strip().split(separator)
                        if paths:
                            out_paths = list()
                            for path in paths:
                                if not path.strip().lower().startswith('$mops'):
                                    # keep this
                                    out_paths.append(path)
                            # now replace line with the rejoined paths
                            if out_paths:
                                env_text[index] = line_start + ' = ' + separator.join(out_paths) + '\n'
                            else:
                                env_text.pop(index)

                elif line.lower().startswith('houdini_path'):
                    has_houdini_path = True
                    if has_mops_var:
                        paths = line.split('=')[-1].strip('"').strip().split(separator)
                        if paths:
                            if "$mops" not in [f.lower() for f in paths]:
                                # insert mops variable into houdini_path
                                # if the user has quotes around the paths, make sure to start with a quote
                                if paths[0].startswith('"'):
                                    paths[0] = paths[0][1:]
                                    paths.insert(0, '"$MOPS')
                                else:    
                                    paths.insert(0, "$MOPS")
                            line = "HOUDINI_PATH = " + separator.join(paths) + '\n'
                            env_text[index] = line

            if not has_houdini_path:
                # add houdini_path env var
                env_text.append("HOUDINI_PATH = $MOPS" + separator + "&\n")
            if analytics and not has_analytics_var:
                env_text.append("\nMOPS_ALLOW_ANALYTICS = 1\n")

        if not has_mops_var:
            hou.ui.displayMessage('$MOPS not found in houdini.env! Aborting.')
            return False
        # backup existing env
        backup_path = os.path.join(os.path.dirname(env_file), 'houdini.env.BAK')
        shutil.copyfile(env_file, backup_path)
        with open(env_file, 'w') as f:
            f.writelines(env_text)
        # hou.ui.displayMessage('Environment file updated!')
        return True
    return False
    
# ui shit

class MOPsUpdateWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super(MOPsUpdateWindow, self).__init__(parent)
        self.setWindowTitle("MOPs Auto Updater")
        self.branch = 'stable'
        self.version = None
        self.releases = get_releases()
        self.buildui()
        self.refresh()
        
    def buildui(self):
        main_layout = QtWidgets.QVBoxLayout()
        btn_layout = QtWidgets.QHBoxLayout()
        form = QtWidgets.QGridLayout()
        main_layout.addLayout(form)
        current_branch_label = QtWidgets.QLabel('Current Branch: ')
        current_branch = QtWidgets.QLineEdit()
        current_build_label = QtWidgets.QLabel('Current Build: ')
        current_build = QtWidgets.QLineEdit()
        branch_combo_label = QtWidgets.QLabel('Select Branch: ')
        self.branch_combo = QtWidgets.QComboBox()
        build_combo_label = QtWidgets.QLabel('Select Build: ')
        self.build_combo = QtWidgets.QComboBox()
        self.update_env = QtWidgets.QCheckBox('Auto-Update houdini.env')
        self.update_env.setChecked(False)
        # deprecated
        self.update_env.setVisible(False)
        self.do_analytics = QtWidgets.QCheckBox('Share anonymous MOPs data')
        self.do_analytics.setChecked(False)
        self.do_analytics.setVisible(False)
        apply_btn = QtWidgets.QPushButton('Apply Update')
        cancel_btn = QtWidgets.QPushButton('Cancel')
        form.addWidget(current_branch_label, 0, 0)
        form.addWidget(current_branch, 0, 1)
        form.addWidget(current_build_label, 1, 0)
        form.addWidget(current_build, 1, 1)
        form.addWidget(branch_combo_label, 2, 0)
        form.addWidget(self.branch_combo, 2, 1)
        form.addWidget(build_combo_label, 3, 0)
        form.addWidget(self.build_combo, 3, 1)
        main_layout.addStretch()
        main_layout.addWidget(self.update_env)
        main_layout.addWidget(self.do_analytics)
        main_layout.addLayout(btn_layout)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        self.setLayout(main_layout)
        # defaults
        current_branch.setEnabled(False)
        current_build.setEnabled(False)
        install_info = get_install_info()
        current_branch.setText(install_info['branch'])
        current_build.setText(install_info['release'])
        # signals / slots
        self.branch_combo.currentIndexChanged.connect(self.set_branch)
        self.build_combo.currentIndexChanged.connect(self.set_build)
        apply_btn.clicked.connect(self.apply)
        cancel_btn.clicked.connect(self.close)
        self.update_env.clicked.connect(self.toggle_env_update)
        # window size
        # self.setFixedSize(300, 200)
        
    def toggle_env_update(self):
        do_env = self.update_env.isChecked()
        if do_env:
            self.do_analytics.setEnabled(True)
        else:
            self.do_analytics.setEnabled(False)
        
    def populate_releases(self):
        releases = filter_releases(self.releases, self.branch)
        self.build_combo.clear()
        for i in releases:
            self.build_combo.addItem(i)
        
    def refresh(self):
        self.branch_combo.clear()
        for i in BRANCHES:
            self.branch_combo.addItem(i)
        index = self.branch_combo.findText(self.branch)
        self.branch_combo.setCurrentIndex(index)
        self.populate_releases()
        self.show()
        self.raise_()
        
    def set_branch(self):
        branch_name = self.branch_combo.currentText()
        self.branch = branch_name
        self.populate_releases()
        
    def set_build(self):
        build = self.build_combo.currentText()
        self.build = build
        
    def apply(self):
        # get the download path for the selected release, run download_url,
        # apply_update, then update the local json data file.
        try:
            release = self.build
            url = get_download_path(release)
            dl = download_url(url)
            install_path = extract_update(dl)
            update_info(self.branch, self.build)
            if(self.update_env.isChecked()):
                do_analytics = self.do_analytics.isChecked()
                update_houdini_env(HOUDINI_ENV, do_analytics)
            # compress HDAs
            # mops_tools.collapse_hdas(os.path.join(install_path, 'otls'))
            # notify user
            msg = '{} release {} installed. Please restart Houdini to see changes.'.format(self.branch.upper(), release)
            if self.update_env.isChecked():
                msg += "\nHoudini.env has been modified. A backup has been saved as houdini.env.BAK."
            QtWidgets.QMessageBox.information(self, 'Update complete!', msg)
        except:
            # display error
            err = traceback.format_exc()
            msg = 'Error installing update: \n\n{}'.format(err)
            QtWidgets.QMessageBox.critical(self, 'Error installing update!', msg)
        finally:
            self.close()
        
    
