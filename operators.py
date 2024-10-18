import bpy
import bmesh
import json
import os
import re
import difflib

# Hierarchy dictionary
hierarchy = {
    "head": ("cranium", "cervical"),
    "torso": ("thoracic", "upper_lumbar", "lower_lumbar"),
    "hips": ("pelvis", "lfemurYZ", "rfemurYZ"),
    "l_hand": ("lhand",),
    "r_hand": ("rhand",),
    "l_arm": ("lhumerus", "lradius", "lradiusX"),
    "r_arm": ("rhumerus", "rradius", "rradiusX"),
    "l_leg": ("ltalus", "ltibia"),
    "r_leg": ("rtalus", "rtibia")
}

# Parent mapping
parents = {
    "head": "torso",
    "torso": "hips",
    "hips": "model_root",
    "model_root": "scene_root",
    "skeleton_root": "scene_root",
    "l_arm": "torso",
    "r_arm": "torso",
    "l_hand": "l_arm",
    "r_hand": "r_arm",
    "l_leg": "hips",
    "r_leg": "hips"
}

# New hierarchy to store objects
newhierarchy = {}

################################################################################################
##                                                                                            ##
##                                        TAGS FUNCTIONS                                      ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateTags(bpy.types.Operator):
    """Creates tags for model_root_0"""
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
            self.report({'ERROR'}, "Mesh data file not found.")

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
        
        object.g2_prop_name = stripLOD(object)
        object.g2_prop_shader = ""
        object.g2_prop_scale = 100.0
        object.g2_prop_off = False
        object.g2_prop_tag = True
        
        return object


class OBJECT_OT_TagParent(bpy.types.Operator):
    """ Parent all tags """
    bl_idname = "parent.tags"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
            
        for object in bpy.data.objects:
            if object.g2_prop_tag:
                
                pattern = r'^\*([lr]+_[a-z]+)'
                pattern_normal = r'^\*([a-z]+)'
                
                if re.search(pattern, object.name):
                    tag_name = re.search(pattern, object.name).group()
                else:
                    tag_name = re.search(pattern_normal, object.name).group()     
                
                closest_key = get_closest_key(tag_name, newhierarchy)
                
                if closest_key:    
                    parent_object = newhierarchy[closest_key]['object']
                else:
                    parent_object = newhierarchy['torso']['object']
                    
                # Copy the world matrix of the child object
                matrixcopy = object.matrix_world.copy()
                
                # Set the parent
                object.parent = parent_object
                
                # Restore the world matrix of the child object
                object.matrix_world = matrixcopy
        
        return {'FINISHED'} 

