import bpy
import jediacademy
import math

bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (2, 4),
    "blender": (4, 1),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has many features that decreases timewastes when preparing a model for JKA.",
    "category": "Modelling / Rigging",
}

class OBJECT_PT_SkeletonTool(bpy.types.Panel):
    """ Creates a Panel in the Object properties window """
    bl_label = "Skeleton Tool"
    bl_idname = "OBJECT_PT_Skeleton_Tool"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.settings
        obj = context.object
               
        box = layout.box() 
        box.label(text="Parent Playermodel")
        
        row = box.row()
        row.operator("body.parent") 
        row.operator("cap.parent") 
        row.operator("tag.parent")
        
        box = layout.box()        
        box.prop(settings, "folder_path")
        
        row = box.row()
        row.operator("g2.propset")
        row.operator("file.create_skin")
        
        box = layout.box() 
        box.label(text="Vehicles")
        box.operator("vehicle.parent")
        
        box = layout.box() 
        box.label(text="Dissolve settings for LODs")
        box.prop(settings, "angle_limit")
        box.prop(settings, "delimit_item", expand=True)
        box.prop(settings, "boundaries")
        box.operator("lod.create") 
              
        box = layout.box()
        box.label(text="Misc") 
        box.operator("remove.parent")
        box.operator("hierarchy.clean")

class AddonProperties(bpy.types.PropertyGroup):
        
    folder_path: bpy.props.StringProperty(
        name = "Save to",
        default = "select folder to save file",
        description = "Model folder",
        maxlen = 1024,
        subtype = "FILE_PATH",
    )
    
    angle_limit: bpy.props.FloatProperty(
        name = "Angle limit:",
    )
    
    delimit_item: bpy.props.EnumProperty(
        name = "Dissolve as",
        description = "sample text",
        items = [
            ('NORMAL', "Normal", "Dissolve on normal"),
            ('MATERIAL', "Material", "Dissolve on material"),
            ('SEAM', "Seam", "Dissolve on seam"),
            ('SHARP', "Sharp", "Dissolve on sharp"),
            ('UV', "UV", "Dissolve on uv")
        ]
    )
    
    boundaries: bpy.props.EnumProperty(
        name = "Boundaries",
        description = "sample text",
        items = [
            ('True', "True", "use_dissolve_boundaries = True"),
            ('False', "Frue", "use_dissolve_boundaries = False"),
        ]
    )

################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """ Parent all body parts if naming convention is respected """
    bl_idname = "body.parent"
    bl_label = "Body"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:       
            
            if "_cap_" in object.name or object.g2_prop_tag or "scene_root" in object.name:
                continue
            
            object.parent = bpy.data.objects[OBJECT_OT_BodyParent.parent(object)]
        
        return {'FINISHED'}
       
    def parent(object):              
  
        parts = {
            "l_leg": "hips",
            "r_leg": "hips",
            "torso": "hips",
            "l_arm": "torso",
            "r_arm": "torso",
            "l_hand": "l_arm",
            "r_hand": "r_arm",
            "head": "torso",
            "hips": ""
        }
      
        if "skeleton_root" in object.name or "model_root" in object.name:
            return "scene_root"
        
        if "stupidtriangle" in object.name or "stupidtriangle_off" in object.name:
            return f"model_root_{getLOD(object)}"
        
        if bpy.data.objects.get(f"stupidtriangle_{getLOD(object)}"):
            parts["hips"] = "stupidtriangle"
        else:
            parts["hips"] = "stupidtriangle_off"
        
        if len(object.name.split("_")) == 2:
            if stripLOD(object) in parts:
                return f"{parts.get(stripLOD(object))}_{getLOD(object)}"
            else:
                return f"model_root_{getLOD(object)}" 
        
        if object.name.startswith("l_") or object.name.startswith("r_"):
            return parts.get("_".join(object.name.split("_", 2)[:2])) + "_" + getLOD(object)
        else:
            return object.name.split("_")[0] + "_" + getLOD(object)

