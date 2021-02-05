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

        row = layout.row()
        row.label(text="Please use the readme if these buttons aren't making sense to you.")
        
        box = layout.box()
        box.operator("object.create_tags")
        box.operator("object.fix_tag_size")  
        box.operator("object.parent_lod_level")
        
        box = layout.box()
        
        box.operator("object.add_one")
        box.operator("object.subtract_one")
        box.label(text='Current LOD level: ' + str(context.scene.settings.lod_level))
        
        box = layout.box()
        
        box.prop(settings, "folder_path", text="Folder")
        box.operator("file.create_skin")
        

class OBJECT_OT_ParentLODLevel(bpy.types.Operator):
    """Parent all objects"""
    bl_idname = "object.parent_lod_level"
    bl_label = "Parent Objects/Tag"

    def execute(self, context):
        
        ParentObjects(str(context.scene.settings.lod_level))
        ParentTags(str(context.scene.settings.lod_level)) 
        SetAllGhoul2Properties(str(context.scene.settings.lod_level)) 
        SetArmature      
        
        return {'FINISHED'}


class OBJECT_OT_CreateTags(bpy.types.Operator):
    """Creates new Tags"""
    bl_idname = "object.create_tags"
    bl_label = "Create Tags"

    def execute(self, context):
        
        bpy.ops.outliner.orphans_purge()
        CreateTags(str(context.scene.settings.lod_level))

        return {'FINISHED'}

    
class OBJECT_OT_CreateSkinfile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create Skin"

    def execute(self, context):
        
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
    

class OBJECT_OT_TransformAll(bpy.types.Operator):
    """This applies all transforms to deltas"""
    bl_idname = "object.transform_all"
    bl_label = "Transform All"

    def execute(self, context):   
        TransformAll()
        return {'FINISHED'}
    
    
class OBJECT_OT_FixTagSize(bpy.types.Operator):
    """This increases the Tag size to 10"""
    bl_idname = "object.fix_tag_size"
    bl_label = "Set Tag Size 10"

    def execute(self, context):   
        FixTagSize(str(context.scene.settings.lod_level))
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

# description: Every object needs to have an armature to be able to move, that's what I do.
def SetArmature():
    exclude = ["scene", "skeleton", "model"]
    
    for obj in bpy.data.objects:
        
        if obj.name.split("_")[0] in exclude:
            continue
        
        if bpy.data.objects[obj.name].modifiers:
            continue
        
        if bpy.data.objects[obj.name].modifiers['skin'].object:
            continue
        
        bpy.data.objects[obj.name].modifiers.new("skin", 'ARMATURE') # Add armature        
        bpy.data.objects[obj.name].modifiers['skin'].object = bpy.data.objects["skeleton_root"] # Assign skeleton_root
        
    else:
        
        print("Assigned modifier 'armature', 'skeleton_root'.")

# description: Every object needs weights, vertex groups obviously and uv mapping set. This includes tags, and that's where I'm for.            
def SetUVMap(obj):        
    
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
                
                
# description: This goes through every object and check whether they are a tag or an object and set Ghoul2 properties accordingly.
def SetAllGhoul2Properties(lod):
    
    exclude = (
        "scene_root", 
        "model_root_" + lod,
        "skeleton_root"
    )
        
    for obj in bpy.data.objects:
            
        if "g2_prop_off" not in obj:
            obj.g2_prop_off = False
        if "g2_prop_tag" not in obj:
            obj.g2_prop_tag = False
        if "g2_prop_name" not in obj:
            obj.g2_prop_name = ""
        if "g2_prop_shader" not in obj:
            obj.g2_prop_shader = ""
          
        if obj.name in exclude:
            continue  
        
        if not obj.name.endswith(lod):
            continue
        
        if "*" in obj.name:   
            obj.g2_prop_tag = True
   
        obj.g2_prop_name = obj.name.replace("_" + lod, "")
    
    