################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """ Parent all body parts if naming convention is respected """
    bl_idname = "parent.objects"
    bl_label = "Parent Objects"

    def execute(self, context):
        os.system('cls')
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
            
        for object in bpy.data.objects:
            self.triangulate(object)
            # Ensure the object has vertex groups and is a mesh
            if object.g2_prop_off or object.g2_prop_tag:
                continue
            
            if "model_root" in object.name:
                newhierarchy["model_root"] = {"object": object}
                continue
                
            if "scene_root" in object.name:
                newhierarchy["scene_root"] = {"object": object}
                continue
            
            if "skeleton_root" in object.name:
                newhierarchy["skeleton_root"] = {"object": object}
                continue
            
            if object.vertex_groups:
                # Get all vertex group names for this object
                vertex_group_names = {group.name for group in object.vertex_groups}
                
                # Check for hand groups
                if "l_hand" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["l_hand"]):
                    newhierarchy["l_hand"] = {"object": object}
                    continue
            
                if "r_hand" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["r_hand"]):
                    newhierarchy["r_hand"] = {"object": object}
                    continue
                
                # Check for legs
                if "l_leg" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["l_leg"]):
                    newhierarchy["l_leg"] = {"object": object}
                    continue
                        
                if "r_leg" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["r_leg"]):
                    newhierarchy["r_leg"] = {"object": object}
                    continue
                
                # Check for head
                if "head" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["head"]):
                    newhierarchy["head"] = {"object": object}
                    continue

                # Check for torso
                if "torso" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["torso"]):
                    newhierarchy["torso"] = {"object": object}
                    continue
                        
                # Check for hips
                if "hips" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["hips"]):
                    newhierarchy["hips"] = {"object": object}
                    continue  
                        
                # Check for arms
                if "l_arm" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["l_arm"]):
                    newhierarchy["l_arm"] = {"object": object}
                    continue
                        
                if "r_arm" not in newhierarchy and all(group in vertex_group_names for group in hierarchy["r_arm"]):
                    newhierarchy["r_arm"] = {"object": object}
                    continue                  
            else:
                print(f"{object.name} has no vertex groups!")
                continue
            
        # Parent the basic hierarchy objects
        for part, info in newhierarchy.items():
            
            if part in parents:  # Check if this part has a defined parent
                parent_part = parents[part]
                parent_info = newhierarchy.get(parent_part, None)
                
                if parent_info:
                    info["parent"] = parent_info["object"]  # Set the parent object
                    child_object = info["object"]
                    parent_object = parent_info["object"]
                    
                    # Copy the world matrix of the child object
                    matrixcopy = child_object.matrix_world.copy()
                    
                    # Set the parent
                    child_object.parent = parent_object
                    
                    # Restore the world matrix of the child object
                    child_object.matrix_world = matrixcopy

        # After parenting the base hierarchy (head, torso, hips, ...) parent the remaining parts
        for object in bpy.data.objects:
            
            # Get rid of stupidtriangle once and for all
            if "stupidtriangle" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=True, confirm=True)
                continue
            
            if object.g2_prop_tag:
                continue    
            
            if re.search(r'\d$', object.name):
                if object.name[:-2] not in newhierarchy:
                    
                    pattern = r'^([lr]+_[a-z]+)'
                    
                    match = re.search(pattern, object.name)
                    
                    if match:
                        child_object = match.group(1)
                    else:
                        child_object = object.name.split("_")[0]
                    
                    parent_object = newhierarchy[child_object]['object']
                    
                    # Copy the world matrix of the child object
                    matrixcopy = object.matrix_world.copy()
                    
                    # Set the parent
                    object.parent = parent_object
                    
                    # Restore the world matrix of the child object
                    object.matrix_world = matrixcopy
                    
        return {'FINISHED'}
    
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
##                                  SET G2 PROPERTIES                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_SetG2Properties(bpy.types.Operator):
    """ Prepare objects for export """
    bl_idname = "set.g2properties"
    bl_label = "Set G2 Properties"

    def execute(self, context):
        os.system('cls')
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:
            
            if object.g2_prop_tag:
                continue
            
            object.g2_prop_name = stripLOD(object)
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
    """Removes all parents from objects"""
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
    """Delete duplicates in hierarchy"""
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
    """Create model_default.skin file"""
    bl_idname = "create.skinfile"
    bl_label = "Create .SKIN"
    
    def draw(self, context):
        props = context.scene.settings
        
        layout = self.layout
        layout.prop(props, "folder_path")
        layout.prop(props, "shadername")
        layout.prop(props, "modelname")
    

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

class OBJECT_OT_SelectObjectType(bpy.types.Operator):
    bl_idname = "select.object_type"
    bl_label = "Model part select"
    
    def execute(self, context): 
        os.system('cls')
        bpy.ops.object.select_all(action='DESELECT')
        settings = bpy.context.scene.settings
            
        for object in bpy.data.objects:
            if object.type == "EMPTY" or object.type == "ARMATURE" or "stupidtriangle" in object.name:
                continue
            
            if settings.meshes and (not object.g2_prop_tag and "_cap_" not in object.name):
                object.select_set(True)
            
            if settings.tags and object.g2_prop_tag:
                object.select_set(True)
            
            if settings.caps and object.g2_prop_off:
                object.select_set(True)
    
        return {'FINISHED'} 
    
