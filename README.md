MOPs
======

![MOPs logo](https://github.com/toadstorm/MOPS/blob/master/mops_logo_01.png)

Motion OPerators for Houdini, a motion graphics toolkit.

MOPs is intended to be an easy way to manipulate lots of copies of things, leveraging Houdini's packed primitives. The goal is a familiar and fast workflow for motion graphics artists migrating from other platforms, as well as a powerful toolkit for more experienced Houdini artists to quickly design and execute new effects.

MOPs is based on an internal framework of nodes that convert point attributes to packed primitive intrinsic attributes and back again, making it easy for technical artists to develop new MOPs modifiers.

[MOPs Plus](https://motionoperators.com/info/mopsplus/) is a paid add-on to MOPs that adds new tools for typography, guided simulations, cameras, and more. 

## LINKS
* [**MOPs Wiki**](https://github.com/toadstorm/MOPS/wiki)
* [**MOPs Discord**](https://discord.gg/TSb3unn6uf)
* [**MOPs Bluesky**](https://bsky.app/profile/motionoperators.com)
* [**MOPs Instagram**](https://www.instagram.com/motionoperators)
* [**MOPs YouTube**](https://www.youtube.com/@motionoperators)


## INSTALLATION

**INSTALLATION PROCEDURE HAS BEEN SIMPLIFIED FROM PREVIOUS RELEASES. PLEASE READ CAREFULLY.**

### Step 1: Downloading MOPs

You need to download MOPs from GitHub and then save them somewhere on a local drive or network share. You can install MOPs pretty much anywhere you like **except**:

* Do **NOT** install to $HOME/houdiniXX.X or $HOME/houdiniX.Y. These are your preferences directories! Only the JSON goes here!
	
* Do **NOT** install to your Houdini program directory!

This directory is your **MOPs installation directory**. For the purposes of this tutorial, we'll use the path `C:\VFX\MOPS` as the example.
	

**Option 1 (users who are familiar with Git)**:
Navigate to the folder you want to contain MOPs (C:\VFX), and from BASH / Git BASH type:
`git clone https://github.com/toadstorm/MOPS.git`

**Option 2 (what's Git?)**:
Download the desired release directly from the [releases page](https://github.com/toadstorm/MOPS/releases) and extract it to your hard drive or network share.

### Step 2: Configuring your Environment

First, locate your **Houdini configuration directory** ($HSITE). This is where houdini.env typically is:

* **Windows**: `My Documents\houdiniXX.Y`
* **Mac OS**: `~/Library/Preferences/Houdini/XX.Y`
* **Linux**: `~/houdiniXX.Y`

Next, look for a directory in there called `packages`. If it doesn't exist, create it. Copy `MOPs.json` from the MOPs installation directory to the `packages` directory, e.g. `My Documents\houdini20.5\packages\MOPS.json`.

Now open `MOPs.json` in a text editor. On line 4, you'll see a variable called "MOPS" followed by a file path in quotes. Change the file path to the **MOPs installation directory** (e.g. `C:/VFX/MOPs`). If you're using Windows, make sure that you are using *forward slashes* and not *backslashes* in the path. The path should remain in quotes. For example:

```
{
   "env": [
      {
         "MOPS": "C:/VFX/MOPS"
      }
   ],
   "hpath": [
      "$MOPS"
   ]
}
```

Save the file.

### Step 3: Test MOPs

To ensure that the installation worked correctly, create a Geometry container and dive inside, then look for the "MOPs" entry in the Tab menu. Also look for a toolbar called "MOPS" in your shelf list. The MOPs Shelf contains some handy tools complete with their own documentation.

### Step 4: Troubleshooting

If you don't see MOPs nodes, there are a few things to check right away.

1. **Are you in a Geometry container?** All MOPs nodes are SOPs, which means you won't see MOPs nodes unless you are inside a Geometry container.
2. **Did you check your MOPs install path**? Make sure that line 4 of MOPs.json is pointing to the **MOPs installation directory** (e.g. `C:/VFX/MOPS`). This directory should contain this `README.md` file.
3. **Do you have a Houdini.env?** If you already have a Houdini.env file in your Houdini configuration directory (specified in Step 2 above), it could be misconfigured. Try renaming it and restarting Houdini. If MOPs works, your environment is misconfigured. Open Houdini.env in a text editor and look for any lines that are defining HOUDINI_PATH. If you see any, ensure that every line defining HOUDINI_PATH includes $HOUDINI_PATH as one of the paths in the variable. Ensure that the last path defined is always the `&` character. For example, `HOUDINI_PATH=$HOUDINI_PATH;$QLIB;/path/to/my_tools/;&`. Use the semicolon to separate paths on Windows. Use the colon to separate paths on Mac OS or Linux.

## LEARNING MOPS

The [MOPs Wiki](https://github.com/toadstorm/MOPS/wiki) here on GitHub has a quick reference list of every MOPs and MOPs Plus node as well as some basic information on how to get started with MOPs. If you prefer written tutorials over videos this is the best place to start.

MOPs (and MOPs Plus) have documentation for every single node in the embedded help cards, as well as an `/examples/` directory included in the installation. It is highly recommended that you take a look in here and see how some of the included setups are put together; this is one of the best ways to understand both MOPs and Houdini.

If you like video tutorials, take a look at Houdini School's three-part series on MOPs, available for free on YouTube:
* [Part 1: MOPs Basics](https://www.youtube.com/watch?v=g9eSle9IVjU)
* [Part 2: Advanced Setups](https://www.youtube.com/watch?v=J2g0v1k6MBs)
* [Part 3: MOPs Math](https://www.youtube.com/watch?v=q_aD6sza6gA)

There is also a [MOPs YouTube channel](https://www.youtube.com/@motionoperators) with some videos primarily about individual MOPs Plus tools.

There is an active [MOPs Discord server](https://discord.gg/TSb3unn6uf) with both novice and expert users of MOPs participating. This is often the best place to get quick help when trying to learn or troubleshoot MOPs.


## DEVELOPERS:

MOPs is essentially a handy front-end for manipulating the transformations of Houdini points and packed primitives. The main node that handles these transformations is the MOPs Apply Attributes SOP. This SOP takes input packed primitives and a matching set of input points with typical instancing attributes, such as p@orient, v@scale, etc. and uses those attributes to modify the primitive intrinsics of the packed primitives in predictable ways. The MOPs Extract Attributes SOP can operate in the other direction, taking the primitive intrinsics and generating instancing point attributes from them. The Falloff nodes create a point attribute called @mops_falloff on the points, which MOPs Apply Attributes will use to weight the applied effects.

Reserved point attributes include:
* f@mops_falloff: the falloff value generated by Falloff nodes. A value of 0 implies that no effect will take place.
* i@mops_index: The index attribute used to decide what object is cloned to what point, if multiple objects are connected to the MOPs Instancer multi-input.
* p@mops_orient: An orientation offset to allow for changes of the local rotation frames without actually rotating the object.
* v@euler: Created internally by the Transform Modifier. If detected, the Apply Attributes SOP will apply these rotations to the incoming points instead of using p@orient. This is to prevent flipping when animating rotations beyond 180 degrees on a given axis.

MOPs is developed and maintained by Henry Foster. Additional contributions by Moritz Schwind, Adam Swaab, Jake Rice, Ian Farnsworth, Kevin Weber, Matt Tillman, and Luca Scheller. 

If you want to help contribute, great! Submit ideas or bug reports to [henry@motionoperators.com](mailto:henry@motionoperators.com) or a pull request here on GitHub!

### Notice:
This software is provided AS-IS, with absolutely no warranty of any kind, express or otherwise. We disclaim any liability for damages resulting from using this software.
