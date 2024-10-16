import bpy
import bmesh
import json
import os
import re

################################################################################################
##                                                                                            ##
##                                        TAGS FUNCTIONS                                      ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateTags(bpy.types.Operator):
    """Creates tags for model_root_0"""
    bl_idname = "tag.create"
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
    bl_idname = "tag.parent"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
            
        for object in bpy.data.objects:  
                
            if not object.g2_prop_tag:
                continue
            
            matrixcopy = object.matrix_world.copy() 
            object.parent = bpy.data.objects[self.parent(object)]
            object.matrix_world = matrixcopy 
        
        return {'FINISHED'} 
    
  
    def parent(self, object):
    
        tags = {
            "*back": "torso",
            "*chestg": "torso",
            "*head_back": "head",
            "*head_cap_torso": "head",
            "*head_eyes": "head",
            "*head_front": "head",
            "*head_left": "head",
            "*head_right": "head",
            "*head_top": "head",
            "*hip_bl": "hips",
            "*hip_br": "hips",
            "*hip_fl": "hips",
            "*hip_fr": "hips",
            "*hip_l": "hips",
            "*hip_r": "hips",
            "*hips_cap_l_leg": "hips",
            "*hips_cap_r_leg": "hips",
            "*hips_cap_torso": "hips",
            "*hips_l_knee": "hips",
            "*hips_r_knee": "hips",
            "*l_arm_cap_l_hand": "l_arm",
            "*l_arm_cap_torso": "l_arm",
            "*l_arm_elbow": "l_arm",
            "*l_hand": "l_hand",
            "*l_hand_cap_l_arm": "l_hand",
            "*l_leg_calf": "l_leg",
            "*l_leg_cap_hips": "l_leg",
            "*l_leg_foot": "l_leg",
            "*lchest_l": "torso",
            "*lchest_r": "torso",
            "*r_arm_cap_r_hand": "r_arm",
            "*r_arm_cap_torso": "r_arm",
            "*r_arm_elbow": "r_arm",
            "*r_hand": "r_hand",
            "*r_hand_cap_r_arm": "r_hand",
            "*r_leg_calf": "r_leg",
            "*r_leg_cap_hips": "r_leg",
            "*r_leg_foot": "r_leg",
            "*shldr_l": "torso",
            "*shldr_r": "torso",
            "*torso_cap_head": "torso",
            "*torso_cap_hips": "torso",
            "*torso_cap_l_arm": "torso",
            "*torso_cap_r_arm": "torso",
            "*uchest_l": "torso",
            "*uchest_r": "torso"
        }
        
        if stripLOD(object) in tags:
            return f"{tags.get(stripLOD(object))}_{getLOD(object)}"
        
        return f"hips_{getLOD(object)}"
        

################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """ Parent all body parts if naming convention is respected """
    bl_idname = "body.parent"
    bl_label = "Parent Meshes"

    def execute(self, context):
        os.system('cls')
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:       
            
            # If stupidtriangle (which has no use) is found, delete it.
            # This is just a way to clean up the model
            if "stupidtriangle" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=True, confirm=True)
                continue
            
            if ("_cap_" in object.name and object.g2_prop_off) or object.g2_prop_tag or "scene_root" in object.name:
                continue
            
            matrixcopy = object.matrix_world.copy() 
            
            if self.parent(object): object.parent = self.parent(object)

            object.matrix_world = matrixcopy
            
            self.triangulate(object)
            
        
        return {'FINISHED'}
   
    def parent(self, object):              
        hierarchy = {
            "r_hand": "r_arm",
            "l_hand": "l_arm",
            "l_arm": "torso",
            "r_arm": "torso",
            "head": "torso",
            "torso": "hips",
            "hips": "model_root",
            "l_leg": "hips",
            "r_leg": "hips"
        }

        splitObject = object.name.split("_")
        length = len(splitObject)
        
        if "model_root" in object.name:
            return bpy.data.objects["scene_root"]
        
        if "skeleton_root" in object.name:
            return bpy.data.objects["scene_root"]
        
        # Define the base name to look up in hierarchy
        def get_hierarchy_name(parts):
            return '_'.join(parts[:2]) if parts[0] in ("l", "r") else parts[0]

        object.g2_prop_name = stripLOD(object)
        object.g2_prop_shader = ""
        object.g2_prop_scale = 100.0
        object.g2_prop_off = False
        object.g2_prop_tag = False

        if length == 2:
            return bpy.data.objects.get(f"{hierarchy[splitObject[0]]}_{splitObject[1]}")

        elif length == 3 and splitObject[0] in ("l", "r"):
            return bpy.data.objects.get(f"{hierarchy[get_hierarchy_name(splitObject[:2])]}_{splitObject[-1]}")
        
        elif length == 3:
            return bpy.data.objects.get(f"{get_hierarchy_name(splitObject)}_{splitObject[-1]}")

        elif length > 3 and splitObject[0] in ("l", "r"):
            return bpy.data.objects.get(f"{'_'.join(splitObject[:2])}_{splitObject[-1]}")

        return bpy.data.objects.get(f"{splitObject[0]}_{splitObject[-1]}")
    
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
    """ Parent all caps """
    bl_idname = "cap.parent"
    bl_label = "Parent Caps"

    def execute(self, context):
        os.system('cls')
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:
            
            c_sign = ("_cap_", "_off")
            roots = ("skeleton_root", "model_root", "scene_root")
            
            if object.g2_prop_tag or any(root in object.name for root in roots):
                continue
            
            if all(sign in object.name for sign in c_sign):
                
                matrixcopy = object.matrix_world.copy() 
                
                object.parent = bpy.data.objects[self.parent(object)]    
                object.matrix_world = matrixcopy # Same problem was found in caps     
                
                object.g2_prop_name = stripLOD(object)
                object.g2_prop_shader = ""
                object.g2_prop_scale = 100.0
                object.g2_prop_off = True
                object.g2_prop_tag = False    
            
        return {'FINISHED'}
    
    def parent(self, object):            
        return "_cap_".join(object.name.split("_cap_", 1)[:1]) + "_" + getLOD(object)  

    
