# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
import bpy
from bpy.props import (IntProperty, StringProperty)
from jediacademy import *
from mathutils.bvhtree import BVHTree


# ADDON INFORMATION
bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (1, 4),
    "blender": (2, 91, 0),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has multiple functions which drastingly decreases time spent in parenting of objects, tags and creating a .skin file.",
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
        row.label(text="Skeleton Tool", icon='WORLD_DATA')
        
        box = layout.box() 
        box.operator("body.parent") 
        box.operator("cap.parent") 
        box.operator("tag.parent") 
        box.operator("object.clean")
        
        box = layout.box()        
        box.prop(settings, "folder_path", text="Folder")
        box.operator("file.create_skin")
        

class OBJECT_OT_BodyParent(bpy.types.Operator):
    """Parent all objects and tags"""
    bl_idname = "body.parent"
    bl_label = "Parent Body Parts"

    def execute(self, context):
        
        for obj in bpy.data.objects:

            lod = LastIndex(obj)        
            
            if "_cap_" in obj.name or "*" in obj.name or "scene_root" in obj.name:
                continue
            
            if GetBodyParent(obj, lod) == None:
                continue
            
            obj.parent = GetBodyParent(obj, lod)
        
        return {'FINISHED'}
    
class OBJECT_OT_CapParent(bpy.types.Operator):
    """Parent all caps"""
    bl_idname = "cap.parent"
    bl_label = "Parent Caps"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            lod = LastIndex(obj) 
            
            if "_cap_" not in obj.name:
                continue
                
            obj.parent = GetCapParent(obj, lod)
                 
            
        return {'FINISHED'}    

class OBJECT_OT_TagParent(bpy.types.Operator):
    """Parent all tags"""
    bl_idname = "tag.parent"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            lod = LastIndex(obj)  
        
            if "*" not in obj.name:
                continue
            
            obj.parent = GetTagParent(obj, lod)
        
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
        
        SetGhoul2Name()
        CreateSkinFile()

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
                
# description: This goes through every object, gives them an armature and check whether they are a tag or an object and set Ghoul2 properties accordingly.
def SetGhoul2Name():
    
    exclude = (
        "scene", 
        "model",
        "skeleton"
    )
        
    for obj in bpy.data.objects:
        
        lod = LastIndex(obj)
            
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
   
        obj.g2_prop_name = obj.name.replace("_" + str(lod), "")


def LastIndex(obj):
    
    object = obj.name.split("_")
    
    for index in object:
        if index.isnumeric():
            return index    
    
