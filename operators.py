import bpy
import bmesh
import json
import os
import re

# Parent mapping
parents = {
    "head": "torso",
    "torso": "hips",
    "hips": "model_root",
    "l_arm": "torso",
    "r_arm": "torso",
    "l_hand": "l_arm",
    "r_hand": "r_arm",
    "l_leg": "hips",
    "r_leg": "hips"
}

################################################################################################
##                                                                                            ##
##                                        CREATE TAGS                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateTags(bpy.types.Operator):
    """
        A class that uses a premade json file to create the original tags
        used by the game. They have multiple functions and are mandatory.
        
        ---------
        Methods:
        ---------
        load_mesh_data(self, file_path)
            This loads the premade json to be passed on to the next method
        
        create_mesh_from_data(self, mesh_data)
            This actually creates the tags using the previous method.
            It sets the proper scaling and g2_properties.
    """
    
    bl_idname = "create.tags"
    bl_label = "Create Tags"

    def execute(self, context):
        # Get the current directory of the addon
        addon_directory = os.path.dirname(os.path.realpath(__file__))

        # Define the JSON file path within the addon directory
        file_path = os.path.join(addon_directory, "tags.json")

        if os.path.exists(file_path):
            mesh_data_list = self.load_mesh_data(file_path)
            for mesh_data in mesh_data_list:
                self.create_mesh_from_data(mesh_data)  # Call with self
            self.report({'INFO'}, "Tags created with vertex groups and weights.")
        else:
            self.report({'ERROR'}, "Tags data file not found.")

        return {'FINISHED'}

    def load_mesh_data(self, file_path):
        """Loads mesh data from a JSON file"""
        with open(file_path, 'r') as f:
            mesh_data_list = json.load(f)
            
        return mesh_data_list

    def create_mesh_from_data(self, mesh_data):
        """Creates a mesh from extracted data and assigns vertex groups and weights"""
        # Check if the object already exists
        if mesh_data['name'] in bpy.data.objects:
            self.report({'INFO'}, f"Object '{mesh_data['name']}' already exists, skipping creation.")
            return bpy.data.objects[mesh_data['name']]

        # Create a new mesh and object if it doesn't exist
        mesh = bpy.data.meshes.new(mesh_data['name'])
        object = bpy.data.objects.new(mesh_data['name'], mesh)

        # Link the object to the Scene Collection
        bpy.context.scene.collection.objects.link(object)

        # Create a BMesh
        bm = bmesh.new()

        # Add vertices
        vertex_map = {}
        for vert in mesh_data['vertices']:
            vertex = bm.verts.new(vert)
            vertex_map[len(vertex_map)] = vertex  # Store the vertex by index

        # Add faces
        for face in mesh_data['faces']:
            bm.faces.new([vertex_map[i] for i in face])

        # Finish BMesh and write to the mesh
        bm.to_mesh(mesh)
        bm.free()

        # Assign vertex groups and weights
        if 'vertex_groups' in mesh_data:
            for group_name, vertices_weights in mesh_data['vertex_groups'].items():
                # Create the vertex group
                vertex_group = object.vertex_groups.new(name=group_name)

                # Assign weights to the vertices
                for vw in vertices_weights:
                    vertex_index = vw['vertex_index']
                    weight = vw['weight']
                    # Assign the weight to the vertex in the group
                    vertex_group.add([vertex_index], weight, 'REPLACE')

        # Scale the object
        object.scale = (object.scale[0] / 10, object.scale[1] / 10, object.scale[2] / 10)

        # Apply transformations
        bpy.context.view_layer.objects.active = object
        object.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        object.select_set(False)

        # Add Armature modifier
        object.modifiers.new(name="Armature", type='ARMATURE')
        object.modifiers["Armature"].object = bpy.data.objects["skeleton_root"]
        
        object.g2_prop_name = object.name[:-2]
        object.g2_prop_shader = ""
        object.g2_prop_scale = 100.0
        object.g2_prop_off = False
        object.g2_prop_tag = True
        
        return object

