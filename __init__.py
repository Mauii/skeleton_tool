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
import bmesh
from bpy.props import (IntProperty, StringProperty)
from jediacademy import *


# ADDON INFORMATION
bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (1, 2),
    "blender": (2, 91, 0),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has multiple functions which drastingly decreases time spent in parenting of objects, tags and creating a .skin file.",
    "category": "Rigging",
}


# BEGIN CLASSES
class OBJECT_PT_skeleton_tool(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Skeleton Tool"
    bl_idname = "OBJECT_PT_skeleton_tool"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        lods = context.scene.lods
        
        row = layout.row()
        row.label(text="Skeleton Tool", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Please use the readme if these buttons aren't making sense to you.")
        
        box = layout.box()
        box.operator("op.apply_all")
        box.operator("object.set_armature")
        
        box = layout.box()
        box.operator("object.create_tags")  
        box.operator("object.set_g2")
        box.operator("object.parent_objects")
        box.operator("object.parent_tags")
        
        lodspresent = -1
        
        for obj in bpy.data.objects:
            splitter = obj.name.split("_")
            
            if "model" not in obj.name.split("_")[0]:
                continue
            else:
                lodspresent += 1
            
        if context.scene.lods.lod_level > lodspresent:
            box.active = False
        
        box = layout.box()
        
        box.operator("op.add_one")
        box.operator("op.subtract_one")
        box.label(text='Amount of LODs: ' + str(context.scene.lods.lod_level))
        
        box = layout.box()
        
        box.prop(lods, "folder_path", text="Folder")
        box.operator("file.create_skin")
        

class OBJECT_OT_parent_objects(bpy.types.Operator):
    """Parent all objects"""
    bl_idname = "object.parent_objects"
    bl_label = "Parent Objects"

    def execute(self, context):
        
        ParentObjects(str(context.scene.lods.lod_level))
        
        return {'FINISHED'}
    
class OBJECT_OT_parent_tags(bpy.types.Operator):
    """Parent all tags"""
    bl_idname = "object.parent_tags"
    bl_label = "Parent Tags"

    def execute(self, context):
        
        ParentTags(str(context.scene.lods.lod_level))
        
        return {'FINISHED'}


class OBJECT_OT_create_tags(bpy.types.Operator):
    """Creates new Tags"""
    bl_idname = "object.create_tags"
    bl_label = "Create Tags"

    def execute(self, context):
        
        bpy.ops.outliner.orphans_purge()
        CreateTags(str(context.scene.lods.lod_level))
        SetUVMap()

        return {'FINISHED'}

    
class OBJECT_OT_create_skinfile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create Skin"

    def execute(self, context):
        CreateSkinFile(str(context.scene.lods.lod_level))

        return {'FINISHED'}
    
class OBJECT_OT_set_g2_values(bpy.types.Operator):
    """Set all object's g2 values"""
    bl_idname = "object.set_g2"
    bl_label = "Set G2 Values"

    def execute(self, context):
        SetG2Values(str(context.scene.lods.lod_level))

        return {'FINISHED'}
    
class OBJECT_OT_set_armature(bpy.types.Operator):
    """Add modifier Armature and assign skeleton_root"""
    bl_idname = "object.set_armature"
    bl_label = "Set Armature"

    def execute(self, context):
        exclude = ["scene_root", "skeleton_root", "model_root_0", "model_root_1", "model_root_2", "model_root_3"]
        
        for obj in bpy.data.objects:
            
            if obj.name in exclude:
                continue
            
            if not bpy.data.objects[obj.name].modifiers:
                bpy.data.objects[obj.name].modifiers.new("skin", 'ARMATURE') # Add armature
            
            bpy.data.objects[obj.name].modifiers['skin'].object = bpy.data.objects["skeleton_root"] # Assign skeleton_root
        else:
            print("Assigned modifier 'armature', 'skeleton_root'.")
            
        return {'FINISHED'}    


class OBJECT_OT_AddOne(bpy.types.Operator):
    """This adds 1 LOD level"""
    bl_idname = "op.add_one"
    bl_label = "LOD + 1"

    def execute(self, context): 
        if context.scene.lods.lod_level < 3:       
            context.scene.lods.lod_level += 1
        return {'FINISHED'}
    
    
class OBJECT_OT_SubtractOne(bpy.types.Operator):
    """This subtracts 1 LOD level"""
    bl_idname = "op.subtract_one"
    bl_label = "LOD - 1"

    def execute(self, context):   
        if context.scene.lods.lod_level > 0:
            context.scene.lods.lod_level -= 1
        return {'FINISHED'}
    

class OBJECT_OT_ApplyAll(bpy.types.Operator):
    """This applies all transforms to deltas"""
    bl_idname = "op.apply_all"
    bl_label = "Transform All"

    def execute(self, context):   
        TransformAll()
        return {'FINISHED'}    
    
        
class LODSetter(bpy.types.PropertyGroup):

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
def SetUVMap():        
    
    for obj in bpy.data.objects:
        
        if "*" not in obj.name:
            continue
        
        bpy.context.view_layer.objects.active = obj 
        bpy.ops.object.mode_set(mode='EDIT')  
        
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        # adjust uv coordinates
        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate
                loop_uv.uv = loop.vert.co.xy

        bmesh.update_edit_mesh(me)
        bpy.ops.object.mode_set(mode='OBJECT') 
        obj.select_set(False)
                

def SetG2Values(lod):
    
    exclude = (
        "scene_root", 
        "model_root_0", 
        "model_root_1", 
        "model_root_2", 
        "skeleton_root"
    )
        
    for obj in bpy.data.objects:
            
        if not "g2_prop_off" in obj:
            obj.g2_prop_off = False
        if not "g2_prop_tag" in obj:
            obj.g2_prop_tag = False
        if not "g2_prop_name" in obj:
            obj.g2_prop_name = ""
        if not "g2_prop_shader" in obj:
            obj.g2_prop_shader = ""
          
        if obj.name in exclude:
            continue  
          
        if not obj.name.endswith(lod):
            continue
        
        if "*" in obj.name:   
            obj.g2_prop_tag = True
   
        obj.g2_prop_name = obj.name.replace("_" + lod, "")


def TransformAll():
    for obj in bpy.data.objects:
        obj.select_set(True) 
        bpy.ops.object.transforms_to_deltas(mode='ALL')
        obj.select_set(False)
    

def ParentObjects(lod):

    parts = {
        "skeleton_root": "scene_root",
        "model_root" : "scene_root",
        "stupidtriangle_off" : "model_root_" + lod,
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
    
    global splitter
    # Go through each and every object found in the hierarchy list
    for obj in bpy.data.objects:

        bpy.ops.object.transforms_to_deltas(mode='ALL')

        splitter = obj.name.split("_")
        
        if "*" in obj.name or "scene_root" in obj.name:
            continue
        
        if "skeleton_root" in obj.name or "model" in splitter[0]:
            obj.parent = bpy.data.objects["scene_root"]
            continue  
        
        if lod not in splitter:
            continue
        
        if obj.name.startswith("l_") or obj.name.startswith("r_"):
            splitter = splitter[0] + "_" + splitter[1]
            obj.parent = bpy.data.objects[parts[splitter]]
            continue
        
        if "off" in splitter[1]:
            splitter = splitter[0] + "_" + splitter[1]
            obj.parent = bpy.data.objects[parts[splitter]]
            continue       
        
        if len(splitter) >= 3:
            print(str(splitter) + " | length: " + str(len(splitter)))
            if lod not in splitter[1]:
                print(str(splitter) + " | length: " + str(len(splitter)))
                obj.parent = bpy.data.objects[splitter[0] + "_" + lod]
                print(obj.name + " parent: " + obj.parent.name)
                continue
        
        obj.parent = bpy.data.objects[parts[splitter[0]]]

def ParentTags(lod):

    tagsparent = {
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

    for tag in bpy.data.objects:

        if "*" not in tag.name:
            continue
        
        if not tag.name.endswith(lod):
            continue
        
        tag.parent = bpy.data.objects[tagsparent[tag.name]]


def CreateTags(lod):

    tags = { # Every tagname 
        0: "*back_" + lod,
        1: "*chestg_" + lod,
        2: "*head_back_" + lod,
        3: "*head_cap_torso_" + lod,
        4: "*head_eyes_" + lod,
        5: "*head_front_" + lod,
        6: "*head_left_" + lod,
        7: "*head_right_" + lod,
        8: "*head_top_" + lod,
        9: "*hip_bl_" + lod,
        10: "*hip_br_" + lod,
        11: "*hip_fl_" + lod,
        12: "*hip_fr_" + lod,
        13: "*hip_l_" + lod,
        14: "*hip_r_" + lod,
        15: "*hips_cap_l_leg_" + lod,
        16: "*hips_cap_r_leg_" + lod,
        17: "*hips_cap_torso_" + lod,
        18: "*hips_l_knee_" + lod,
        19: "*hips_r_knee_" + lod,
        20: "*l_arm_cap_l_hand_" + lod,
        21: "*l_arm_cap_torso_" + lod,
        22: "*l_arm_elbow_" + lod,
        23: "*l_hand_" + lod,
        24: "*l_hand_cap_l_arm_" + lod,
        25: "*l_leg_calf_" + lod,
        26: "*l_leg_cap_hips_" + lod,
        27: "*l_leg_foot_" + lod,
        28: "*lchest_l_" + lod,
        29: "*lchest_r_" + lod,
        30: "*r_arm_cap_r_hand_" + lod,
        31: "*r_arm_cap_torso_" + lod,
        32: "*r_arm_elbow_" + lod,
        33: "*r_hand_" + lod,
        34: "*r_hand_cap_r_arm_" + lod,
        35: "*r_leg_calf_" + lod,
        36: "*r_leg_cap_hips_" + lod,
        37: "*r_leg_foot_" + lod,
        38: "*shldr_l_" + lod,
        39: "*shldr_r_" + lod,
        40: "*torso_cap_head_" + lod,
        41: "*torso_cap_hips_" + lod,
        42: "*torso_cap_l_arm_" + lod,
        43: "*torso_cap_r_arm_" + lod,
        44: "*uchest_l_" + lod,
        45: "*uchest_r_" + lod
    }
    
    groups = { # These are all the bones the tags are being parented to
        "*back_" + lod: "thoracic",
        "*chestg_" + lod: "upper_lumbar",
        "*head_back_" + lod: "cranium",
        "*head_cap_torso_" + lod: "cervical",
        "*head_eyes_" + lod: "cranium",
        "*head_front_" + lod: "cranium",
        "*head_left_" + lod: "cranium",
        "*head_right_" + lod: "cranium",
        "*head_top_" + lod: "cranium",
        "*hip_bl_" + lod: "lower_lumbar",
        "*hip_br_" + lod: "lower_lumbar",
        "*hip_fl_" + lod: "lower_lumbar",
        "*hip_fr_" + lod: "lower_lumbar",
        "*hip_l_" + lod: "lower_lumbar",
        "*hip_r_" + lod: "lower_lumbar",
        "*hips_cap_l_leg_" + lod: "ltibia",
        "*hips_cap_r_leg_" + lod: "rtibia",
        "*hips_cap_torso_" + lod: "lower_lumbar",
        "*hips_l_knee_" + lod: "ltibia",
        "*hips_r_knee_" + lod: "rtibia",
        "*l_arm_cap_l_hand_" + lod: "lradiusX",
        "*l_arm_cap_torso_" + lod: "lhumerusX",
        "*l_arm_elbow_" + lod: "lradius",
        "*l_hand_" + lod: "lhang_tag_bone",
        "*l_hand_cap_l_arm_" + lod: "lhand",
        "*l_leg_calf_" + lod: "ltibia",
        "*l_leg_cap_hips_" + lod: "ltibia",
        "*l_leg_foot_" + lod: "ltalus",
        "*lchest_l_" + lod: "upper_lumbar",
        "*lchest_r_" + lod: "upper_lumbar",
        "*r_arm_cap_r_hand_" + lod: "rradiusX",
        "*r_arm_cap_torso_" + lod: "rhumerusX",
        "*r_arm_elbow_" + lod: "rradius",
        "*r_hand_" + lod: "rhang_tag_bone",
        "*r_hand_cap_r_arm_" + lod: "rhand",
        "*r_leg_calf_" + lod: "rtibia",
        "*r_leg_cap_hips_" + lod: "rtibia",
        "*r_leg_foot_" + lod: "rtalus",
        "*shldr_l_" + lod: "lclavical",
        "*shldr_r_" + lod: "rclavical",
        "*torso_cap_head_" + lod: "cervical",
        "*torso_cap_hips_" + lod: "lower_lumbar",
        "*torso_cap_l_arm_" + lod: "lhumerusX",
        "*torso_cap_r_arm_" + lod: "rhumerusX",
        "*uchest_l_" + lod: "thoracic",
        "*uchest_r_" + lod: "thoracic",
    }

    verts = [ # Every tag verts
        [(-0.0569, 0.4202, 5.1881),(0.0041, 0.4202, 5.1881),(0.0041, 0.2861, 5.1881)],
        [(0.0651, -0.0254, 5.0317),(0.0041, -0.0254, 5.0317),(0.0041, 0.1087, 5.0317)],
        [(-0.0569, 0.4184, 6.3305),(0.0041, 0.4184, 6.3305),(0.0041, 0.2843, 6.3305)],
        [(-0.0569, 0.0310, 5.8167),(0.0041, 0.0310, 5.8167),(0.0041, 0.0008, 5.9474)],
        [(0.0651, -0.3286, 6.3079),(0.0041, -0.3286, 6.3079),(0.0041, -0.1944, 6.3079)],
        [(0.0651, -0.4217, 6.0056),(0.0041, -0.4217, 6.0056),(0.0041, -0.2875, 6.0056)],
        [(0.3107, 0.0177, 6.3193),(0.3107, -0.0433, 6.3193),(0.1765, -0.0433, 6.3193)],
        [(-0.2774, -0.1043, 6.3193),(-0.2774, -0.0433, 6.3193),(-0.1432, -0.0433, 6.3193)],
        [(0.0651, -0.0943, 6.6378),(0.0041, -0.0943, 6.6378),(0.0041, 0.0399, 6.6378)],
        [(0.3253, 0.3359, 4.2369),(0.3781, 0.3054, 4.2369),(0.3110, 0.1892, 4.2369)],
        [(-0.4227, 0.2749, 4.2369),(-0.3699, 0.3054, 4.2369),(-0.3028, 0.1892, 4.2369)],
        [(0.3842, -0.3229, 4.1777),(0.3299, -0.3506, 4.1777),(0.2690, -0.2311, 4.1777)],
        [(-0.2674, -0.3783, 4.1777),(-0.3217, -0.3506, 4.1777),(-0.2608, -0.2311, 4.1777)],
        [(0.4977, -0.0253, 4.1846),(0.4871, -0.0853, 4.1846),(0.3563, -0.0623, 4.1659)],
        [(-0.4849, -0.1460, 4.1573),(-0.4954, -0.0860, 4.1573),(-0.3646, -0.0629, 4.1386)],
        [(0.8993, 0.1805, 1.6666),(0.8432, 0.1805, 1.6428),(0.7908, 0.1805, 1.7663)],
        [(-0.7789, 0.1805, 1.6190),(-0.8350, 0.1805, 1.6428),(-0.7826, 0.1805, 1.7663)],
        [(0.0605, 0.0214, 4.1647),(-0.0005, 0.0214, 4.1647),(-0.0005, 0.0354, 4.0313)],
        [(0.7807, -0.0067, 2.1210),(0.7218, -0.0067, 2.1052),(0.7218, 0.1274, 2.1052)],
        [(-0.6549, -0.0068, 2.0895),(-0.7138, -0.0068, 2.1053),(-0.7138, 0.1274, 2.1053)],
        [(1.8660, 0.1020, 4.0128),(1.8659, 0.0410, 4.0133),(1.7701, 0.0419, 4.1072)],
        [(0.7759, 0.0168, 5.1949),(0.7756, 0.0778, 5.1951),(0.8704, 0.0785, 5.1002)],
        [(1.2802, 0.1889, 4.6768),(1.3229, 0.1892, 4.6333),(1.3235, 0.0551, 4.6329)],
        [(2.0674, -0.0028, 3.8461),(2.0117, -0.0102, 3.8343),(1.9579, 0.0060, 3.8952)],
        [(1.8941, -0.0408, 3.9921),(1.8942, 0.0202, 3.9918),(1.9900, 0.0193, 3.9449)],
        [(1.0028, 0.2746, 1.9321),(1.0186, 0.2157, 1.9321),(0.8934, 0.1821, 1.9009)],
        [(0.7747, 0.1839, 1.8482),(0.8300, 0.1839, 1.8714),(0.8866, 0.1839, 1.7620)],
        [(1.2792, -0.0651, 0.7125),(1.2213, -0.0699, 0.6959),(1.1805, -0.0704, 0.8109)],
        [(0.3201, -0.3678, 4.7277),(0.2630, -0.3887, 4.7328),(0.2178, -0.2627, 4.7418)],
        [(-0.1978, -0.4403, 4.7379),(-0.2549, -0.4195, 4.7328),(-0.2096, -0.2935, 4.7418)],
        [(-1.8582, -0.0211, 4.0136),(-1.8582, 0.0398, 4.0136),(-1.7633, 0.0398, 4.1084)],
        [(-0.7680, 0.1400, 5.1951),(-0.7680, 0.0790, 5.1951),(-0.8629, 0.0790, 5.1003)],
        [(-1.3696, 0.1870, 4.5908),(-1.3264, 0.1870, 4.6339),(-1.3264, 0.0529, 4.6339)],
        [(-1.9478, -0.0177, 3.6719),(-2.0035, -0.0102, 3.6956),(-1.9497, 0.0060, 3.8174)],
        [(-1.8941, -0.0408, 3.9921),(-1.8942, 0.0202, 3.9918),(-1.9900, 0.0193, 3.9449)],
        [(-1.0183, 0.1568, 1.9321),(-1.0026, 0.2157, 1.9321),(-0.8774, 0.1821, 1.9008)],
        [(-0.8775, 0.1839, 1.8937),(-0.8218, 0.1839, 1.8714),(-0.8763, 0.1839, 1.7611)],
        [(-1.1623, -0.0719, 0.6831),(-1.2206, -0.0675, 0.6989),(-1.1818, -0.0675, 0.8145)],
        [(0.6433, -0.1271, 5.4083),(0.5845, -0.1300, 5.4240),(0.5541, -0.0422, 5.3273)],
        [(-0.5555, -0.1342, 5.4398),(-0.6144, -0.1315, 5.4240),(-0.5843, -0.0435, 5.3273)],
        [(0.0651, 0.0364, 5.7931),(0.0041, 0.0364, 5.7931),(0.0041, 0.0666, 5.6624)],
        [(-0.0569, -0.0030, 4.2077),(0.0041, -0.0030, 4.2077),(0.0041, -0.0170, 4.3411)],
        [(0.7738, 0.1338, 5.1968),(0.7741, 0.0729, 5.1966),(0.6793, 0.0721, 5.2915)],
        [(-0.7665, 0.0132, 5.1966),(-0.7665, 0.0741, 5.1966),(-0.6717, 0.0741, 5.2915)],
        [(0.3757, -0.3544, 5.1514),(0.3168, -0.3648, 5.1633),(0.2879, -0.2377, 5.1314)],
        [(-0.2497, -0.3752, 5.1751),(-0.3086, -0.3648, 5.1633),(-0.2798, -0.2377, 5.1314)]
    ]

    edges = [] # Edges will be made automaticly, but had to define it
    faces = [] # Same as edges, only this one will be used down below  
    faces.append([0, 1, 2]) # Make sure faces will be made with 3 verts (triangles)    
    
    for number in range(45): # 45 tags
        
        mesh = bpy.data.meshes.new(tags[number])
        obj = bpy.data.objects.new(tags[number], mesh)
        mesh.from_pydata(verts[number], edges, faces) # Create Tag
        
        bpy.context.scene.collection.objects.link(obj) # Make the Tag visible
        
        obj.vertex_groups.new(name=groups[obj.name]) # Adds a vertex group
        obj.vertex_groups.active.add([0, 1, 2], 1.0, 'ADD') # Assign weight
         
        print("Tag " + obj.name + " created.")   
        
        
def CreateSkinFile(lod):
    file = open(bpy.context.scene.lods.folder_path + "\model_default.skin", "w")
    
    bpy.context.scene.lods.folder_path
    
    exclude = (
        "scene_root", 
        "model_root_0", 
        "model_root_1", 
        "model_root_2", 
        "stupidtriangle_off_0",
        "stupidtriangle_off_1",
        "stupidtriangle_off_2",
        "skeleton_root"
    )
    
    caps = ""
    
    for obj in bpy.data.objects:
            
        if not obj.name.endswith(lod):
            continue
        
        if "*" in obj.name:
            continue   
        
        if obj.name in exclude:
            continue
        
        if not obj.active_material:
            file.write(obj.g2_prop_name + ",*off\n")
            continue
                
        if "cap" in obj.name.split("_"):
            caps = obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n"
            continue
                
        file.write(obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n")    

    file.write("\n" + caps)
    file.close()


# New way to register and unregister classes
def register(): 
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.lods = bpy.props.PointerProperty(type=LODSetter)
   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.lods

    # Current classes
classes = [
    OBJECT_PT_skeleton_tool,
    OBJECT_OT_create_tags,
    OBJECT_OT_parent_objects,
    OBJECT_OT_parent_tags,
    OBJECT_OT_create_skinfile,
    OBJECT_OT_set_g2_values,
    OBJECT_OT_set_armature,
    OBJECT_OT_AddOne,
    OBJECT_OT_SubtractOne,
    OBJECT_OT_ApplyAll,
    LODSetter
]

# Not entirely sure what this means.. yet but it's mandatory
if __name__ == "__main__":
    register()
