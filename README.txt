			Author: Maui							  					Blender version: 4.1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSTALLATION:
Edit ==> Preferences ==> Addons ==> Install
The same way as you would do any addon.

COLLABORATION:
This addon is being coded together with Vioxini. He is a modeller and a coder. He had some nice ideas to implement into the addon.

EXTRA:
mjt came with the idea to support t
Vehicles aswell.

=======================================================================================================================================================================
=======================================================================================================================================================================
LITTLE EXTRA: I included a blender file with skeleton_root and all the default jka tags of every LOD level.
=======================================================================================================================================================================
=======================================================================================================================================================================

=======================================================================================================================================================================
NAMING CONVENTION
=======================================================================================================================================================================

				  The "hierarchy" is shown below.

		 			       head
		    				 |
			    l_hand ==> l_arm ==> torso <== r_arm <== r_hand
		   			         |
	 			      l_leg ==> hips <== r_leg

If you have armor or other accessories for your bodyparts, you should name it like this: head_helmet_x (x: LOD level)


=======================================================================================================================================================================
FUNCTIONS AND USAGE:
=======================================================================================================================================================================

(** Shows a message if you're using this function while having a vehicle skeleton_root in the mix.)
(* Shows a message if you're using this function while having a humanoid skeleton_root in the mix.)

Parent Body: All bodyparts will be parented. ** 
Parent Caps: All caps will be parented. **
Parent Tags: All tags will be parented. **

Make sure to use the naming convention as stated above!

Folder: Select a location where you want to send model_default.skin to.

Set G2 Props: Sets the g2_prop_name for everything
Create Skin File: Creates a model_default.skin file.

Parent Vehicle Parts - parents all vehicle parts, tags and caps *

Create LODs: Creates all the LOD levels and decreases the level of detail accordingly.
You have the option to alter the way it reduces the level of detail, so expertimenting is advised.

Remove Parents - Removes parents from all objects (used for testing my functions)
Clean duplicates in hierarchy: All objects having the name ending with .001 and above, will be deleted.
=======================================================================================================================================================================


=======================================================================================================================================================================
						If you run into problems, please place a comment or send me a PM.
								Discord can be used aswell: Maui#6422
=======================================================================================================================================================================