################################################################################################
##                                                                                            ##
##                              SET VEHICLE PARENTING                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_VehicleParent(bpy.types.Operator):
    """ Parent objects, caps and tags from the vehicle """
    bl_idname = "vehicle.parent"
    bl_label = "Assemble Vehicle"

    def execute(self, context):
        os.system('cls')  
        # Check if pelvis is in the skeleton_root, if it's not then we're probably using a vehicle armature
        # Throw an error if not
        if "pelvis" in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No vehiclemodel loaded!")
            
            return {'FINISHED'}
        
        for object in bpy.data.objects:     
            if "scene" in object.name:
                continue
            
            matrixcopy = object.matrix_world.copy() 
            object.parent = bpy.data.objects[self.parent(object) + "_" + getLOD(object)]
            object.matrix_world = matrixcopy
            
        return {'FINISHED'} 
    
    def parent(self, object):  
        """ Goes through the dictionary and return the key value if found, else return body. """
        
        if "skeleton" or "model" in object.name:
            return "scene_root"
           
        dictionary = {
            "body": "model_root",
            "l_wing1": "body",
            "l_wing2": "l_wing1",
            "r_wing1": "body",
            "r_wing2": "r_wing1"
            }
        
        if stripLOD(object) in dictionary:
            return dictionary.get(object)

        return "body"  

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
    bl_idname = "hierarchy.clean"
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
    bl_idname = "file.create_skin"
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
                    
                    clean_material_name = ""
                    
                    if object.active_material.node_tree.nodes.get('Image Texture'):
                        material_name = object.active_material.node_tree.nodes['Image Texture'].image.name 
                        clean_material_name = re.sub(r'\.\d+$', '', material_name)
                    else:
                        material_name = object.active_material.name

                    # Ensure the material name has the correct extension
                    if clean_material_name.endswith('.jpg') or clean_material_name.endswith('.png'):
                        clean_material_name = clean_material_name[:-4]  # Remove .jpg extension
                    else:
                        clean_material_name = material_name
                    
                    modelparts += f"{object.g2_prop_name},models/players/{modelname}/{clean_material_name}.tga\n"
                
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

                if not object.modifiers.get("Armature"):
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
        if "scene_root" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.context.active_object.name = "scene_root"
            
        if "model_root_0" not in bpy.data.objects:
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.context.active_object.name = "model_root_0"
            
        bpy.ops.object.select_all(action='DESELECT')
            
        return {'FINISHED'}  

def getLOD(object):   
    lod = object.name.split("_")[-1]
          
    if lod.isnumeric():
        return str(lod)
    
def stripLOD(object): 
    return object.name.replace(f"_{getLOD(object)}", "")


def register_operators():
    bpy.utils.register_class(OBJECT_OT_BodyParent)
    bpy.utils.register_class(OBJECT_OT_TagParent)
    bpy.utils.register_class(OBJECT_OT_CapParent)
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
    bpy.utils.unregister_class(OBJECT_OT_CapParent)
    bpy.utils.unregister_class(OBJECT_OT_CreateSkinFile)
    bpy.utils.unregister_class(OBJECT_OT_VehicleParent)
    bpy.utils.unregister_class(OBJECT_OT_UnparentAll)
    bpy.utils.unregister_class(OBJECT_OT_CreateTags)
    bpy.utils.unregister_class(OBJECT_OT_Clean)
    bpy.utils.unregister_class(OBJECT_OT_SelectObjectType)
    bpy.utils.unregister_class(OBJECT_OT_SetArmature)
    bpy.utils.unregister_class(OBJECT_OT_RemoveEmptyVertexGroups)
    bpy.utils.unregister_class(OBJECT_OT_CreateRoot)
