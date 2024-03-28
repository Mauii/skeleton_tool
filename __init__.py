import bpy
from bpy.props import (IntProperty, StringProperty)
from jediacademy import *

bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (2),
    "blender": (4, 0, 2),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has multiple functions which drastingly decreases time spent in parenting of objects, caps, tags and creating a .skin file.",
    "category": "Rigging",
}

class OBJECT_PT_SkeletonTool(bpy.types.Panel):
    """ Creates a Panel in the Object properties window """
    bl_label = "Skeleton Tool"
    bl_idname = "OBJECT_PT_skeleton_tool"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        settings = context.scene.settings
               
        box = layout.box() 
        box.label(text="Player Characters")
        box.operator("body.parent") 
        box.operator("cap.parent") 
        box.operator("tag.parent") 
        
        box = layout.box()        
        box.prop(settings, "folder_path", text="Save to")
        box.operator("g2.propset")
        box.operator("file.create_skin")
        
        box = layout.box()
        box.label(text="Vehicles")
        box.operator("vehicle.parent")
              
        box = layout.box()
        box.label(text="Misc")
        box.operator("remove.parent")
        box.operator("hierarchy.clean")
        

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """ Parent all body parts if naming convention is respected """
    bl_idname = "body.parent"
    bl_label = "Parent Body Parts"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "You're trying to use a function for Character Models!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:       
            
            if "_cap_" in object.name or object.g2_prop_tag or "scene_root" in object.name:
                continue
            
            if getBodyParent(object, lastIndex(object)) == False:
                self.report({'ERROR'}, stripLOD(object) + " was not in the partlist, parenting to torso_" + lastIndex(object))
                object.parent = bpy.data.objects["torso_" + lastIndex(object)]
                continue
            
            object.parent = bpy.data.objects[getBodyParent(object, lastIndex(object))]
        
        return {'FINISHED'}
    
class OBJECT_OT_CapParent(bpy.types.Operator):
    """ Parent all caps """
    bl_idname = "cap.parent"
    bl_label = "Parent Caps"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "You're trying to use a function for Character Models!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:
            
            if object.g2_prop_tag or "_cap_" not in object.name or "scene_root" in object.name:
                continue
            
            object.parent = bpy.data.objects[getCapParent(object, lastIndex(object))]
                 
            
        return {'FINISHED'}    

class OBJECT_OT_TagParent(bpy.types.Operator):
    """ Parent all tags """
    bl_idname = "tag.parent"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "You're trying to use a function for Character Models!")
        
            return {'FINISHED'}
            
        for object in bpy.data.objects:  
        
            if object.g2_prop_tag == False or object.g2_prop_off or "scene_root" in object.name:
                continue
            
            object.parent = bpy.data.objects[getTagParent(object, lastIndex(object))]
        
        return {'FINISHED'}  
    
class OBJECT_OT_VehicleParent(bpy.types.Operator):
    """ Parent objects, caps and tags corcerning vehicles """
    bl_idname = "vehicle.parent"
    bl_label = "Parent Vehicle Parts"

    def execute(self, context):
        
        if "pelvis" in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "You're trying to use a function for Vehicles!")
            
            return {'FINISHED'}
        
        for object in bpy.data.objects:     
            if "scene_root" in object.name:
                continue
            
            object.parent = bpy.data.objects[setVehicleObjectParent(object, lastIndex(object))]
        
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
        
        for object in bpy.data.objects:         
            if ".00" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=False, confirm=True)
        
        return {'FINISHED'}

    
class OBJECT_OT_CreateSkinfile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create model_default.skin"
    
    def execute(self, context): 
        
        createSkinFile() 
    
        return {'FINISHED'}
    
class OBJECT_OT_SetGhoul2Properties(bpy.types.Operator):
    """Sets all ghoul2 properties"""
    bl_idname = "g2.propset"
    bl_label = "Set Ghoul 2 Properties"

    def execute(self, context): 
        
        for object in bpy.data.objects:       
            if "model" in object.name or "scene" in object.name or "skeleton" in object.name:
                continue
                
            setGhoul2Properties(object, lastIndex(object))
    
        return {'FINISHED'}
    