################################################################################################
##                                                                                            ##
##                                        PARENT TAGS                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_TagParent(bpy.types.Operator):
    """
        This class does exactly as it says. This functions makes sure to parent
        all existing tags onto their respective 'bodypart'.
        
        The 'algorithm' if you can call it that, I choose is fairly simplistic
        but so long my Python skills do not develop further, it will stay this way.
    """
    
    bl_idname = "parent.tags"
    bl_label = "Parent Tags"

    def execute(self, context):
        for object in bpy.data.objects:
            if object.g2_prop_tag:  # Check if the object is a tag
                
                # Ignore the first character and split the name
                name_parts = object.name[1:].split('_')
                
                # Determine the parent based on the naming conventions
                if name_parts[0] in {"l", "r"}:  # Left or right tags
                    parent = f"{name_parts[0]}_{name_parts[1]}_{name_parts[-1]}"
                elif f"{name_parts[0]}_{name_parts[-1]}" in bpy.data.objects:
                    parent = f"{name_parts[0]}_{name_parts[-1]}"
                elif name_parts[0] == "hip":
                    parent = f"hips_{name_parts[-1]}"
                else:
                    parent = f"torso_{name_parts[-1]}"
                
                # Check if the parent exists
                parent_object = bpy.data.objects.get(parent)
                if parent_object:
                    # Copy the world matrix of the child object
                    matrixcopy = object.matrix_world.copy()
                    
                    # Set the parent
                    object.parent = parent_object
                    
                    # Restore the world matrix of the child object
                    object.matrix_world = matrixcopy
                else:
                    print(f"Warning: Parent '{parent}' for tag '{object.name}' not found.")
        
        return {'FINISHED'}


