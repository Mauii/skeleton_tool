			Author: Maui							  					Blender version: 4.0.2
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSTALLATION:
Edit ==> Preferences ==> Addons ==> Install
The same way as you would do any addon.


=======================================================================================================================================================================
=======================================================================================================================================================================
LITTLE EXTRA: I uncluded a blender file with skeleton_root and all the default jka tags of every LOD level.
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

Parent Parts: All bodyparts will be parented.
Parent Caps: All caps will be parented.
Parent Tags: All tags will be parented.

Make sure to use the naming convention as stated above!

Clean duplicates in hierarchy: All objects having the name ending with .001 and above, will be deleted.

Folder: Select a location where you want to send model_default.skin to.
Create Skin File: Creates a model_default.skin file. No more tedious manual typing :)

Added functionality for vehicles
Parent Vehicle Parts - parents all vehicle parts, tags and caps
Remove Parents - Removes parents from all objects (used for testing my functions)
=======================================================================================================================================================================


=======================================================================================================================================================================
						If you run into problems, please place a comment or send me a PM.
								Discord can be used aswell: Maui#6422
=======================================================================================================================================================================