# description: Goes through every object and check what kind of part it is and parent accordingly.
def ParentObjects(lod):

    parts = {
        "stupidtriangle_off_" + lod: "model_root_" + lod,
        "hips_" + lod: "stupidtriangle_off_" + lod,
        "l_leg_" + lod: "hips_" + lod,
        "r_leg_" + lod: "hips_" + lod,
        "torso_" + lod: "hips_" + lod,
        "l_arm_" + lod: "torso_" + lod,
        "r_arm_" + lod: "torso_" + lod,
        "l_hand_" + lod: "l_arm_" + lod,
        "r_hand_" + lod: "r_arm_" + lod,
        "head_" + lod: "torso_" + lod
    }
    
    global splitter
    # Go through each and every object found in the hierarchy list
    for obj in bpy.data.objects:
       
        splitter = obj.name.split("_") # Split name into an array of strings
        
        if "scene_root" in obj.name:
            continue
        
        if "skeleton" in splitter[0] or "model" in splitter[0]:
            obj.parent = bpy.data.objects["scene_root"]
            continue
        
        if lod not in splitter:
            continue
                      
        if "*" in obj.name:
            continue
        
        if obj.name.startswith("l_") or obj.name.startswith("r_") or "off" in splitter[1]:
            splitter = splitter[0] + "_" + splitter[1] + "_" + lod  
            try: # This is a debug print to see if the object's parent is present or not
                obj.parent = bpy.data.objects[parts[splitter]]       
            except:
                print("Parent {} is not found, check names of your objects!".format(parts[splitter]))
            continue
        
        splitter = splitter[0] + "_" + lod
        
        if splitter not in parts: # If naming convention is not followed, I will try to find which object I'm colliding with
            for obj2 in bpy.data.objects:# Get the objects remaining objects
                
                if obj2 == obj or obj2.name.split("_")[0] in obj.name:
                    continue
                
                if "*" in obj2:
                    continue
                
                if lod not in obj2.name:
                    continue
                
                if obj2.name.split("_")[0] in ["skeleton", "model", "scene"]:
                    continue
                
                # Found the code underneath at: https://blender.stackexchange.com/questions/149891/python-in-blender-2-8-testing-if-two-objects-overlap-in-the-xy-plane/150014
                # Adjusted a little bit so it would fit this addon
                
                # Get their world matrix
                mat1 = obj.matrix_world
                mat2 = obj2.matrix_world

                # Get the geometry in world coordinates
                vert1 = [mat1 @ v.co for v in obj.data.vertices] 
                poly1 = [p.vertices for p in obj.data.polygons]

                vert2 = [mat2 @ v.co for v in obj2.data.vertices] 
                poly2 = [p.vertices for p in obj2.data.polygons]

                # Create the BVH trees
                bvh1 = BVHTree.FromPolygons(vert1, poly1)
                bvh2 = BVHTree.FromPolygons(vert2, poly2)

                # Test if overlap
                if bvh1.overlap(bvh2):
                    print("{} and {} overlap".format(obj.name, obj2.name))
                    break
         
            obj.parent = bpy.data.objects[obj2.name]
            continue
        try: # This is a debug print to see if the object's parent is present or not
            obj.parent = bpy.data.objects[parts[splitter]]       
        except:
            print("Parent {} is not found, check names of your objects!".format(parts[splitter]))

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
    
    for obj in bpy.data.objects:
    
        if lod not in obj.name:
            continue
                      
        if "*" in obj.name:
            obj.parent = bpy.data.objects[tagsparent[obj.name]]


# description: This function checks if the to-be-made tag is already existing, if not then create it.
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

    edges = []
    faces = [[0, 1, 2]] 
    
    for number in range(46): # 46 tags
        
        print("To be made: ", tags[number])
        
        if tags[number] not in bpy.data.objects:
        
            mesh = bpy.data.meshes.new(tags[number])
            obj = bpy.data.objects.new(tags[number], mesh)
            mesh.from_pydata(verts[number], edges, faces) # Create Tag
            
            bpy.context.scene.collection.objects.link(obj) # Make the Tag visible
            
            obj.vertex_groups.new(name=groups[obj.name]) # Adds a vertex group
            obj.vertex_groups.active.add([0, 1, 2], 1.0, 'ADD') # Assign weight
            
            print(obj.name + " created.")  
            
            SetUVMap(obj) 
            
            
def FixTagSize(lod):
    for obj in bpy.data.objects:
        if "*" not in obj.name:
            continue
        
        if lod not in obj.name:
            continue
        
        print(obj.name, " being increased.")
        
        obj.scale[0] = 10
        obj.scale[1] = 10
        obj.scale[2] = 10
        
        bpy.ops.object.transforms_to_deltas(mode='ALL')
        

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
        "skeleton_root"
    )
    
    caps = ""
    
    for obj in bpy.data.objects:
        
        if "*" in obj.name or "0" not in obj.name:
            continue   
        
        if obj.name in exclude:
            continue
        
        if not obj.active_material:
            file.write(obj.g2_prop_name + ",*off\n")
            continue
                
        if obj.g2_prop_off:
            caps = caps + obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n"
            continue
                
        file.write(obj.g2_prop_name + "," + obj.active_material.name.split(".tga")[0] + ".tga\n")    

    file.write("\n" + caps)
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
    OBJECT_OT_CreateTags,
    OBJECT_OT_FixTagSize,
    OBJECT_OT_ParentLODLevel,
    OBJECT_OT_CreateSkinfile,
    OBJECT_OT_AddOne,
    OBJECT_OT_SubtractOne,
    AddonProperties
]


if __name__ == "__main__":
    register()