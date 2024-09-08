import os
import sys
import json

CSIDL_PERSONAL = 5       # My Documents
SHGFP_TYPE_CURRENT = 0   # Get current, not default value

HOUDINI_VERSION_REGEX = r"[\d]{1,2}\.[\d]{1,2}"


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


"""
process breakdown
# find houdini preference dirs
# choose dirs to install to
# make sure we're not in a houdini directory already to prevent conflicts
# edit MOPs.json to reflect current directory (where is this EXE?)
# copy MOPs.json to all selected preference dirs
"""


def install_mops(path_list, package):
    """
    Configure the specified package file and copy it to the package path
    in each directory in path_list.
    :param path_list: the list of Houdini pref paths to install to.
    :param package: the JSON file to configure.
    """
    data = None
    install_path = os.path.dirname(package).replace("\\", "/")
    with open(package, 'r') as f:
        data = json.load(f)
    plus = False
    if "MOPS" in data["env"][0].keys():
        data["env"][0]["MOPS"] = install_path
    if "MOPSPLUS" in data["env"][0].keys():
        data["env"][0]["MOPSPLUS"] = install_path
    for path in path_list:
        # create the package directory and get ready to write the modified JSON file
        # print(path)
        packages_path = os.path.join(path, "packages")
        if not os.path.exists(packages_path):
            os.makedirs(packages_path)
        out_path = os.path.join(packages_path, os.path.basename(package))
        # print(json.dumps(data, indent=3))
        with open(out_path, 'w') as f:
            json.dump(data, f, indent=3)


# install_mops(["D:/Documents/houdini18.5"], "D:/Projects/VFX/MOPS/MOPs.json")