class OBJECT_OT_SetArmature(bpy.types.Operator):
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
          
    
class OBJECT_OT_RemoveEmptyVertexGroups(bpy.types.Operator):
    bl_idname = "remove.emptyvgroups"
    bl_label = "Remove Empty VGroups"
    
    def execute(self, context): 
        os.system('cls')
        for object in bpy.data.objects:
            
            if object.g2_prop_off and "_cap_" in object.name or object.g2_prop_tag:
                continue
            
            # Check if the object is a mesh
            if object and object.type == 'MESH':
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

    
class OBJECT_OT_CreateRoot(bpy.types.Operator):
    bl_idname = "create.root"
    bl_label = "Create Model/Scene"
    
    def execute(self, context): 
        os.system('cls')
        
        scene_collection = bpy.context.scene.collection
        
        # Check if scene_root exists
        if "scene_root" not in bpy.data.objects:
            # Add the empty object
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            # Rename the newly created object
            new_object = bpy.context.active_object
            new_object.name = "scene_root"
            # Link to the Scene Collection
            scene_collection.objects.link(new_object)

        # Check if model_root_0 exists
        if "model_root_0" not in bpy.data.objects:
            # Add the empty object
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            # Rename the newly created object
            new_object = bpy.context.active_object
            new_object.name = "model_root_0"
            # Link to the Scene Collection
            scene_collection.objects.link(new_object)
            
        bpy.ops.object.select_all(action='DESELECT')
            
        return {'FINISHED'}  

def getLOD(object):   
    return str(object.name[-1])
    
def stripLOD(object): 
    return object.name[:-2]

# Function to find the closest matching key from the dictionary
def get_closest_key(object_name, dictionary):
    # Look for close matches based on the object name
    possible_keys = difflib.get_close_matches(object_name, dictionary.keys(), n=1, cutoff=0.6)
    return possible_keys[0] if possible_keys else None

def register_operators():
    bpy.utils.register_class(OBJECT_OT_BodyParent)
    bpy.utils.register_class(OBJECT_OT_TagParent)
    bpy.utils.register_class(OBJECT_OT_SetG2Properties)
    bpy.utils.register_class(OBJECT_OT_CreateSkinFile)
    bpy.utils.register_class(OBJECT_OT_VehicleParent)
    bpy.utils.register_class(OBJECT_OT_UnparentAll)
    bpy.utils.register_class(OBJECT_OT_CreateTags)
    bpy.utils.register_class(OBJECT_OT_Clean)
    bpy.utils.register_class(OBJECT_OT_SelectObjectType)
    bpy.utils.register_class(OBJECT_OT_SetArmature)
    bpy.utils.register_class(OBJECT_OT_RemoveEmptyVertexGroups)
    bpy.utils.register_class(OBJECT_OT_CreateRoot)
    
def unregister_operators():
    bpy.utils.unregister_class(OBJECT_OT_BodyParent)
    bpy.utils.unregister_class(OBJECT_OT_TagParent)
    bpy.utils.unregister_class(OBJECT_OT_SetG2Properties)
    bpy.utils.unregister_class(OBJECT_OT_CreateSkinFile)
    bpy.utils.unregister_class(OBJECT_OT_VehicleParent)
    bpy.utils.unregister_class(OBJECT_OT_UnparentAll)
    bpy.utils.unregister_class(OBJECT_OT_CreateTags)
    bpy.utils.unregister_class(OBJECT_OT_Clean)
    bpy.utils.unregister_class(OBJECT_OT_SelectObjectType)
    bpy.utils.unregister_class(OBJECT_OT_SetArmature)
    bpy.utils.unregister_class(OBJECT_OT_RemoveEmptyVertexGroups)
    bpy.utils.unregister_class(OBJECT_OT_CreateRoot)