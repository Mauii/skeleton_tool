import bpy
import bmesh
import json
import os
import re

# Parent mapping
parents_dict = {
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


class OBJECT_OT_CreateTags(bpy.types.Operator):
    bl_idname = "create.tags"
    bl_label = "Create Tags"
    bl_description = "Create all tags (if not existing yet)"

    def execute(self, context):
        addon_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(addon_directory, "tags.json")

        if not os.path.exists(file_path):
            self.report({'ERROR'}, "Tags data file not found.")
            return {'CANCELLED'}

        mesh_data_list = self.load_mesh_data(file_path)
        model_roots = self.get_all_model_roots()

        if not model_roots:
            self.report({'WARNING'}, "No model_root objects found.")
            return {'CANCELLED'}

        for lod in model_roots:
            for mesh_data in mesh_data_list:
                self.create_mesh_from_data(mesh_data, lod)

        self.report({'INFO'}, f"Tags created for {len(model_roots)} model_root(s).")
        return {'FINISHED'}
    
    def load_mesh_data(self, file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    def create_mesh_from_data(self, mesh_data, lod):
        name = f"{mesh_data['name']}_{lod}"
        if not self.name_unique_check(name):
            return None

        mesh = bpy.data.meshes.new(name)
        bm = self.create_bmesh_from_mesh(mesh, mesh_data)
        bm.to_mesh(mesh)
        bm.free()

        obj = self.create_object_with_meshdata(name, mesh, mesh_data)
        self.apply_vertex_groups(obj, mesh_data)
        self.set_armature_modifier(obj)
        return obj

    def create_bmesh_from_mesh(self, mesh, mesh_data):
        bm = bmesh.new()
        vertex_map = {}
        for vert in mesh_data['vertices']:
            v = bm.verts.new(vert)
            vertex_map[len(vertex_map)] = v
        for face in mesh_data['faces']:
            bm.faces.new([vertex_map[i] for i in face])
        return bm
    
    def create_object_with_meshdata(self, name, mesh, mesh_data):
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)

        obj.scale = (obj.scale[0] / 10, obj.scale[1] / 10, obj.scale[2] / 10)
        obj.data.transform(obj.matrix_world)
        obj.matrix_world.identity()
        self.apply_g2_properties(obj, mesh_data)
        return obj    

    def set_armature_modifier(self, obj):
        armature = bpy.data.objects.get("skeleton_root")
        if armature:
            mod = obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature
        else:
            self.report({'WARNING'}, "No skeleton_root object found.")


    def name_unique_check(self, name):
        if name in bpy.data.objects:
            self.report({'INFO'}, f"Object '{name}' already exists, skipping creation.")
            return False
        return True

    def apply_vertex_groups(self, obj, mesh_data):
        if 'vertex_groups' in mesh_data:
            for group_name, vertices_weights in mesh_data['vertex_groups'].items():
                vg = obj.vertex_groups.new(name=group_name)
                for vw in vertices_weights:
                    vg.add([vw['vertex_index']], vw['weight'], 'REPLACE')

    def get_all_model_roots(self):
        pattern = re.compile(r"^model_root_(\d+)$")
        model_roots = []
        for obj in bpy.data.objects:
            match = pattern.match(obj.name)
            if match:
                model_roots.append(int(match.group(1)))
        return sorted(model_roots)
    
    def apply_g2_properties(self, obj, mesh_data):
        obj.g2_prop_name = mesh_data['name']
        obj.g2_prop_shader = ""
        obj.g2_prop_off = False
        obj.g2_prop_tag = True

class OBJECT_OT_TagParent(bpy.types.Operator):  
    bl_idname = "parent.tags"
    bl_label = "Parent Tags"
    bl_description = "Parent all tags to their respective parents."

    def execute(self, context):
        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)

                self.check_object(object)
                
                if self.should_skip(object):
                    continue
                                 
                parent_object = self.get_parent(object)
            
                if parent_object:
                    set_parent(object, parent_object)
            except ReferenceError:
                continue
                   
        return {'FINISHED'}

    def get_parent(self, object: bpy.types.Object) -> bpy.types.Object:
        
        try:
            name_parts = object.name[1:].split('_')
            base = name_parts[0]
            lod = name_parts[-1]
            
            # left check
            if base in 'l':
                return bpy.data.objects.get(f"l_{name_parts[1]}_{lod}")
            
            # right check
            if base in 'r':
                return bpy.data.objects.get(f"r_{name_parts[1]}_{lod}")
            
            if base in "hip":
                return bpy.data.objects.get(f"torso_{lod}")

            # hips check
            if base in "hips":
                return bpy.data.objects.get(f"hips_{lod}")
            
            #head check
            if base in "head":
                return bpy.data.objects.get(f"head_{lod}")
                
            # fallback to torso
            return bpy.data.objects.get(f"torso_{lod}")
        except Exception as e:
            print(f"WARNING: {object.name} caused an unknown problem.")
            
    def should_skip(self, object: bpy.types.Object) -> bool:          
        
        # startswith * added as failsafe if tag object didn't get g2 props set 
        if not object.g2_prop_tag or not object.name.startswith("*"):
            return True
        
        return False

    def check_object(self, object: bpy.types.Object) -> None: 
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")
        
        set_g2_properties(self, object)        

