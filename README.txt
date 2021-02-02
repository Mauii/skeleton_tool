Author: Maui									  Blender version: 2.91
-------------------------------------------------------------------------------------------------------

==============================================================================================================================================================================================================
==                                           INSTALLATION                                            == 
==============================================================================================================================================================================================================
Go to: Edit ==> Preferences ==> Addons ==> Install and select skeleton_tool.zip. Now make sure to click the checkbox to make the addon active.


==============================================================================================================================================================================================================
==                                         FUNCTIONS & USAGE					     ==
==============================================================================================================================================================================================================

=======================================================================================================
READ ME FIRST: Make sure to select your LOD level at the bottom of the panel first. This determines how the other buttons behave. More information about that below.
=======================================================================================================

=======================================================================================================
Transform All: When this button is selected, all Transforms will be set to Deltas. This resets the Scale, Location and Rotation to the default values. (Recommended)
=======================================================================================================

=======================================================================================================
Set Armature: When this button is selected, this will check whether the Armature modifier is present and if not, add it. This will also assign skeleton_root to it.
=======================================================================================================

=======================================================================================================
Create Tags: When this button is selected, Tags which otherwise would have to be copied from default models, will be automaticly created. This works per LOD level. Make sure there are none existing Tags else you will get an error.

EG: Select LOD level 0 -> Press Create Tags
This will create tags for the model_root_0 (and obviously the rest that belongs to model_root_0)
=======================================================================================================

=======================================================================================================
Set G2 Values: When this button is selected, this will set Ghoul2 name to the objects name and when the selected object is a Tag, the Tag checkbox will be filled.

EG: Select LOD level 0 -> Set G2 Values -> Tags (Name: *back Tag checkbox: filled) -> Object(Name: torso_l_armor)
1) Tags get its Ghoul2 properties Name and Tag checkbox filled.
2) Objects get its Ghoul2 properties Name set.
=======================================================================================================

=======================================================================================================
Parent Objects: When this button is selected, every object will be parented according to the hierarchy standards. It will also parent extra objects like l_arm_armor (as an example). Make sure the naming convention is used. This means that every extra object needs to be named to its respective bodypart. This function uses the LOD level, so if you have more LOD levels made, make sure to increase or decrease the LOD level and press this button accordingly.

Example: My skeleton has a helmet. So I named it head_helmet. Once I add boots, I'd name them l_leg_boot and r_leg_boot.

				  The "hierarchy" is shown below.

		 			       head
		    				 |
			    l_hand ==> l_arm ==> torso <== r_arm <== r_hand
		   			         |
	 			      l_leg ==> hips <== r_leg
=======================================================================================================

=======================================================================================================
Parent Tags: When this button is selected, every Tag will be parented according to the hierarchy standards. This means that every extra object needs to be named to its respective bodypart. This function uses the LOD level, so if you have more LOD levels made, make sure to increase or decrease the LOD level and press this button accordingly.
=======================================================================================================

=======================================================================================================
LOD + 1 and LOD - 1: When these buttons are pressed, the LOD level (shown below the buttons) will either increase or decrease. All buttons above except Transform All and Set Armature will be greyed out when you select an LOD level which has not been made yet.
=======================================================================================================

=======================================================================================================
Folder |textbox| Folder icon (pressable): When this button is selected, you can determine in which folder the Skin file (more about this below) will be saved.
=======================================================================================================

=======================================================================================================
Create Skin File: When this button is selected, the addon creates a model_default.skin file and places it on the earlier determined folder, which otherwise would be created manually. This will use caps aswell.
=======================================================================================================


				Hopefully this works out for you!

		If you run into problems, please place a comment or send me a PM.
				Discord can be used aswell: Maui#6422