################################################################################################
##                                                                                            ##
##                                  SET CAP PARENTING                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_CapParent(bpy.types.Operator):
    """ Parent all caps """
    bl_idname = "cap.parent"
    bl_label = "Caps"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:
            
            if object.g2_prop_tag or "_cap_" not in object.name or "scene_root" in object.name:
                continue
            
            object.parent = bpy.data.objects[OBJECT_OT_CapParent.parent(object)]                
            
        return {'FINISHED'}
    
    
    def parent(object):    

        return "_cap_".join(object.name.split("_cap_", 1)[:1]) + "_" + getLOD(object)  

################################################################################################
##                                                                                            ##
##                                  SET TAG PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_TagParent(bpy.types.Operator):
    """ Parent all tags """
    bl_idname = "tag.parent"
    bl_label = "Tags"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
            
        for object in bpy.data.objects:  
        
            if object.g2_prop_tag == False:
                continue
            
            object.parent = bpy.data.objects[OBJECT_OT_TagParent.parent(object)]
        
        return {'FINISHED'} 
    
    def parent(object):
    
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
        
        newObject = stripLOD(object)
        
        if newObject in tags:
            return tags.get(newObject) + "_" + getLOD(object)
    
################################################################################################
##                                                                                            ##
##                              SET VEHICLE PARENTING                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_VehicleParent(bpy.types.Operator):
    """ Parent objects, caps and tags from the vehicle """
    bl_idname = "vehicle.parent"
    bl_label = "Parent Parts"

    def execute(self, context):
        
        if "pelvis" in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No vehiclemodel loaded!")
            
            return {'FINISHED'}
        
        for object in bpy.data.objects:     
            if "scene" in object.name:
                continue
            
            object.parent = bpy.data.objects[parentVehicle(object) + "_" + getLOD(object)]
        
        return {'FINISHED'} 
    
    def parentVehicle(object):  
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
        
        for object in bpy.data.objects:
            object.parent = None 
        
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
    
class OBJECT_OT_CreateSkinfile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create .SKIN"
    
    def execute(self, context): 
        
        OBJECT_OT_CreateSkinFile.create() 
    
        return {'FINISHED'}
    
    def create():
        file = open(bpy.context.scene.settings.folder_path + "\model_default.skin", "w")
        
        exclude = (
            "scene_root", 
            "model_root_0",
            "model_root_1",
            "model_root_2",
            "model_root_3",
            "stupidtriangle_off_0",
            "stupidtriangle_off_1",
            "stupidtriangle_off_2",
            "stupidtriangle_off_3",
            "stupidtriangle_0",
            "stupidtriangle_1",
            "stupidtriangle_2",
            "stupidtriangle_3",
            "skeleton_root"
        )
        
        caps = ""
        
        for object in bpy.data.objects:
                    
            if object.g2_prop_tag or object.name in exclude or object == None:
                continue   
                    
            if object.g2_prop_off and "_cap_" in object.name:
                
                if "Material" in object.active_material.name.split("."):
                    caps = caps + object.g2_prop_name + ",*off\n"
                    continue
                
                caps = caps + object.g2_prop_name + "," + object.active_material.name.split(".tga")[0] + ".tga\n"
                continue
            
            if "Material" in object.active_material.name:
                file.write(object.g2_prop_name + ",*off\n")
                continue
                    
            file.write(object.g2_prop_name + "," + object.active_material.name.split(".tga")[0] + ".tga\n")  

        file.write("\n")
        file.write(caps)
        file.close()

