Author: Maui									  Blender version: 2.91
-------------------------------------------------------------------------------------------------------

INSTALLATION:
Go to: Edit ==> Preferences ==> Addons ==> Install and select skeleton_tool.zip. Now make sure to click the checkbox to make the addon active.

=================================================================================================================================================================================
FUNCTIONS AND USAGE:
=================================================================================================================================================================================


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
READ ME FIRST: Make sure to select your LOD level at the bottom of the panel first. This determines how the other buttons behave. More information about that below.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


=================================================================================================================================================================================
Create Tags: When this button is selected, Tags which otherwise would have to be copied from default models, will be automaticly created. This works per LOD level. If you have existing tags, it will make the remaining ones. It will also weight the tags as it should be.

EG: Select LOD level 0 -> Press Create Tags
This will create tags for model_root_0
=================================================================================================================================================================================



=================================================================================================================================================================================
Parent Objects/Tags: When this button is selected, every object will be parented according to the hierarchy standards. It will also parent extra objects like l_arm_armor (as an example). If the naming convention is not being used, it will check where the object is located/whether it collides with a body part or not. This function uses the LOD level, so if you have more LOD levels made, make sure to increase or decrease the LOD level and press this button accordingly.

Example: My skeleton has an object named helmet. It will see that it's not a normal object and will see if it collides with an object. If so, it will be parented on that object. 

				  The "hierarchy" is shown below.

		 			       head
		    				 |
			    l_hand ==> l_arm ==> torso <== r_arm <== r_hand
		   			         |
	 			      l_leg ==> hips <== r_leg
				      
After parenting everything, it will set the Ghoul2 properties of the objects and tags as they should be and check if the objects and tags have a modifier called armature set with a value on it, if not.. then the function will do it for you.
=================================================================================================================================================================================



=================================================================================================================================================================================
LOD + 1 and LOD - 1: When these buttons are pressed, the LOD level (shown below the buttons) will either increase or decrease. All buttons above except Transform All and Set Armature will be greyed out when you select an LOD level which has not been made yet.
=================================================================================================================================================================================



=================================================================================================================================================================================
Folder |textbox| Folder icon (pressable): When this button is selected, you have to navigate to the folder where you want the model_default.skin to be created.
=================================================================================================================================================================================



=================================================================================================================================================================================
Create Skin File: When this button is selected, the addon creates a model_default.skin file and places it on the earlier determined folder, which otherwise would be created manually. This will use caps aswell.
=================================================================================================================================================================================



=================================================================================================================================================================================
=================================================================================================================================================================================
						If you run into problems, please place a comment or send me a PM.
								Discord can be used aswell: Maui#6422
==================================================================================================================================================================================================================================================================================================================================================================
