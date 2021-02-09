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
    "version": (1, 3),
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
        box.operator("object.parent") 
        box.operator("object.clean")
        
        box = layout.box()        
        box.prop(settings, "folder_path", text="Folder")
        box.operator("file.create_skin")
        

class OBJECT_OT_Parent(bpy.types.Operator):
    """Parent all objects"""
    bl_idname = "object.parent"
    bl_label = "Parent Objects/Tags"

    def execute(self, context):
        
        for obj in bpy.data.objects:
            
            lod = LastIndex(obj)
            
            if "scene_root" in obj.name:
                continue
          
            if "skeleton_root" in obj.name or "model_root_" + lod in obj.name:
                obj.parent = bpy.data.objects["scene_root"]
                continue
            
            obj.parent = GetParent(obj)
        
        return {'FINISHED'}
    
    
class OBJECT_OT_Clean(bpy.types.Operator):
    """Clean up copies"""
    bl_idname = "object.clean"
    bl_label = "Clean Hierarchy"

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


class OBJECT_OT_AddOne(bpy.types.Operator):
    """This adds 1 LOD level"""
    bl_idname = "object.add_one"
    bl_label = "LOD +1"

    def execute(self, context): 
        if context.scene.settings.lod_level < 3:       
            context.scene.settings.lod_level += 1
        return {'FINISHED'}
    
    
class OBJECT_OT_SubtractOne(bpy.types.Operator):
    """This subtracts 1 LOD level"""
    bl_idname = "object.subtract_one"
    bl_label = "LOD -1"

    def execute(self, context):   
        if context.scene.settings.lod_level > 0:
            context.scene.settings.lod_level -= 1
        return {'FINISHED'}       
    
        
class AddonProperties(bpy.types.PropertyGroup):

    lod_level: IntProperty(
        name="Setter for LOD",
        description="This number determines which LOD to use.",
        default = 0
        )
        
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
   
        obj.g2_prop_name = obj.name.replace("_" + lod, "")


def LastIndex(modelpart):
    
    modelpart = modelpart.name.split("_")
    
    for index in modelpart:
        if index.isnumeric():
            return index    

    
def GetParent(obj):

    lod = LastIndex(obj)   

    parts = {
        "hips": "stupidtriangle_off_" + lod,
        "l_leg": "hips_" + lod,
        "r_leg": "hips_" + lod,
        "torso": "hips_" + lod,
        "l_arm": "torso_" + lod,
        "r_arm": "torso_" + lod,
        "l_hand": "l_arm_" + lod,
        "r_hand": "r_arm_" + lod,
        "head": "torso_" + lod
    } 
    
    caps = {
        "hips": "hips_" + lod,
        "l_leg": "l_leg_" + lod,
        "r_leg": "r_leg_" + lod,
        "torso": "torso_" + lod,
        "l_arm": "l_arm_" + lod,
        "r_arm": "r_arm_" + lod,
        "l_hand": "l_hand_" + lod,
        "r_hand": "r_hand_" + lod,
        "head": "head_" + lod
    }
    
    tags = {
        "*back_" + lod: "torso_" + lod,
        "*chestg_" + lod: "torso_" + lod,
        "*head_back_" + lod: "head_" + lod,
        "*head_cap_torso_" + lod: "head_" + lod,
        "*head_eyes_" + lod: "head_" + lod,
        "*head_front_" + lod: "head_" + lod,
        "*head_left_" + lod: "head_" + lod,
        "*head_right_" + lod: "head_" + lod,
        "*head_top_" + lod: "head_" + lod,
        "*hip_bl_" + lod: "hips_" + lod,
        "*hip_br_" + lod: "hips_" + lod,
        "*hip_fl_" + lod: "hips_" + lod,
        "*hip_fr_" + lod: "hips_" + lod,
        "*hip_l_" + lod: "hips_" + lod,
        "*hip_r_" + lod: "hips_" + lod,
        "*hips_cap_l_leg_" + lod: "hips_" + lod,
        "*hips_cap_r_leg_" + lod: "hips_" + lod,
        "*hips_cap_torso_" + lod: "hips_" + lod,
        "*hips_l_knee_" + lod: "hips_" + lod,
        "*hips_r_knee_" + lod: "hips_" + lod,
        "*l_arm_cap_l_hand_" + lod: "l_arm_" + lod,
        "*l_arm_cap_torso_" + lod: "l_arm_" + lod,
        "*l_arm_elbow_" + lod: "l_arm_" + lod,
        "*l_hand_" + lod: "l_hand_" + lod,
        "*l_hand_cap_l_arm_" + lod: "l_hand_" + lod,
        "*l_leg_calf_" + lod: "l_leg_" + lod,
        "*l_leg_cap_hips_" + lod: "l_leg_" + lod,
        "*l_leg_foot_" + lod: "l_leg_" + lod,
        "*lchest_l_" + lod: "torso_" + lod,
        "*lchest_r_" + lod: "torso_" + lod,
        "*r_arm_cap_r_hand_" + lod: "r_arm_" + lod,
        "*r_arm_cap_torso_" + lod: "r_arm_" + lod,
        "*r_arm_elbow_" + lod: "r_arm_" + lod,
        "*r_hand_" + lod: "r_hand_" + lod,
        "*r_hand_cap_r_arm_" + lod: "r_hand_" + lod,
        "*r_leg_calf_" + lod: "r_leg_" + lod,
        "*r_leg_cap_hips_" + lod: "r_leg_" + lod,
        "*r_leg_foot_" + lod: "r_leg_" + lod,
        "*shldr_l_" + lod: "torso_" + lod,
        "*shldr_r_" + lod: "torso_" + lod,
        "*torso_cap_head_" + lod: "torso_" + lod,
        "*torso_cap_hips_" + lod: "torso_" + lod,
        "*torso_cap_l_arm_" + lod: "torso_" + lod,
        "*torso_cap_r_arm_" + lod: "torso_" + lod,
        "*uchest_l_" + lod: "torso_" + lod,
        "*uchest_r_" + lod: "torso_" + lod
    }
                      
    if "*" in obj.name:
        return bpy.data.objects[tags[obj.name]]        
  
    splitter = obj.name.split("_") # Split name into an array of strings 
  
    if obj.name.startswith("l_") or obj.name.startswith("r_"):
         
        if "cap" in splitter:
            splitter = splitter[0] + "_" + splitter[1]
            return bpy.data.objects[caps[splitter]]
        
        splitter = splitter[0] + "_" + splitter[1]
        return bpy.data.objects[parts[splitter]]
  
    if "stupidtriangle" in obj.name or "stupidtriangle_off" in obj.name:
        return bpy.data.objects["model_root_" + lod]        
    
    if "stupidtriangle_off" not in bpy.data.objects and "hips" in splitter:
        return bpy.data.objects["stupidtriangle_" + lod]
          
    print(splitter)
    print(obj.name)
    
    return bpy.data.objects[parts[splitter[0]]]

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
            caps = caps + obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n"
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
    OBJECT_OT_Parent,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinfile,
    OBJECT_OT_AddOne,
    OBJECT_OT_SubtractOne,
    AddonProperties
]


if __name__ == "__main__":
    register()
