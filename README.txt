			Author: Maui				Addon version: 3.0	  					Blender version: 4.1
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

As of version 3.0:

1. AutoSplitter function. This feature allows to split a whole mesh when the parts have been previously defined by Mark Sharp Edges (CTRL+E) and it will also split the looses part of the edges.
Internally, it will select linked delimited by SHARP edges, which will split the mesh in many meshes as they are. In case there were some problem on non-separating by sharp edges, 
run the operator again with the object selected. This function requires an object to be selected in order to work and the rest will be done automatically.

2. AutoRenamer function. This is the fair complement of AutoSplitter. Once the mesh has been separated by AutoSplitter or manually, 
it will take into account both distance from most closest bones and the bounding box volume of the mesh, so as it takes the main parts (head,hips,torso,arms...) to the bigger object in relation to distance.

3. Parent meshes. This will parent meshes based on the NAMING CONVENTION.

4. Parent caps. This will parent caps based on NAMING CONVENTION.

5. Parent tags. This will parent tags based on NAMING CONVENTION.

6. Create LODs function. This will take every object which is not skeleton, cap or tag and make a dissolve function on all of them together. The best results are provided by UV, generally. 
For better results manual LODing is recommended, however, this is a quick way to prevent negative side effects of not LODing without too much effort. Dissolve limit maximum will make a proportion 
from LOD 3 which will take the Dissolve Limit angle towards model_root_1

7. Set G2 props will set the g2 name of the mesh without the LOD number, will set tags as Tag and will set caps as Off.

8. Create Skin after selecting folder (remove the hint) will create a model_default.skin file with a shader for each object based on first material slot on the object.

9. Assemble vehicle (same as parenting for vehicles)

10. Clean duplicates of existing meshes.

11. Delete empty vertex group. Very useful when you have weighted the whole model from a main mesh and then separate it; it will remove unused vertex groups not affecting the mesh.

=======================================================================================================================================================================


=======================================================================================================================================================================
						If you run into problems, please place a comment or send me a PM.
								Discord can be used aswell: Maui#6422 / vioxini
=======================================================================================================================================================================