class AddonProperties(bpy.types.PropertyGroup):
        
    folder_path: StringProperty(
        name="Save to:",
        default="",
        description="Model folder",
        maxlen=1024,
        subtype="FILE_PATH",
    )
    
    
           
def unparentAll():
    """ Loop through all objects and remove the parent. """
    for object in bpy.data.objects:
        object.parent = None

def getVehicleObjectParent(object):  
    """ Goes through the dictionary and return the key value if found, else return body. """
       
    dictionary = {
        "body": "model_root",
        "l_wing1": "body",
        "l_wing2": "l_wing1",
        "r_wing1": "body",
        "r_wing2": "r_wing1"
        }
    
    if object in dictionary:
        return dictionary.get(object)

    return "body"   


def setVehicleObjectParent(object, lod):       
	      
    if "skeleton" in object.name or "model" in object.name:
        return "scene_root"
    
    return getVehicleObjectParent(stripLOD(newObject)) + "_" + lod  


def stripLOD(object):
    
    newObject = object.name.split("_")
    
    # left, right, hand or arm, return as needed
    if object.name.startswith("l_") or object.name.startswith("r_"):
        if "hand" in newObject[1]:  # if it's hand or arm, return as such
            return newObject[0] + "_" + newObject[1]  # return l_hand or l_arm for example
        else:
            return newObject[1]
    else:
        return newObject[0]
      
      
def setGhoul2Properties(object, lod):
    
    g2Name = object.name.replace("_" + lod, "")    
            
    if "g2_prop_off" not in object:
        object.g2_prop_off = False
        
    if "g2_prop_tag" not in object:
        object.g2_prop_tag = False
        
    if "g2_prop_name" not in object:
        object.g2_prop_name = g2Name
        
    if "g2_prop_shader" not in object:
        object.g2_prop_shader = ""
    

def lastIndex(object):
    
    newObject = object.name.split("_")
    
    for index in newObject:      
        if index.isnumeric():
            return str(index)    
   
def getTagParent(object, lod):
    
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
    
    newObject = object.name.replace("_" + lod, "")
    
    if newObject in tags:
        return tags.get(newObject) + "_" + lod
    else:
        return "torso_" + lod
   
def getCapParent(object, lod):
    
    newObject = "_cap_".join(object.name.split("_cap_", 1)[:1])    

    return newObject + "_" + lod
        
def getBodyParent(object, lod):              
  
    parts = {
        "leg": "hips_",
        "torso": "hips_",
        "arm": "torso_",
        "l_hand": "l_arm_",
        "r_hand": "r_arm_",
        "head": "torso_",
    }
  
    if "skeleton_root" in object.name or "model_root" in object.name:
        return "scene_root"
    
    if "stupidtriangle" in object.name or "stupidtriangle_off" in object.name:
        return "model_root_" + lod
    
    if object.name.startswith("hips"):
        if object.name.split("_")[1].isnumeric():
            if bpy.data.objects.find("stupidtriangle_" + lod) != -1:
                return "stupidtriangle_" + lod
            elif bpy.data.objects.find("stupidtriangle_off_" + lod) != -1:
                return "stupidtriangle_off_" + lod
        else:
            return "hips_" + lod
    
    newObject = stripLOD(object)
    
    if object.name.startswith("torso"):
        if object.name.split("_")[1].isnumeric():
            return parts.get(newObject) + lod
        else:
            return "torso_" + lod
    
    if object.name.startswith("head"):
        if object.name.split("_")[1].isnumeric():
            return parts.get(newObject) + lod
        else:
            return "head_" + lod
    
    if newObject in parts:
        return parts.get(newObject) + lod
    else:
        return False

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
    OBJECT_OT_SetGhoul2Properties,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinfile,
    OBJECT_OT_VehicleParent,    
    OBJECT_OT_UnparentAll,
    AddonProperties
]

if __name__ == "__main__":
    register()