################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """ 
    A class that parents all objects to their respective parents. (it will ignore some if the parent is not found).
    Also, it will check if the objects have non-triangulated faces and apply triangulate if needed.
    
    ---------
    Methods:
    ---------
    get_parent(self, object)
        This takes an object and does a simple algorithm to find a suitable parent.
    
    set_parent(self, child, parent)
        This takes the child and parent (found with get_parent) object and does the actual parenting.
        
    should_skip(self, object)
        This runs a check if it is a stupidtriangle or a specific reason to skip the current object.
        If none of these have a reason to skip, it will return False so the main function continues. 
    """
    
    bl_idname = "parent.objects"
    bl_label = "Parent Objects"
    bl_description = "Parent all objects to their respective parents and apply triangulate if needed."

    def execute(self, context):
          # Clears the console (Windows only)

        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)

                if self.should_skip(object):
                    continue
                
                if object.type == 'MESH':
                    triangulate(object)
                
                parent_object = self.get_parent(object)
                
                if parent_object:
                    set_parent(object, parent_object)
            except Exception as e:
                print(f"[ISSUE] Exception {e} caught. Research it, fix the issue, try again.")
                                
        return {'FINISHED'}
       
    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object:
      
        name_parts = child.name.split("_")
        
        try: 
            # Root objects
            if "skeleton_root" in child.name or "model_root" in child.name:
                return bpy.data.objects.get("scene_root")

            # hips, torso, head
            if len(name_parts) > 1 and name_parts[1].isnumeric():
                parent_key = child.name[:-2]
                return bpy.data.objects.get(f"{parents_dict[parent_key]}_{child.name[-1]}")

            # legs, arms, hands
            if child.name.startswith(("l_", "r_")):
                if len(name_parts) > 3:  # extra piece
                    return bpy.data.objects.get(f"{name_parts[0]}_{name_parts[1]}_{child.name[-1]}")
                
                else:
                    parent_key = child.name[:-2]
                    return bpy.data.objects.get(f"{parents_dict[parent_key]}_{child.name[-1]}")

            # Fallback: use first part of name
            else:
                return bpy.data.objects.get(f"{name_parts[0]}_{child.name[-1]}")
        except Exception as e:
            print(f"[ISSUE] Exception {e} caught. Research it, fix the issue, try again.")
                                      
    def should_skip(self, object: bpy.types.Object) -> bool:                
        if "stupidtriangle" in object.name:
            object.select_set(True)
            bpy.ops.object.delete(use_global=True, confirm=True)
            print(f"{object.name} deleted.")
            return True
        
        if object.g2_prop_tag or object.name == "scene_root" or "_cap_" in object.name:
            return True
        
        return False
    
    
################################################################################################
##                                                                                            ##
##                                  SET CAP PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CapParent(bpy.types.Operator):
    """ 
    A class that parents all caps to their respective parents. (it will ignore some if the parent is not found).
    Also, it will check if the caps have non-triangulated faces and apply triangulate if needed.
    
    ---------
    Methods:
    ---------
    get_parent(self, object)
        This takes an object and does a simple algorithm to find a suitable parent.
    
    set_parent(self, child, parent)
        This takes the child and parent (found with get_parent) object and does the actual parenting.
        
    should_skip(self, object)
        This runs a check if it is a stupidtriangle or a specific reason to skip the current object.
        If none of these have a reason to skip, it will return False so the main function continues. 
    """
    
    bl_idname = "parent.caps"
    bl_label = "Parent Caps"
    bl_description = "Parent all caps to their respective parents and apply triangulate if needed."
    
    def execute(self, context):

        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)

                if self.should_skip(object):
                    continue
                
                if object.type == 'MESH':
                    triangulate(object)
                    
                    parent_object = self.get_parent(object)
                    
                    if parent_object:
                        set_parent(object, parent_object)
                    else:
                        print(f"WARNING: Parent not found for {object.name}.")
                        
            except ReferenceError:
                continue
            except Exception as e:
                print(f"[ISSUE] Exception {e} caught. Research it, fix the issue, try again.")
                                    
        return {'FINISHED'}
      
    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object:
        
        name_parts = child.name.split("_")
        
        if name_parts[0] in {"l", "r"}:
            return bpy.data.objects.get(f"{name_parts[0]}_{name_parts[1]}_{name_parts[-1]}")
        
        return bpy.data.objects.get(f"{name_parts[0]}_{name_parts[-1]}")

    def should_skip(self, object: bpy.types.Object) -> bool:                
        if "stupidtriangle" in object.name:
            print(f"{object.name} deleted.")
            object.select_set(True)
            bpy.ops.object.delete(use_global=True, confirm=True)
            return True
        
        if "_cap_" not in object.name or object.g2_prop_tag:
            return True
        
        return False


################################################################################################
##                                                                                            ##
##                                  SET ALL PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_AllParent(bpy.types.Operator):
    
    bl_idname = "parent.all"
    bl_label = "Parent All"
    bl_description = "Parent everything at once."

    def execute(self, context):
        bpy.ops.parent.objects()
        bpy.ops.parent.tags()
        bpy.ops.parent.caps()
        return {'FINISHED'}  
    
    
################################################################################################
##                                                                                            ##
##                                  SET G2 PROPERTIES                                         ##
##                                                                                            ##
################################################################################################
    
class SetG2Properties(bpy.types.Operator):
    """
    This class makes sure to set all g2_properties for all objects within the scene. This is needed for
    JKA to be able to run this model at all. Even modview needs it.
    
    If you want to set a custom shader, change g2_prop_shader after using this function or it will be
    overwritten by emptiness.
    
    ---------
    Methods:
    ---------
    set_g2_properties(self, object)
        This takes an object and sets any Ghoul2 property to what it should be.
        
    should_skip(self, object)
        This runs a check if it is a stupidtriangle or a specific reason to skip the current object.
        If none of these have a reason to skip, it will return False so the main function continues. 
    """
    
    bl_idname = "set.g2properties"
    bl_label = "Set G2 Properties"
    bl_description = "Set all Ghoul2 properties"

    def execute(self, context):
        
        
        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)

                if self.should_skip(object):
                    continue
                
                set_g2_properties(object)
            except ReferenceError:
                continue
                                     
        return {'FINISHED'}
        
    def should_skip(self, object: bpy.types.Object) -> bool:        

        if object.type != 'MESH' or object.type != 'ARMATURE':
            return True
        
        return False
    
    
################################################################################################
##                                                                                            ##
##                               REMOVE ALL PARENTING                                         ##
##                                                                                            ##
################################################################################################
   
class OBJECT_OT_UnparentAll(bpy.types.Operator):
    """ Remove all child-parent relations """
    
    bl_idname = "remove.parent"
    bl_label = "Unparent All"

    def execute(self, context):
        
        for object in bpy.data.objects:
            try:
                matrixcopy = object.matrix_world.copy()
            except ReferenceError:
                # Object has been deleted, skip it
                continue

            object.parent = None 
            object.matrix_world = matrixcopy
        
        return {'FINISHED'} 
    
################################################################################################
##                                                                                            ##
##                                   CLEAN DUPLICATES                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_Clean(bpy.types.Operator):
    """ Delete all objects with atleast .00 in their names """
    
    bl_idname = "clean.hierarchy"
    bl_label = "Clean duplicates"

    def execute(self, context): 

        for object in bpy.data.objects:
            try:
                if ".00" in object.name:
                    object.select_set(True)
                    bpy.ops.object.delete(use_global=True, confirm=True)
            except ReferenceError:
                continue
       
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                              CREATE MODEL_DEFAULT.SKIN                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateSkinFile(bpy.types.Operator):
    """ Create a model_default.skin file """
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
                modelparts = []
                caps = []
                roots = ("skeleton_root", "model_root", "scene_root")

                for object in bpy.data.objects:
                    try:
                        check_object_isinstance(object)

                        # Skip model_root, scene_root and skeleton_root, tags and objects without an active_material set.
                        if object.type != "MESH":
                            continue

                        if object.g2_prop_tag:
                            continue

                        if not object.name.endswith("_0"):
                            continue

                        if any(root in object.name for root in roots):
                            continue
                        
                        if object.g2_prop_off and "_cap_" in object.name:
                            caps.append(f"{object.g2_prop_name},models/players/stormtrooper/caps.tga")
                            continue
                        
                        texture = self.get_image(object)
                        if texture:
                            texture = re.sub(r'\.\d+$', '', texture)
                            texture = os.path.basename(texture)
                            texture = os.path.splitext(texture)[0]
                        materialname = texture if texture else None
                        modelparts.append(f"{object.g2_prop_name},models/players/{modelname}/{materialname}.tga")
                    except ReferenceError:
                        continue
                
                model_lines = modelparts + caps

                output = self.write_output(model_lines)
                
                # Write to the file
                file.write(output)

            self.report({'INFO'}, "model_default.skin created.")
            
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create .skin file: {e}")
            return {'CANCELLED'}
    
    def write_output(self, model: list):
        output = ""
        for part in model:
            output += f"{part}\n"
        return output

    def invoke(self, context, event) -> None:
        return context.window_manager.invoke_props_dialog(self)
    
    def get_image(self, object: bpy.types.Object) -> str | None:
        material = getattr(object, "active_material", None)
        if not material:
            return None

        node_tree = getattr(material, "node_tree", None)
        if not node_tree:
            return None

        image_node = next((node for node in node_tree.nodes if getattr(node, "type", "") == "TEX_IMAGE"), None)
        image = getattr(image_node, "image", None)
        filepath = getattr(image, "filepath", None)
        if not filepath:
            return None

        texture = filepath.replace("\\", "/")
        if "base/" in texture:
            return texture.split("base/", 1)[1]

        return texture
        

################################################################################################
##                                                                                            ##
##                                     SELECT OBJECT TYPE                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_SelectObjectType(bpy.types.Operator):
    """ Select all (caps/tags/objects) or both """
    
    bl_idname = "select.object_type"
    bl_label = "Model part select"
    
    def execute(self, context): 
        
        bpy.ops.object.select_all(action='DESELECT')
        
        settings = bpy.context.scene.settings
            
        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)

                if self.should_skip(object):
                    continue
                
                if settings.meshes and (not object.g2_prop_tag and "_cap_" not in object.name):
                    object.select_set(True)
                
                if settings.tags and object.g2_prop_tag:
                    object.select_set(True)
                
                if settings.caps and object.g2_prop_off and "_cap_" in object.name:
                    object.select_set(True)
            except ReferenceError:
                continue
            except Exception as e:
                print(f"[ISSUE] Exception {e} caught.")
        
        return {'FINISHED'} 
    
    def should_skip(self, object: bpy.types.Object) -> bool:                
        if object.type != 'MESH':
            return True
        
        return False

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
    bl_description = "Setup an armature modifier with skeleton_root"
    
    def execute(self, context): 
        
        skeleton_root = bpy.data.objects.get("skeleton_root")

        for object in bpy.data.objects:
            try:
                if not check_object_isinstance(object):
                    continue

                if self.should_skip(object):
                    continue
                
                # Make sure we have only 1 armature modifier
                for mod in object.modifiers:    
                    if mod.type == 'ARMATURE':
                        object.modifiers.remove(mod)
                
                object.modifiers.new("Armature", type="ARMATURE")       
                object.modifiers["Armature"].object = skeleton_root 

            except ReferenceError:
                continue
        
        return {'FINISHED'}
    
    def should_skip(self, object: bpy.types.Object) -> bool:        
        if "stupidtriangle" in object.name:
            print(f"{object.name} deleted.")
            object.select_set(True)
            bpy.ops.object.delete(use_global=True, confirm=True)
            return True
        
        if object.type != 'MESH':
            return True
        
        return False

################################################################################################
##                                                                                            ##
##                                REMOVE EMPTY VERTEX GROUPS                                  ##
##                                                                                            ##
################################################################################################         
    
class OBJECT_OT_RemoveEmptyVertexGroups(bpy.types.Operator):
    """
    This class will check every object for empty vertex groups.
    """
    
    bl_idname = "remove.emptyvgroups"
    bl_label = "Remove Empty VGroups"
    
    def execute(self, context):      
        for object in bpy.data.objects:
            try:
                check_object_isinstance(object)
                
                if self.should_skip(object):
                    continue
                
                self.remove_vertex_groups(object)
            except ReferenceError:
                continue
            except Exception as e:
                print(f"[ISSUE] Exception {e} caught while removing vertex groups.")
    
        return {'FINISHED'}
    
    def remove_vertex_groups(self, object: bpy.types.Object) -> None:                   
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

    def should_skip(self, object: bpy.types.Object) -> bool:      
        if "stupidtriangle" in object.name:
            print(f"{object.name} deleted.")
            object.select_set(True)
            bpy.ops.object.delete(use_global=True, confirm=True)
            return True
        
        if object.type != 'MESH' or "root" in object.name:
            return True
        
        return False       

################################################################################################
##                                                                                            ##
##                                CREATE SCENE/MODEL ROOT                                     ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_CreateRoot(bpy.types.Operator):
    """ Create scene_root and model_root_0 """
    bl_idname = "create.root"
    bl_label = "Create Model/Scene"
    
    def execute(self, context): 
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
    
class OBJECT_OT_OrigintoGeometry(bpy.types.Operator):
    """ Set Origin to Geometry on all objects """
    
    bl_idname = "origin.geometry"
    bl_label = "Set Origin to Geometry"
    
    def execute(self, context): 

        for object in bpy.context.scene.objects:
            if object.type == 'MESH':
                bpy.context.view_layer.objects.active = object
                object.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                object.select_set(False)
                
        print("Origin to Geometry set on all objects.")
        
        return {'FINISHED'} 

class OBJECT_OT_ReplaceObject(bpy.types.Operator):
    """
    This class will assist your kitbashing even further. Instead of unparenting everything, you can now
    define object 1 (object to replace) and object 2 (object to replace object 1 with).
    
    It will rename object 2 to the name of object 1, it will also parent object 2 to the parent of
    object 1. Then it will see what children object 1 has and parent those to object 2.
    
    ------
    METHODS:
    ------
        
        copy_parenting(self, object1, object2):
            This will copy every parent-child relations of object1 to object2 while
            keeping the previous hierarchy of object2's children intact.
    """
    
    bl_idname = "object.replace_object"
    bl_label = "Replace Object"
    bl_description = "Replace Object 1 with Object 2 (Rename & Take over child-parent relations)"

    def execute(self, context):
        props = context.scene.settings
        object1_name = props.object1
        object2_name = props.object2
        action = props.action

        if object1_name == "" or object2_name == "":
            self.report({'ERROR'}, "Please select both objects")
            return {'CANCELLED'}

        if object1_name == object2_name:
            self.report({'ERROR'}, "Cannot replace an object with itself")
            return {'CANCELLED'}

        object1 = bpy.data.objects[object1_name]
        object2 = bpy.data.objects[object2_name]

        if not object1 or not object2:
            self.report({'ERROR'}, "Objects not found")
            return {'CANCELLED'}
        
        if action == 'DELETE':
            self.copy_parenting(object1, object2)

            old_name = object1.name
            bpy.data.objects.remove(object1)  # delete Object 1
            object2.name = old_name           # rename Object 2

        elif action == 'UNPARENT':
            self.copy_parenting(object1, object2)
            
            old_name = object1.name
            print(f"Object 1 old name: {old_name}")
            print(f"Object 2 old name: {object2.name}")
            object1.name = f"replaced_{old_name}"
            object2.name = old_name           # rename Object 2
            print(f"Object 2 new name: {object2.name}")
            
            matrixcopy = object1.matrix_world.copy()
            object1.parent = None 
            object1.matrix_world = matrixcopy
            
            
        elif action == 'KEEP':
            self.copy_parenting(object1, object2)
            
            old_name = object1.name
            object1.name = f"replaced_{old_name}"
            object2.name = old_name           # rename Object 2
            

        self.report({'INFO'}, f"Replaced {object1_name} with {object2_name}")
        return {'FINISHED'}  
    
    def copy_parenting(self, object1: bpy.types.Object, object2: bpy.types.Object) -> None:            
        old_parent1 = object1.parent
        old_parent2 = object2.parent

        def reparent_preserve_world(child: bpy.types.Object, parent: bpy.types.Object | None):
            matrixcopy = child.matrix_world.copy()
            child.parent = parent
            child.matrix_world = matrixcopy

        # Reparent children of object2 to their previous parent to leave object2 free
        for child in list(object2.children):
            if child is object1:
                continue
            reparent_preserve_world(child, old_parent2)

        # Give object2 the same parent as object1
        object2.parent = old_parent1
        object2.matrix_parent_inverse = object1.matrix_parent_inverse.copy()

        # Reparent all children of object1 to object2
        for child in list(object1.children):
            if child is object2:
                continue
            reparent_preserve_world(child, object2)

        print(f"Copied parenting from {object1.name} to {object2.name}")
        
def triangulate(object: bpy.types.Object) -> None:
    check_object_isinstance(object)
    
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

def set_parent(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    try:
        # Copy the world matrix
        matrixcopy = child.matrix_world.copy()
        
        # Set the parent
        child.parent = parent
        
        # Restore the world transform
        child.matrix_world = matrixcopy
        
        print(f"{child.name} parented to {parent.name}")
        
    except Exception as e:
        print(f"[ISSUE] Exception {e} caught. Research it, fix the issue, try again.")     

def check_object_isinstance(object: bpy.types.Object) -> bool:
    if not isinstance(object, bpy.types.Object):
        raise TypeError(f"{object.name} must be an Object.")
    return True

def set_g2_properties(self, object: bpy.types.Object) -> None:
    object.g2_prop_name = object.name[:-2]
    object.g2_prop_shader = "" # Used for MD3 as far as I know
                
    if "_off" in object.name[:-2]:
        object.g2_prop_off = True
        object.g2_prop_tag = False
        
    elif object.name.startswith("*"):
        object.g2_prop_tag = True
        
    else:
        object.g2_prop_off = False
        object.g2_prop_tag = False

classes = [
    OBJECT_OT_ReplaceObject,
    OBJECT_OT_AllParent,
    OBJECT_OT_BodyParent,
    OBJECT_OT_CapParent,
    OBJECT_OT_TagParent,
    OBJECT_OT_UnparentAll,
    SetG2Properties,
    OBJECT_OT_CreateTags,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinFile,
    OBJECT_OT_SelectObjectType,
    OBJECT_OT_SetArmature,
    OBJECT_OT_RemoveEmptyVertexGroups,
    OBJECT_OT_CreateRoot,
    OBJECT_OT_OrigintoGeometry,
]

def register_operators():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
