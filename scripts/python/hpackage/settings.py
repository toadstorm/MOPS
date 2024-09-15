# the name of the package file you're configuring.
# this should exist in the same path or in a parent path of this script.
FILENAME = "MOPs.json"

# vars to set install path values for in the package file.
# if this list is empty, the package path will be set for the "hpath" package key.
PATH_VARS = ["MOPS", "MOPSPLUS"]

# any other vars to set via the installer.
# this is a dictionary, i.e. OTHER_VARS = {"HOUDINI_PYTHONWARNINGS: "ignore", "load_package_once": true}
OTHER_VARS = {}

# if your package is version-limited, you can whitelist supported major/minor versions here.
# if it's empty, all found versions of houdini will be available for the package install UI.
# example: SUPPORTED_VERSIONS = ["20.5", "20.0", "19.5"]
SUPPORTED_VERSIONS = []

# window title
TITLE = "MOPs Package Installer"

# intro window graphic. leave blank to exclude.
IMAGE = "mops_logo_01.png"

# intro text
INTRO = """Welcome to the MOPs installation wizard."""

# chooser text
CHOOSER = """Please select a list of compatible Houdini versions to install MOPs to."""

# location text
LOCATION = "Please select the location where you want MOPs extracted to. Do not install MOPs directly into a Houdini " \
           "installation or configuration directory!"

# maximum screen width for labels on dialogs
LABELWIDTH = 800