################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """
    This class makes sure to parent all 'bodyparts' if the naming convention
    is respected. It will also make sure that the stupidtriangle(_off) will be
    deleted once and for all, since it has no use.
    
    Methods:
    parent(self, child_object, parent_object)
        This method receives 2 objects. The child, which will be parented
        onto the parent_object.
    
    triangulate(self, object)
        This method saves you the time of having to triangulate the edited,
        newly created or added 'bodyparts' yourself. Since games work on poly's
        this is a mandatory step. You will get an ingame error if you don't do this. 
    """
    
    bl_idname = "parent.objects"
    bl_label = "Parent Objects"

    def execute(self, context):
        os.system('cls')  # Clears the console (Windows only)

        for object in bpy.data.objects:

            # Get rid of the useless stupidtriangle once and for all
            if "stupidtriangle" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=True, confirm=True)
                continue

            # Skip objects with specific properties
            if object.g2_prop_off or object.g2_prop_tag or object.name == "scene_root":
                continue

            if object.type == 'MESH':
                self.triangulate(object)  # Triangulate the object

            if "skeleton_root" in object.name or "model_root" in object.name:
                parent_object = bpy.data.objects["scene_root"]
            
            elif object.name.split("_")[1].isnumeric():
                parent_object = bpy.data.objects[f"{parents[object.name[:-2]]}_{object.name[-1]}"]
                
            else:
                if object.name.startswith("l_") or object.name.startswith("r_"):
                    
                    # If it is an extra piece
                    if len(object.name.split("_")) > 3:
                        object_names = object.name.split("_")
                        parent_object = bpy.data.objects[f"{object_names[0]}_{object_names[1]}_{object.name[-1]}"]
                    
                    # If it is not an extra piece
                    else:
                        parent_object = bpy.data.objects[f"{parents[object.name[:-2]]}_{object.name[-1]}"]
                        
                else:
                    parent_object = bpy.data.objects[f"{object.name.split('_')[0]}_{object.name[-1]}"]
            
            self.parent(object, parent_object)      
                         
        return {'FINISHED'}
        
    def parent(self, child_object, parent_object):
        # Copy the world matrix of the child object
        matrixcopy = child_object.matrix_world.copy()

        # Set the parent
        child_object.parent = parent_object

        # Restore the world matrix of the child object
        child_object.matrix_world = matrixcopy
    
    def triangulate(self, object):
        # Iterate through all objects in the scene
        for object in bpy.data.objects:
            # Check if the object is a mesh
            if object.type == 'MESH':
                mesh = object.data

                # Check for non-triangulated faces
                if any(len(face.vertices) > 3 for face in mesh.polygons):
                    object.modifiers.new(name="Triangulate", type='TRIANGULATE')
                    object.modifiers['Triangulate'].quad_method = 'BEAUTY'
                    object.modifiers['Triangulate'].ngon_method = 'BEAUTY'
                    object.modifiers['Triangulate'].min_vertices = 4  # Minimum vertices for ngons

                    # Apply the modifier
                    bpy.context.view_layer.objects.active = object
                    bpy.ops.object.modifier_apply(modifier="Triangulate")
                    
################################################################################################
##                                                                                            ##
##                                  SET CAP PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CapParent(bpy.types.Operator):
    """
    This class also makes sure to parent all caps (if made) to their respective 'bodyparts'.
    The code itself is pretty simplistic aswell, but it works like a charm. So long my python is not
    improving, this code will stay the way it is.
    """
    
    bl_idname = "parent.caps"
    bl_label = "Parent Caps"

    def execute(self, context):
        os.system('cls')  # Clears the console (Windows only)

        for object in bpy.data.objects:
            # Process only objects with g2_prop_off
            if object.g2_prop_off:
                # Split the object name into parts
                name_parts = object.name.split("_")
                
                if name_parts[0] in {"l", "r"}:
                    # Handle cases like l_arm_cap_0
                    parent_name = f"{name_parts[0]}_{name_parts[1]}_{name_parts[-1]}"
                else:
                    # Handle cases like torso_cap_0
                    parent_name = f"{name_parts[0]}_{name_parts[-1]}"

                # Look for the parent object
                parent_object = bpy.data.objects.get(parent_name)
                
                if parent_object:
                    # Copy the world matrix of the child object
                    matrixcopy = object.matrix_world.copy()

                    # Set the parent
                    object.parent = parent_object

                    # Restore the world matrix of the child object
                    object.matrix_world = matrixcopy
                else:
                    # Print a warning if the parent object is not found
                    print(f"Warning: Parent '{parent_name}' not found for '{object.name}'")
            else:
                continue
                        
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                                  SET G2 PROPERTIES                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_SetG2Properties(bpy.types.Operator):
    """
    This class makes sure to set all g2_properties for all objects within the scene. This is needed for
    JKA to be able to run this model at all. Even modview needs it.
    
    If you want to set a custom shader, change g2_prop_shader after using this function or it will be
    overwritten by emptiness.
    """
    
    bl_idname = "set.g2properties"
    bl_label = "Set G2 Properties"

    def execute(self, context):
        os.system('cls')
        
        for object in bpy.data.objects:
            
            if object.g2_prop_tag:
                continue
            
            object.g2_prop_name = object.name[:-2]
            object.g2_prop_shader = ""
            object.g2_prop_scale = 100.0
                        
            if "_off" in object.name[:-2]:
                object.g2_prop_off = True
                object.g2_prop_tag = False
                
            else:
                object.g2_prop_off = False
                object.g2_prop_tag = False
                                     
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                               REMOVE ALL PARENTING                                         ##
##                                                                                            ##
################################################################################################
   
class OBJECT_OT_UnparentAll(bpy.types.Operator):
    """
    This class simply removes the parent-child relation for all objects, in case you'd need this. It can
    be useful when frankenstein modeling for example:
        
    You want an arm replaced by another model's. Activate this function, remove the arm you don't
    want and press Parent Objects. 
    """
    
    bl_idname = "remove.parent"
    bl_label = "Unparent All"

    def execute(self, context):
        os.system('cls')
        
        for object in bpy.data.objects:
            matrixcopy = object.matrix_world.copy()
            object.parent = None 
            object.matrix_world = matrixcopy

        
        return {'FINISHED'} 
    
################################################################################################
##                                                                                            ##
##                                   CLEAN DUPLICATES                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_Clean(bpy.types.Operator):
    """
    This class simply deletes every object with a name that ends with atleast .001. I've been needing
    this when I started with frankenstein modeling for some reason. Just a little tool to quicken some
    steps.
    """
    
    bl_idname = "clean.hierarchy"
    bl_label = "Clean duplicates"

    def execute(self, context): 
        os.system('cls')
        
        for object in bpy.data.objects:         
            if ".00" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=True, confirm=True)
        
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                              CREATE MODEL_DEFAULT.SKIN                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateSkinFile(bpy.types.Operator):
    """
    This class is the cherry on the cake, the beer on a hot summer day, ...
    It creates the model_default.skin file for you. You make sure to UVMap your objects with the right
    textures, and this class will do the rest for you. Its use is self explanatory once you press it.
    
    Methods:
    invoke(self, context, event)
    This method will open a file explorer window so you can select the path where you want to save it.
    
    get_image(self, object)
    This method will try to find the textures you've set on the objects so it can be added in
    the .skin file.
    """
    bl_idname = "create.skinfile"
    bl_label = "Create .SKIN"
    
    def draw(self, context):
        props = context.scene.settings

        layout = self.layout
        
        # Create a split layout with custom proportions
        split = layout.split(factor=0.3)  # 30% for the label, 70% for the field
        
        # Add properties to the split layout
        col = split.column()  # Label column
        col.label(text="Folder Path:")
        col = split.column()  # Property field column
        col.prop(props, "folder_path", text="")

        split = layout.split(factor=0.3)
        col = split.column()
        col.label(text="Shader Name:")
        col = split.column()
        col.prop(props, "shadername", text="")

        split = layout.split(factor=0.3)
        col = split.column()
        col.label(text="Model Name:")
        col = split.column()
        col.prop(props, "modelname", text="")

    def execute(self, context):       
        props = context.scene.settings
        path = bpy.path.abspath(props.folder_path)
        shadername = props.shadername
        modelname = props.modelname
            
        try:
            with open(path + f"/model_{shadername}.skin", "w") as file: 
                modelparts = ""
                caps = ""
                roots = ("skeleton_root", "model_root", "scene_root")

                for object in bpy.data.objects:
                    # Skip model_root, scene_root and skeleton_root, tags and objects without an active_material set.
                    if object.type != "MESH" or object.g2_prop_tag or any(root in object.name for root in roots):
                        continue
                    
                    if object.g2_prop_off:
                        caps += f"{object.g2_prop_name},models/players/stormtrooper/caps.tga\n"
                        continue
                    
                    materialname = (re.sub(r'\.\d+$', '', self.get_image(object))) if self.get_image(object) else None
                    modelparts += f"{object.g2_prop_name},models/players/{modelname}/{materialname}.tga\n"
                
                output = f"{modelparts}\n{caps}"
                
                # Write to the file
                file.write(output)

            self.report({'INFO'}, "model_default.skin created.")
            
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create .skin file: {e}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def get_image(self, object):
        if object.active_material:
            material = object.active_material
            
            # Check if the material uses nodes
            if material.use_nodes:
                # Get the node tree of the material
                nodes = material.node_tree.nodes
                
                # Find the Principled BSDF node
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Check if Base Color is linked
                        base_color_input = node.inputs['Base Color']
                        
                        if base_color_input.is_linked:
                            # Get the node linked to Base Color
                            linked_node = base_color_input.links[0].from_node
                            
                            if linked_node.type == 'TEX_IMAGE':
                                # Get the image from the image texture node
                                image = linked_node.image
                            else:
                                print("Base Color is not linked to an image texture.")
                        else:
                            print("Base Color is not linked.")
                        break
                else:
                    print("Principled BSDF node not found.")
        else:
            return object.active_material.name.split("/")[-1][:-4]
        return image.name[:-4]

################################################################################################
##                                                                                            ##
##                                     SELECT OBJECT TYPE                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_SelectObjectType(bpy.types.Operator):
    """
    This class is a neat little tool if you need a certain object type to be selected.
    Whether it be tags, caps or the actual 'bodyparts' themselves. It is a multiple choice function,
    so use it as you see fit.
    """
    
    bl_idname = "select.object_type"
    bl_label = "Model part select"
    
    def execute(self, context): 
        os.system('cls')
        
        bpy.ops.object.select_all(action='DESELECT')
        
        settings = bpy.context.scene.settings
            
        for object in bpy.data.objects:
            if object.type == "EMPTY" or object.type == "ARMATURE":
                continue
            
            if settings.meshes and (not object.g2_prop_tag and "_cap_" not in object.name):
                object.select_set(True)
            
            if settings.tags and object.g2_prop_tag:
                object.select_set(True)
            
            if settings.caps and object.g2_prop_off:
                object.select_set(True)
    
        return {'FINISHED'} 

################################################################################################
##                                                                                            ##
##                                        SET ARMATURE                                        ##
##                                                                                            ##
################################################################################################
   
class OBJECT_OT_SetArmature(bpy.types.Operator):
    """
    This class will set the skeleton_root to all objects if they don't have it already.
    """
    
    bl_idname = "set.armaturemod"
    bl_label = "Set Armature Modifier"
    
    def execute(self, context): 
        os.system('cls')

        for object in bpy.data.objects:
        
            if object.type == 'MESH':
                
                # Make sure we have only 1 armature modifier
                for mod in object.modifiers:    
                    if mod.type == 'ARMATURE':
                        object.modifiers.remove(mod)
                
                object.modifiers.new("Armature", type="ARMATURE")       
                object.modifiers["Armature"].object = bpy.data.objects["skeleton_root"] 
    
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                                REMOVE EMPTY VERTEX GROUPS                                  ##
##                                                                                            ##
################################################################################################         
    
class OBJECT_OT_RemoveEmptyVertexGroups(bpy.types.Operator):
    """
    This class will check every object for empty vertex groups. I like my objects clean, hence why I made
    it.
    """
    
    bl_idname = "remove.emptyvgroups"
    bl_label = "Remove Empty VGroups"
    
    def execute(self, context):      
        os.system('cls')
        
        for object in bpy.data.objects:
            
            if "root" in object.name:
                continue
            
            # Check if the object is a mesh
            if object.type == 'MESH':
                # List to store vertex groups to remove
                vertex_groups_to_remove = []

                # Iterate through the vertex groups
                for vgroup in object.vertex_groups:
                    # Initialize the count and weight sum for this vertex group
                    count = 0
                    weight_sum = 0.0
                    
                    # Count the number of vertices assigned to this vertex group and their weights
                    for vertex in object.data.vertices:
                        for group in vertex.groups:
                            if group.group == vgroup.index:
                                count += 1
                                weight_sum += group.weight  # Get the weight of the vertex for this group
                                break  # No need to check other groups for this vertex
                    
                    # Check the conditions: count < 5 or weight_sum < 0.50
                    if count < 5 or weight_sum < 0.100:
                        vertex_groups_to_remove.append(vgroup)

                # Remove the empty vertex groups
                for vgroup in vertex_groups_to_remove:
                    object.vertex_groups.remove(vgroup)

            else:
                print("The active object is not a mesh or no object is selected.")
        
        return {'FINISHED'}       

################################################################################################
##                                                                                            ##
##                                CREATE SCENE/MODEL ROOT                                     ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_CreateRoot(bpy.types.Operator):
    """
    This class will get your hierarchy started by creating a model_root_0 and a scene_root if it doesn't
    exist yet.
    """
    bl_idname = "create.root"
    bl_label = "Create Model/Scene"
    
    def execute(self, context): 
        os.system('cls')

        scene_collection = bpy.context.scene.collection

        # Ensure 'scene_root' exists
        if "scene_root" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
            bpy.context.active_object.name = "scene_root"

        # Ensure 'model_root_0' exists
        if "model_root_0" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
            bpy.context.active_object.name = "model_root_0"

        # Deselect everything
        bpy.ops.object.select_all(action='DESELECT')

            
        return {'FINISHED'}  
    
################################################################################################
##                                                                                            ##
##                                     ORIGIN TO GEOMETRY                                     ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_Origin_to_Geometry(bpy.types.Operator):
    """
    This class will set Origin to Geometry on all objects. A neat little tool when modeling.
    """
    
    bl_idname = "origin.geometry"
    bl_label = "Set Origin to Geometry"
    
    def execute(self, context): 
        os.system('cls')
        
        for object in bpy.context.scene.objects:
            if object.type == 'MESH':
                bpy.context.view_layer.objects.active = object
                obj.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                obj.select_set(False)
                
        print("Origin to Geometry set on all objects.")
        
        return {'FINISHED'}  

def register_operators():
    bpy.utils.register_class(OBJECT_OT_BodyParent)
    bpy.utils.register_class(OBJECT_OT_CapParent)
    bpy.utils.register_class(OBJECT_OT_TagParent)
    bpy.utils.register_class(OBJECT_OT_SetG2Properties)
    bpy.utils.register_class(OBJECT_OT_CreateSkinFile)
    bpy.utils.register_class(OBJECT_OT_UnparentAll)
    bpy.utils.register_class(OBJECT_OT_CreateTags)
    bpy.utils.register_class(OBJECT_OT_Clean)
    bpy.utils.register_class(OBJECT_OT_SelectObjectType)
    bpy.utils.register_class(OBJECT_OT_SetArmature)
    bpy.utils.register_class(OBJECT_OT_RemoveEmptyVertexGroups)
    bpy.utils.register_class(OBJECT_OT_CreateRoot)
    bpy.utils.register_class(OBJECT_OT_Origin_to_Geometry)
    
def unregister_operators():
    bpy.utils.unregister_class(OBJECT_OT_BodyParent)
    bpy.utils.unregister_class(OBJECT_OT_CapParent)
    bpy.utils.unregister_class(OBJECT_OT_TagParent)
    bpy.utils.unregister_class(OBJECT_OT_SetG2Properties)
    bpy.utils.unregister_class(OBJECT_OT_CreateSkinFile)
    bpy.utils.unregister_class(OBJECT_OT_UnparentAll)
    bpy.utils.unregister_class(OBJECT_OT_CreateTags)
    bpy.utils.unregister_class(OBJECT_OT_Clean)
    bpy.utils.unregister_class(OBJECT_OT_SelectObjectType)
    bpy.utils.unregister_class(OBJECT_OT_SetArmature)
    bpy.utils.unregister_class(OBJECT_OT_RemoveEmptyVertexGroups)
    bpy.utils.unregister_class(OBJECT_OT_CreateRoot)
    bpy.utils.unregister_class(OBJECT_OT_Origin_to_Geometry)