def GetTagParent(obj, lod):
    
    tags = {
        "*back_" + str(lod): "torso_" + str(lod),
        "*chestg_" + str(lod): "torso_" + str(lod),
        "*head_back_" + str(lod): "head_" + str(lod),
        "*head_cap_torso_" + str(lod): "head_" + str(lod),
        "*head_eyes_" + str(lod): "head_" + str(lod),
        "*head_front_" + str(lod): "head_" + str(lod),
        "*head_left_" + str(lod): "head_" + str(lod),
        "*head_right_" + str(lod): "head_" + str(lod),
        "*head_top_" + str(lod): "head_" + str(lod),
        "*hip_bl_" + str(lod): "hips_" + str(lod),
        "*hip_br_" + str(lod): "hips_" + str(lod),
        "*hip_fl_" + str(lod): "hips_" + str(lod),
        "*hip_fr_" + str(lod): "hips_" + str(lod),
        "*hip_l_" + str(lod): "hips_" + str(lod),
        "*hip_r_" + str(lod): "hips_" + str(lod),
        "*hips_cap_l_leg_" + str(lod): "hips_" + str(lod),
        "*hips_cap_r_leg_" + str(lod): "hips_" + str(lod),
        "*hips_cap_torso_" + str(lod): "hips_" + str(lod),
        "*hips_l_knee_" + str(lod): "hips_" + str(lod),
        "*hips_r_knee_" + str(lod): "hips_" + str(lod),
        "*l_arm_cap_l_hand_" + str(lod): "l_arm_" + str(lod),
        "*l_arm_cap_torso_" + str(lod): "l_arm_" + str(lod),
        "*l_arm_elbow_" + str(lod): "l_arm_" + str(lod),
        "*l_hand_" + str(lod): "l_hand_" + str(lod),
        "*l_hand_cap_l_arm_" + str(lod): "l_hand_" + str(lod),
        "*l_leg_calf_" + str(lod): "l_leg_" + str(lod),
        "*l_leg_cap_hips_" + str(lod): "l_leg_" + str(lod),
        "*l_leg_foot_" + str(lod): "l_leg_" + str(lod),
        "*lchest_l_" + str(lod): "torso_" + str(lod),
        "*lchest_r_" + str(lod): "torso_" + str(lod),
        "*r_arm_cap_r_hand_" + str(lod): "r_arm_" + str(lod),
        "*r_arm_cap_torso_" + str(lod): "r_arm_" + str(lod),
        "*r_arm_elbow_" + str(lod): "r_arm_" + str(lod),
        "*r_hand_" + str(lod): "r_hand_" + str(lod),
        "*r_hand_cap_r_arm_" + str(lod): "r_hand_" + str(lod),
        "*r_leg_calf_" + str(lod): "r_leg_" + str(lod),
        "*r_leg_cap_hips_" + str(lod): "r_leg_" + str(lod),
        "*r_leg_foot_" + str(lod): "r_leg_" + str(lod),
        "*shldr_l_" + str(lod): "torso_" + str(lod),
        "*shldr_r_" + str(lod): "torso_" + str(lod),
        "*torso_cap_head_" + str(lod): "torso_" + str(lod),
        "*torso_cap_hips_" + str(lod): "torso_" + str(lod),
        "*torso_cap_l_arm_" + str(lod): "torso_" + str(lod),
        "*torso_cap_r_arm_" + str(lod): "torso_" + str(lod),
        "*uchest_l_" + str(lod): "torso_" + str(lod),
        "*uchest_r_" + str(lod): "torso_" + str(lod)
    }
    
    if "*" in obj.name:
        return bpy.data.objects[tags[obj.name]]
    
def GetCapParent(obj, lod):
    
    caps = {
        "l_leg": "l_leg_" + str(lod),
        "r_leg": "r_leg_" + str(lod),
        "l_arm": "l_arm_" + str(lod),
        "r_arm": "r_arm_" + str(lod),
        "l_hand": "l_hand_" + str(lod),
        "r_hand": "r_hand_" + str(lod),
        "head": "head_" + str(lod),
        "torso": "torso_" + str(lod),
        "hips": "hips_" + str(lod)
    }
    
    splitter = obj.name.split("_")
        
    if obj.name.startswith("l_") or obj.name.startswith("r_"): # Determine: left or right

        splitter = splitter[0] + "_" + splitter[1]
        return bpy.data.objects[caps[splitter]]
    
    return bpy.data.objects[caps[splitter[0]]]  
    
def GetBodyParent(obj, lod):           

    parts = {
        "stupidtriangle_off": "model_root_" + str(lod),
        "hips": "stupidtriangle_off_" + str(lod),
        "l_leg": "hips_" + str(lod),
        "r_leg": "hips_" + str(lod),
        "torso": "hips_" + str(lod),
        "l_arm": "torso_" + str(lod),
        "r_arm": "torso_" + str(lod),
        "l_hand": "l_arm_" + str(lod),
        "r_hand": "r_arm_" + str(lod),
        "head": "torso_" + str(lod)
    } 
    
    splitter = obj.name.split("_")     
  
    if "skeleton_root" in obj.name or "model_root" in obj.name:
        return bpy.data.objects["scene_root"]
    
    if splitter[0] in parts:
        return bpy.data.objects[parts.get(splitter[0])]
    
    if splitter[0] + "_" + splitter[1] in parts: # Determine: object arm or leg     
        return bpy.data.objects[parts.get(splitter[0] + "_" + splitter[1])]
    
    else:  
        print("WARNING: Wrong naming convention used on object: " + obj.name)

# description: After you've selected a path I will create model_default.skin for you.   
def CreateSkinFile():
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
                
        if obj.g2_prop_off and "cap" in obj.name:
            
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
    AddonProperties
]


if __name__ == "__main__":
    register()
