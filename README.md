MOPs
======
Motion OPerators for Houdini, a motion graphics toolkit.

MOPs is intended to be an easy way to manipulate lots of copies of things, leveraging Houdini's packed primitives. The goal is a familiar and fast workflow for motion graphics artists migrating from other platforms, as well as a powerful toolkit for more experienced Houdini artists to quickly design and execute new effects.

MOPs is based on an internal framework of nodes that convert point attributes to packed primitive intrinsic attributes and back again, making it easy for technical artists to develop new MOPs modifiers.

### Installation:

Navigate to the folder you want to contain MOPs, and from BASH / Git BASH type:
`git clone https://github.com/toadstorm/MOPS.git`

Edit your houdini.env file and create a variable called MOPS that points to the new folder:
`$MOPS = "/path/to/MOPS"`

Finally, add `$MOPS/otls` to your HOUDINI_OTLSCAN_PATH:
`HOUDINI_OTLSCAN_PATH = $MOPS/otls;@/otls`

### Usage basics:
in progress

### Developers:
in progress- reserved attributes, technical nodes overview