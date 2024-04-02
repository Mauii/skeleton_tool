			Author: Maui				Addon version: 2.5	  					Blender version: 4.1
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSTALLATION:
Edit ==> Preferences ==> Addons ==> Install
The same way as you would do any addon.

COLLABORATION:
This addon is being coded together with Vioxini. He is a modeller and a coder. He had some nice ideas to implement into the addon.

EXTRA:
mjt came with the idea to support Vehicles aswell.

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

Parent body parts 
Parent caps 
Parent tags
Create tags - for model_root_0

Create LODs - which duplicates model_root_0 completely and reduces level of detail on the mesh
You can set the variables on how to dissolve the verts

Create .SKIN - creates a model_default.skin file at the location you selected by using the file browser
Set G2 Props - sets every property your objects need
Assemble Vehicle - parents all body parts, caps and tags of vehicles
Clean duplicates - cleans up everything that has .00 in the name
Unparent all - if for some reason you want all objects to be unparented
Remove Empty Vertex Groups - deletes every unused vertex group in all objects (useful when splitting your weighted model)

Use these functions carefully as some of them need to be used in a specific way.
If you have only have model_root_0 without tags, you click on Create Tags, Parent Tags and then Create LODs
Before creating the skin file you have to select a folder path and then click Set G2 Props and finally the Create .SKIN
=======================================================================================================================================================================


=======================================================================================================================================================================
						If you run into problems, please place a comment or send me a PM.
								Discord can be used aswell: Maui#6422
=======================================================================================================================================================================
