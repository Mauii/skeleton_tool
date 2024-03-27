import bpy
from bpy.props import (IntProperty, StringProperty)
from jediacademy import *
from mathutils.bvhtree import BVHTree


# ADDON INFORMATION
bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (2),
    "blender": (4, 0, 2),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has multiple functions which drastingly decreases time spent in parenting of objects, caps, tags and creating a .skin file.",
    "category": "Rigging",
}


# BEGIN CLASSES
class OBJECT_PT_SkeletonTool(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Skeleton Tool"
    bl_idname = "OBJECT_PT_skeleton_tool"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        settings = context.scene.settings
        
        row = layout.row()
        row.label(text="Player Characters")
        
        box = layout.box() 
        box.operator("body.parent") 
        box.operator("cap.parent") 
        box.operator("tag.parent") 
        box.operator("hierarchy.clean")
        
        box = layout.box()        
        box.prop(settings, "folder_path", text="Folder")
        box.operator("file.create_skin")
        
        row = layout.row()
        row.label(text="Vehicles")
        
        box = layout.box()
        box.operator("vehicle.parent")
        
        row = layout.row()
        row.label(text="Misc")
        
        box = layout.box()
        box.operator("remove.parent")
        

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """Parent all objects and tags"""
    bl_idname = "body.parent"
    bl_label = "Parent Body Parts"

    def execute(self, context):
        
        parts = {
            "stupidtriangle": "model_root",
            "hips": "stupidtriangle",
            "l_leg": "hips",
            "r_leg": "hips",
            "torso": "hips",
            "l_arm": "torso",
            "r_arm": "torso",
            "l_hand": "l_arm",
            "r_hand": "r_arm",
            "head": "torso",
        }  
        
        for obj in bpy.data.objects:

            lod = lastIndex(obj)        
            
            if "stupidtriangle_off" in obj.name:
                parts["stupidtriangle_off"] = "model_root"
            
            if "_cap_" in obj.name or "*" in obj.name or "scene_root" in obj.name or obj == None:
                continue
            
            if getBodyParent(obj, lod, parts) == None:
                continue
            
            obj.parent = bpy.data.objects[getBodyParent(obj, lod, parts)]
        
        return {'FINISHED'}
    
class OBJECT_OT_CapParent(bpy.types.Operator):
    """Parent all caps"""
    bl_idname = "cap.parent"
    bl_label = "Parent Caps"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            lod = lastIndex(obj) 
            
            if "*" in obj.name or "_cap_" not in obj.name or obj == None:
                continue
                
            obj.parent = bpy.data.objects[getCapParent(obj, lod)]
                 
            
        return {'FINISHED'}    

class OBJECT_OT_TagParent(bpy.types.Operator):
    """Parent all tags"""
    bl_idname = "tag.parent"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            lod = lastIndex(obj)  
        
            if "*" not in obj.name or obj == None:
                continue
            
            obj.parent = bpy.data.objects[getTagParent(obj, lod)]
        
        return {'FINISHED'}  
    
class OBJECT_OT_VehicleParent(bpy.types.Operator):
    """Parent all Vehicle parts"""
    bl_idname = "vehicle.parent"
    bl_label = "Parent Vehicle Parts"

    def execute(self, context):
        
        setVehicleObjectParent()
        
        return {'FINISHED'} 
    
class OBJECT_OT_UnparentAll(bpy.types.Operator):
    """Removes all parents from objects"""
    bl_idname = "remove.parent"
    bl_label = "Remove Parents"

    def execute(self, context):
        
        unparentAll()
        
        return {'FINISHED'} 
    
class OBJECT_OT_Clean(bpy.types.Operator):
    """Delete duplicate in hierarchy"""
    bl_idname = "hierarchy.clean"
    bl_label = "Clean duplicates in hierarchy"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            if ".00" in obj.name:
                obj.select_set(True)
                bpy.ops.object.delete(use_global=False, confirm=True)
        
        return {'FINISHED'}

    
class OBJECT_OT_CreateSkinfile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create Skin"


    def execute(self, context): 
        
        setGhoul2Name()
        createSkinFile() 
    
        return {'FINISHED'}
    
class AddonProperties(bpy.types.PropertyGroup):
        
    folder_path: StringProperty(
        name="Folder",
        default="",
        description="Model folder",
        maxlen=1024,
        subtype="FILE_PATH",
    )
    
# END CLASSES

   
# ALL FUNCTIONS BELOW           
  
def unparentAll():
    for obj in bpy.data.objects:
        obj.parent = None

def getVehicleObjectParent(object, list):
    
    dictionary = {
        "body": "model_root",
        "l_wing1": "body",
        "l_wing2": "l_wing1",
        "r_wing1": "body",
        "r_wing2": "r_wing1"
        }
    
    if len(list) > 2:
        list = list[0] + "_" + list[1]
    else:
        list = list[0] 
    
    if list in dictionary:
        return dictionary.get(list)

    return "body"   

def setVehicleObjectParent():       
    for object in bpy.data.objects:
            
        # scene_root is the grand parent, no need to assign a parent to this
        if "scene_root" in object.name or object == None:
            continue
           
        # Split object.name in segments: l_wing1_0 makes a list l, wing1, 0
        splitter = object.name.split("_")
        
        # Find LOD level in splitter and assign value to lod
        for index in splitter:
            if index.isnumeric():
                lod = index
        
        if "skeleton_root" in object.name or "model_root" in object.name:
            object.parent = bpy.data.objects["scene_root"]
            continue 

        object.parent = bpy.data.objects[getVehicleObjectParent(object, splitter) + "_" + lod]  
              
# description: This goes through every object, gives them an armature and check whether they are a tag or an object and set Ghoul2 properties accordingly.
def setGhoul2Name():
    
    exclude = (
        "scene", 
        "model",
        "skeleton"
    )
        
    for obj in bpy.data.objects:
        
        if obj == None:
            continue
        
        lod = lastIndex(obj)
            
        if "g2_prop_off" not in obj:
            obj.g2_prop_off = False
        if "g2_prop_tag" not in obj:
            obj.g2_prop_tag = False
        if "g2_prop_name" not in obj:
            obj.g2_prop_name = ""
        if "g2_prop_shader" not in obj:
            obj.g2_prop_shader = ""
    
        if obj.name.split("_")[0] in exclude or "*" in obj.name:
            continue
   
        obj.g2_prop_name = obj.name.replace("_" + lod, "")

# Description: split the obj.name, iterate and see if it's a number, return if so.
#              this will be used everywhere in the addon.
def lastIndex(obj):
    
    object = obj.name.split("_")
    
    for index in object:
        if index.isnumeric():
            return str(index)    

# Description: This one speaks for itself, it checks if * is in the name,
#              navigate in the dictionary and parent accordingly.    
def getTagParent(obj, lod):
    
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
    
    newObject = obj.name.replace("_" + lod, "")
    
    if "*" in obj.name:
        if newObject in tags:
            return tags.get(newObject) + "_" + lod
        else:
            return "torso" + "_" + lod

# Description: This function takes an object and lod level as argument,
#              these will be splitted and checked in a dictionary.    
def getCapParent(obj, lod):
    
    caps = {
        "l_leg": "l_leg",
        "r_leg": "r_leg",
        "l_arm": "l_arm",
        "r_arm": "r_arm",
        "l_hand": "l_hand",
        "r_hand": "r_hand",
        "head": "head",
        "torso": "torso",
        "hips": "hips"
    }
    
    newObject = "_cap_".join(obj.name.split("_cap_", 1)[:1])    
            
    if newObject in caps:    
        return caps.get(newObject) + "_" + lod
    else:
        print("WARNING: Cap " + obj.name + " has not been found. You sure you're using the right function?")
        
# Description: Goes through every given object, split and see if it's in the dictionary.
#              I added torso_l and torso_r since default jka models might have them,
#              just in case someone uses this in their frankenstein model.
def getBodyParent(obj, lod, parts):              
  
    if "skeleton_root" in obj.name or "model_root" in obj.name:
        return "scene_root"
    
    if obj.name.count("_") > 1:
        newObject = "_".join(obj.name.split("_", 2)[:2]) # left or right
    else:
        newObject = obj.name.replace("_" + lod, "") # Single object   
        
    if newObject in parts:    
        return parts.get(newObject) + "_" + lod
    elif obj.name.split("_")[0] in parts:  
        newObject = obj.name.split("_")[0]
        return newObject + "_" + lod

# description: After you've selected a path I will create model_default.skin for you.   
def createSkinFile():
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
    
    for obj in bpy.data.objects:
                
        if "*" in obj.name or "0" not in obj.name or obj.name in exclude:
            continue   
                
        if obj.g2_prop_off and "_cap_" in obj.name:
            
            if "Material" in obj.active_material.name.split("."):
                caps = caps + obj.g2_prop_name + ",*off\n"
                continue
            
            caps = caps + obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n"
            continue
        
        if "Material" in obj.active_material.name:
            file.write(obj.g2_prop_name + ",*off\n")
            continue
                
        file.write(obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n")  

    file.write("\n")
    file.write(caps)
    file.close()


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
    OBJECT_PT_SkeletonTool,
    OBJECT_OT_BodyParent,
    OBJECT_OT_CapParent,
    OBJECT_OT_TagParent,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinfile,
    OBJECT_OT_VehicleParent,
    OBJECT_OT_UnparentAll,
    AddonProperties
]


if __name__ == "__main__":
    register()