################################################################################################
##                                                                                            ##
##                            CREATE NEW MODEL_ROOT HIERARCHIES                               ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_CreateLODs(bpy.types.Operator):
    """Create 3 extra LOD levels"""
    bl_idname = "lod.create"
    bl_label = "Create LODs"
    
    def execute(self, context): 
        for lod in (1,2,3):
            verts = OBJECT_OT_CreateLODs.autoLOD(lod, bpy.context.scene.settings.angle_limit, bpy.context.scene.settings.delimit_item)   
            self.report({'INFO'}, f"Created model_root_{getLOD(bpy.context.selected_objects[0])} with {verts} vertices.")
    
        return {'FINISHED'}       

    def autoLOD(lod, maxLimit, mode="UV"):
            
        bpy.ops.object.select_all(action='DESELECT') # We deselect everything
        
        for object in bpy.context.scene.objects:
            if "skeleton_root" in object.name or "scene_root" in object.name:
                continue
            
            if object.name.endswith("_0"):
                object.select_set(True)
                
        bpy.ops.object.duplicate() # We make a duplicate
        
        for obj in bpy.context.selected_objects:
            
            obj.name = obj.name.replace("0.001", str(lod)) # We rename selected objects. Actually we are always working with LOD 0
            
            if obj.g2_prop_tag or "stupidtriangle" in obj.name or "skeleton_root" in obj.name or "scene_root" in obj.name or "model_root" in obj.name:
                obj.select_set(False) # We unselect what we do not want to be dissolved  
        
        if bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
        else: 
            bpy.context.view_layer.objects.active = None
               
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT') # Select every vertex in the mesh           
        bpy.ops.mesh.remove_doubles() # We optimize removing doubles
      
        radians = math.radians(maxLimit)
        angle = 0.0
        match lod:
            case 3:
                angle = radians
            case 2:
                angle = radians/2
            case 1:
                angle = radians/5
        
        bpy.ops.mesh.tris_convert_to_quads()             
        bpy.ops.mesh.dissolve_limited(angle_limit=angle, use_dissolve_boundaries=boundaries, delimit={mode})
        bpy.ops.mesh.quads_convert_to_tris() # We apply our dissolve formula
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        verts = 0
        
        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH':
                continue
            
            verts += len(obj.data.vertices)
            
        return verts

################################################################################################
##                                                                                            ##
##                              SET GHOUL2 PROPERTIES                                         ##
##                                                                                            ##
################################################################################################
    
class OBJECT_OT_SetGhoul2Properties(bpy.types.Operator):
    """Sets all ghoul2 properties"""
    bl_idname = "g2.propset"
    bl_label = "Set G2Props"

    def execute(self, context): 
        
        for object in bpy.data.objects:       
            if object.type != "MESH":
                continue
                
            OBJECT_OT_SetGhoul2Properties.setProperties(object)
    
        return {'FINISHED'}
      
    def setProperties(object):    
                
        if "g2_prop_off" not in object:
            object.g2_prop_off = False
            
        if "g2_prop_tag" not in object:
            object.g2_prop_tag = False
            
        if "g2_prop_name" not in object:
            object.g2_prop_name = object.name.replace("_" + getLOD(object), "")
            
        if "g2_prop_shader" not in object:
            object.g2_prop_shader = ""

################################################################################################
##                                                                                            ##
##                                      LOD FUNCTIONS                                         ##
##                                                                                            ##
################################################################################################    

def getLOD(object):
    
    lod = object.name.split("_")[-1]
          
    if lod.isnumeric():
        return str(lod)
    
def stripLOD(object):
    
    return object.name.replace("_" + getLOD(object), "")


# New way to register and unregister classes
def register(): 
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=AddonProperties)   
   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.settings

classes = [
    AddonProperties,
    OBJECT_PT_SkeletonTool,
    OBJECT_OT_BodyParent,
    OBJECT_OT_CapParent,
    OBJECT_OT_TagParent,
    OBJECT_OT_SetGhoul2Properties,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinfile,
    OBJECT_OT_VehicleParent,    
    OBJECT_OT_UnparentAll,
    OBJECT_OT_CreateLODs
]

if __name__ == "__main__":
    register()
