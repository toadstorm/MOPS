import os
import hou
import uuid
import json
import traceback
import threading
import subprocess
import shutil
import platform
from PySide2 import QtCore, QtWebEngineWidgets, QtWidgets

import toolutils

REQUESTS_ENABLED = True

try:
    import requests
except:
    # requests library missing
    REQUESTS_ENABLED = False

home = os.environ["HOUDINI_USER_PREF_DIR"]
CONFIG = os.path.join(home, "hcommon.pref")

GA_TRACKING_ID = "UA-129987675-1"
MOPS_SETTINGS = os.path.join(os.getenv("HOUDINI_USER_PREF_DIR"), "mops.json")
MOPS_FEEDBACK_ADDRESS = "https://www.motionoperators.com/kontakt/"
HOUDINI_BIN = os.path.join(os.getenv("HFS"), "bin")

def get_uuid():
    # check MOPS_SETTINGS file for UUID info
    userid = None
    if not os.path.exists(MOPS_SETTINGS):
        # make the settings file
        userid = uuid.uuid4()
        info = {'branch': "N/A", 'release': "N/A", 'uuid': str(userid)}
        with open(MOPS_SETTINGS, 'w') as f:
            json.dump(info, f)
    else:
        with open(MOPS_SETTINGS, 'r') as f:
            info = json.load(f)
            userid = info.get('uuid')
        if not userid:
            userid = uuid.uuid4()
            info['uuid'] = str(userid)
            with open(MOPS_SETTINGS, 'w') as f:
                json.dump(info, f)
    return userid


def can_send_anonymous_stats():
    can_share = True
    with open(CONFIG, 'r') as f:
        for line in f.readlines():
            if line.startswith("sendAnonymousStats"):
                if line.strip().strip(";").split(":=")[1].strip() == "0":
                    can_share = False
                break
    # print('anonymous stats enabled: {}'.format(can_share))
    override = os.getenv("HOUDINI_ANONYMOUS_STATISTICS", 1)
    if int(override) == 0:
        can_share = False
    override = hou.getenv("MOPS_ALLOW_ANALYTICS")
    if override is not None:
        if int(override) == 0:
            can_share = False
        elif int(override) == 1:
            can_share = True
    # print('stats enabled: {}'.format(can_share))
    return can_share


def track_event(category, action, label=None, value=0):
    """ this actually sends the tracking event to google analytics.
        the event includes an anonymous userid and some information about the node/action. """
    # forget this shit, it's slowing everything down
    return
    userid = str(get_uuid())

    data = {
        'v': '1',  # API Version.
        'tid': GA_TRACKING_ID,  # Tracking ID / Property ID.
        # Anonymous Client Identifier. Ideally, this should be a UUID that
        # is associated with particular user, device, or browser instance.
        'cid': userid,
        't': 'event',  # Event hit type.
        'ec': category,  # Event category.
        'ea': action,  # Event action.
        'el': label,  # Event label.
        'ev': value,  # Event value, must be an integer
    }

    if REQUESTS_ENABLED:
        try:
            response = requests.post(
                'http://www.google-analytics.com/collect', data=data, timeout=0.1)
            # print(response)
        except:
            # print(traceback.format_exc())
            pass


def like_node(node):
    track_event("Like Events", "liked node", str(node.type().name()))
    hou.ui.displayMessage("Thanks for your feedback! We're glad this node is working for you!")


def dislike_node(node):
    track_event("Like Events", "disliked node", str(node.type().name()))
    hou.ui.displayMessage("Thanks for your feedback! We'd appreciate it if you shared any concerns with us at \
     henry@motionoperators.com or mo@motionoperators.com.")


def send_on_create_analytics(node):
    return
    if can_send_anonymous_stats():
        # only track the event if the node were actually just put down (not as a child of a parent node!)
        n = node.node('..')
        if n.type().name().startswith('MOPS'):
            # print('analytics skipping child node')
            return
        track_event("Node Created", str(node.type().name()), str(node.type().definition().version()))


def collapse_hdas(directory):
    """
    Collapses all expanded operators in the given directory.
    :param directory: the "otls" directory where the definitions are stored.
    :return: None
    """
    if not os.path.exists(directory):
        raise(FileNotFoundError, "Directory does not exist!")
    if not os.path.isdir(directory):
        raise(FileNotFoundError, "Given path is not a directory!")
    for i in os.listdir(directory):
        in_dir = os.path.join(directory, i)
        if os.path.isdir(in_dir) and os.path.splitext(i)[-1] == '.hda':
            out_hda = os.path.join(directory, i + '_')
            try:
                proc = None
                if platform.system() == "Windows":
                    hotl = os.path.join(HOUDINI_BIN, "hotl.exe")
                    cmd = [hotl, '-l', in_dir, out_hda]
                    startup = subprocess.STARTUPINFO
                    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup)
                else:
                    hotl = os.path.join(HOUDINI_BIN, "hotl")
                    cmd = [hotl, '-l', in_dir, out_hda]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate()
                if err:
                    raise(RuntimeError, err)
                # rename file and remove original
                shutil.rmtree(in_dir)
                os.rename(out_hda, in_dir)
                print('Collapsed HDA: {}'.format(i))
            except:
                print('Error collapsing {}: {}'.format(i, traceback.format_exc()))

def expand_hdas(directory):
    """
    Expands all collapsed operators in the given directory.
    :param directory: the "otls" directory where the definitions are stored.
    :return: None
    """
    if not os.path.exists(directory):
        raise(FileNotFoundError, "Directory does not exist!")
    if not os.path.isdir(directory):
        raise(FileNotFoundError, "Given path is not a directory!")
    for i in os.listdir(directory):
        in_hda = os.path.join(directory, i)
        if not os.path.isdir(in_hda) and os.path.splitext(i)[-1] == '.hda':

            out_dir = os.path.join(directory, i + '_')
            try:      
                proc = None
                if platform.system() == 'Windows':
                    hotl = os.path.join(HOUDINI_BIN, "hotl.exe")
                    cmd = [hotl, '-t', out_dir, in_hda]
                    startup = subprocess.STARTUPINFO
                    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startup)
                else:
                    hotl = os.path.join(HOUDINI_BIN, "hotl")
                    cmd = [hotl, '-t', out_dir, in_hda]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate()
                if err:
                    raise(RuntimeError, err)
                # rename file and remove original
                os.remove(in_hda)
                os.rename(out_dir, in_hda)
                print('Expanded HDA: {}'.format(i))
            except:
                print('Error expanding {}: {}'.format(i, traceback.format_exc()))


def viewport_selection(kwargs, groupparm="group", grouptypeparm="grouptype"):
    me = kwargs['node']
    # enable active viewport interactive grouping
    if hou.isUIAvailable():
        scene_viewer = toolutils.sceneViewer()
        selection = scene_viewer.currentGeometrySelection()
        if selection:
            me.parm('group').set(selection.mergedSelectionString())
            type = selection.geometryType()
            if type == hou.geometryType.Points:
                me.parm('grouptype').set(3)
            if type == hou.geometryType.Primitives:
                me.parm('grouptype').set(4)

def blackbox_definitions(out_folder):
    # given the selected nodes, create a blackboxed definition for each asset and save to out_folder.
    nodes = hou.selectedNodes()
    for node in nodes:
        definition = node.type().definition()
        if definition:
            def_filename = definition.libraryFilePath()
            out_file = os.path.join(out_folder, os.path.basename(def_filename))
            print("saving blackboxed file: {}".format(out_file))
            definition.save(file_name=out_file, template_node=node, compile_contents=True, black_box=True)