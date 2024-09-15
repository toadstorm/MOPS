import os
import sys
import json
import re
import settings
import shutil

# insane windows things to fetch user's home folder
CSIDL_PERSONAL = 5       # My Documents
SHGFP_TYPE_CURRENT = 0   # Get current, not default value

# regex for parsing houdini major/minor versions from home folders
HOUDINI_VERSION_REGEX = r"(?P<major>[\d]{1,2})\.(?P<minor>[\d]{1,2})"

def get_windows_docs_path():
    import ctypes.wintypes
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
    return buf.value


def get_windows_houdini_paths():
    """
    Return all detected Houdini configuration paths on Windows.
    """
    root = get_windows_docs_path()
    out_dirs = list()
    if os.path.exists(root):
        houdini_dirs = [f for f in os.listdir(root) if f.startswith("houdini")]
        if houdini_dirs:
            for f in houdini_dirs:
                if settings.SUPPORTED_VERSIONS:
                    # make sure this detected directory fits one of these versions.
                    match = re.match(HOUDINI_VERSION_REGEX, f)
                    version = match.group("major") + "." + match.group("minor")
                    if version not in settings.SUPPORTED_VERSIONS:
                        continue
                full_path = os.path.join(root, f)
                if os.path.isdir(full_path):
                    out_dirs.append(full_path.replace("\\", "/"))
    return out_dirs


def get_macos_houdini_paths():
    """
    Return all detected Houdini configuration paths on Mac OS.
    """
    home = os.path.expanduser("~/Library/Preferences/Houdini")
    out_dirs = list()
    if os.path.exists(home):
        houdini_dirs = [f for f in os.listdir(home) if re.match(HOUDINI_VERSION_REGEX, f)]
        if houdini_dirs:
            for f in houdini_dirs:
                if settings.SUPPORTED_VERSIONS:
                    # make sure this detected directory fits one of these versions.
                    match = re.match(HOUDINI_VERSION_REGEX, f)
                    version = match.group("major") + "." + match.group("minor")
                    if version not in settings.SUPPORTED_VERSIONS:
                        continue
                full_path = os.path.join(home, f)
                if os.path.isdir(full_path):
                    out_dirs.append(full_path)
    return out_dirs


def get_linux_houdini_paths():
    """
    Return all detected Houdini configuration paths on Linux.
    """
    home = os.path.expanduser("~")
    out_dirs = list()
    houdini_dirs = [f for f in os.listdir(home) if f.startswith("houdini")]
    if houdini_dirs:
        for f in houdini_dirs:
            if settings.SUPPORTED_VERSIONS:
                # make sure this detected directory fits one of these versions.
                match = re.match(HOUDINI_VERSION_REGEX, f)
                version = match.group("major") + "." + match.group("minor")
                if version not in settings.SUPPORTED_VERSIONS:
                    continue
            full_path = os.path.join(home, f)
            if os.path.isdir(full_path):
                out_dirs.append(full_path)
    return out_dirs


def get_houdini_prefs_paths():
    if sys.platform == "win32":
        return get_windows_houdini_paths()
    elif sys.platform.lower() == "darwin":
        return get_macos_houdini_paths()
    else:
        return get_linux_houdini_paths()


def find_payload_path():
    this_path = os.path.dirname(__file__)
    iter = 50
    while iter > 0:
        test = os.path.join(this_path, "otls")
        # print(test)
        if os.path.exists(test):
            return os.path.dirname(test)
        this_path = os.path.dirname(this_path)
        iter -= 1
    return None


def find_package_path():
    this_path = os.path.dirname(__file__)
    iter = 50
    while iter > 0:
        test = os.path.join(this_path, settings.FILENAME)
        # print(test)
        if os.path.exists(test):
            return test
        this_path = os.path.dirname(this_path)
        iter -= 1
    return None


def install_package(path_list, package, destination=None, debug=False):
    """
    Configure the specified package file and copy it to the package path
    in each directory in path_list.
    :param path_list: the list of Houdini pref paths to install to.
    :param package: the JSON file to configure.
    :param destination: the location to copy files to. if not specified, uses the existing package path without copying.
    :param debug: doesn't actually save or copy any files and prints a dry run instead.
    """
    data = None
    install_path = os.path.dirname(package).replace("\\", "/")
    if destination:
        install_path = destination
        # copy the contents of the package to this destination.
        payload = find_payload_path()
        if debug:
            print("copying payload at {} to install path {}".format(payload, destination))
        else:
            shutil.copytree(payload, install_path, dirs_exist_ok=True)

    # handle path-based vars (for HOUDINI_PATH or other generic env stuff)
    with open(package, 'r') as f:
        data = json.load(f)
    if settings.PATH_VARS:
        for var in settings.PATH_VARS:
            if var in data["env"][0].keys():
                data["env"][0][var] = install_path
    else:
        data["hpath"] = install_path

    # handle any other specified vars in the settings file
    if settings.OTHER_VARS.keys():
        for k, v in settings.OTHER_VARS.items():
            data["env"][0][k] = v

    for path in path_list:
        # create the package directory and get ready to write the modified JSON file
        # print(path)
        packages_path = os.path.join(path, "packages")
        if not os.path.exists(packages_path):
            os.makedirs(packages_path)
        out_path = os.path.join(packages_path, os.path.basename(package))
        # print(json.dumps(data, indent=3))
        if debug:
            print(json.dumps(data, indent=3))
        else:
            with open(out_path, 'w') as f:
                json.dump(data, f, indent=3)





# install_mops(["D:/Documents/houdini18.5"], "D:/Projects/VFX/MOPS/MOPs.json")