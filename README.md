MOPs
======

![MOPs logo](https://github.com/toadstorm/MOPS/blob/master/mops_logo_01.png)

Motion OPerators for Houdini, a motion graphics toolkit.

MOPs is intended to be an easy way to manipulate lots of copies of things, leveraging Houdini's packed primitives. The goal is a familiar and fast workflow for motion graphics artists migrating from other platforms, as well as a powerful toolkit for more experienced Houdini artists to quickly design and execute new effects.

MOPs is based on an internal framework of nodes that convert point attributes to packed primitive intrinsic attributes and back again, making it easy for technical artists to develop new MOPs modifiers.

* [**MOPs Wiki**](https://github.com/toadstorm/MOPS/wiki)
* [MOPs Forum](https://forum.motionoperators.com)
* [MOPs Discord](https://discord.gg/TSb3unn6uf)
* [Motionoperators Twitter](https://twitter.com/motionoperators)
* [Motionoperators Instagram](https://www.instagram.com/motionoperators)
* [Facebook User's Group](https://www.facebook.com/groups/616993195326231)


# Installation:

For detailed instructions and troubleshooting, see the [Installation](https://github.com/toadstorm/MOPS/wiki/Installation) page on the MOPs Wiki.

## Step 1: Downloading MOPs

You need to download MOPs from GitHub and then save them somewhere on a local drive or network share. It's important that you **do not** install MOPs directly into your `$HOME/houdiniXX.X` directory or into any other default Houdini installation directory, or else it may not properly be loaded when you start Houdini.

### Option 1 (users who are familiar with Git):
Navigate to the folder you want to contain MOPs, and from BASH / Git BASH type:
`git clone https://github.com/toadstorm/MOPS.git`

### Option 2 (what's Git?):
Download the desired release directly from the [releases page](https://github.com/toadstorm/MOPS/releases) and extract it to your hard drive or network share.

## Step 2: Configuring your Environment


### Option 1: Package

This is by far the easiest method. First, locate your Houdini preferences directory:
* **Windows**: %HOME%/houdiniXX.X/
* **Mac OS**: ~/Preferences/Houdini/XX.X/
* **Linux**: /home/<username>/houdini

Next, look for a directory in your preferences directory called "packages". If it doesn't exist, create it. Then place the MOPS.json file from the MOPs download into that package folder. 

Next, open the MOPS.json file in your package folder in a text editor. Change the "MOPS" variable's value to match the MOPs install path you chose in step 1 (the directory that contains "otls", "scripts", and so on). 

For example, if you downloaded MOPs to /home/henry/MOPs, the line defining the MOPS environment variable should look like this:

**"MOPS": "/home/henry/MOPS"**

Remember that you must use **forward slashes** to describe paths, not backslashes. This includes Windows!


### Option 2: Edit Houdini.env

Only use this method if you cannot use packages for some reason! Packages are much simpler.

You need to add the MOPS installation directory to your Houdini environment file. For more information about the Houdini environment file, see [this help link](https://www.sidefx.com/docs/houdini/basics/config_env.html#setting-environment-variables).
Edit your houdini.env file and create a variable called MOPS that points to the new folder you just extracted MOPs to. The folder you point to should be the one that contains "otls", "scripts", and "toolbar":
`MOPS="/path/to/MOPS"`

Finally, add `$MOPS` to your HOUDINI_PATH:
`HOUDINI_PATH=$HOUDINI_PATH;$MOPS;&`

If you already have a HOUDINI_PATH defined, you can simply append $MOPS to that existing HOUDINI_PATH. For example, if you're using both MOPs and QLib:

```
MOPS="/path/to/MOPS"
QLIB="/path/to/qlib"
HOUDINI_PATH=$HOUDINI_PATH;$QLIB;$MOPS;&
```

*Note:* On Linux and OSX, use `:` instead of `;` to separate your paths. 

It's important that your HOUDINI_PATH always ends in ;&. You can append any other paths you like,
but the last path should be `&`. This will ensure that Houdini's built-in operators work normally.

## Step 3: Test MOPs

To verify your install, open Houdini and drop down a Geometry container, then dive inside. If you see MOPs nodes in the Tab menu, the installation was successful. You can also check the "+" button next to the Shelf menu and look for a shelf called "MOPs" to verify your installation.


# Usage basics:

The main types of nodes in MOPs are the Generators, Modifiers, and Falloff nodes. Generators like the MOPs Instancer create copies of objects. Modifiers transform or otherwise change the objects. Falloffs weight the effects of Modifiers.

The simplest network to start with is the MOPs Instancer. Create a Instancer and an empty File SOP, then add the File SOP as an Instance Object under the MOPS Instancer > Instances tab. The Instancer will create several copies of the File object. If you want to copy onto another mesh, you can change the Distribution Type to Mesh and select an Input Mesh to copy to. If you add multiple Instance objects to the Instancer, by default they will be randomly selected for each instance. You can use the MOPs Index From Attribute node to determine exactly which objects will be instanced where.

Append a MOPs Transform Modifier to the MOPs Instancer. Try playing with the rotation and translation settings. Next, connect a MOPs Shape Falloff in between the MOPs Instancer and the Transform Modifier. The Falloff node by default will change how much the Transform Modifier affects the objects upstream. If you want to reposition the center of the falloff effect, connect a MOPs Transform Falloff node to the second input of the Shape Falloff. All MOPs Modifiers by default will respect the Falloff value assigned to incoming points. 

For more detailed examples, see the "examples" folder for HIP files.


# Developers:
This section is in progress.

MOPs is essentially a handy front-end for manipulating the transformations of Houdini packed primitives. The main node that handles these transformations is the MOPs Apply Attributes SOP. This SOP takes input packed primitives and a matching set of input points with typical instancing attributes, such as p@orient, v@scale, etc. and uses those attributes to modify the primitive intrinsics of the packed primitives in predictable ways. The MOPs Extract Attributes SOP can operate in the other direction, taking the primitive intrinsics and generating instancing point attributes from them. The Falloff nodes create a point attribute called @mops_falloff on the points, which MOPs Apply Attributes will use to weight the applied effects.

Reserved point attributes include:
* f@mops_falloff: the falloff value generated by Falloff nodes. A value of 0 implies that no effect will take place.
* i@mops_index: The index attribute used to decide what object is cloned to what point, if multiple objects are connected to the MOPs Instancer multi-input.
* p@mops_orient: An orientation offset to allow for changes of the local rotation frames without actually rotating the object.
* v@euler: Created internally by the Transform Modifier. If detected, the Apply Attributes SOP will apply these rotations to the incoming points instead of using p@orient. This is to prevent flipping when animating rotations beyond 180 degrees on a given axis.

MOPs is developed and maintained by Henry Foster. Additional contributions by Moritz Schwind, Adam Swaab, Jake Rice, Ian Farnsworth, Kevin Weber, Matt Tillman, and Luca Scheller. 

# Notice:
This software is provided AS-IS, with absolutely no warranty of any kind, express or otherwise. We disclaim any liability for damages resulting from using this software.
