import bpy
import jediacademy # This can get very fancy names, so it would be interesting to make a "try" on wonko functions


bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (3, 1), # Updating directly to 3.0 with our new great features and a video!
    "blender": (4, 2),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has many features that decreases timewastes when preparing a model for JKA.",
    "category": "Modelling / Rigging",
}


class OBJECT_PT_SkeletonTool(bpy.types.Panel):
    """ Creates a Panel in the Object properties window """
    bl_label = "Jedi Academy: Skeleton tool"
    bl_idname = "OBJECT_PT_Skeleton_Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Skeleton tool"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context): 
        ''' Sized box which can encompass all the buttons, could be more adjusted.
        Keep parent buttons as different in the Playermodel tag; set create LODs within the function
        and send create tags to misc and disabled cause it's not working'''
        layout = self.layout
        
        layout.ui_units_x = 14.0 
        layout.ui_units_y = 14.0
        
        settings = context.scene.settings
        obj = context.object
               
        box = layout.box() 
        box.label(text="Playermodel")
        
        box.operator("body.parent") 
        box.operator("cap.parent") 
        box.operator("tag.parent")
        box.operator("tag.create")
        
        box = layout.box()                
        row = box.row()
        row.operator("g2.propset")
        row.operator("file.create_skin")
        
        box = layout.box() 
        box.label(text="Vehicles")
        box.operator("vehicle.parent")
        
        box = layout.box()
        box.label(text="Misc") 
        box.operator("remove.parent")
        box.operator("hierarchy.clean")
        
        box = layout.box()
        box.label(text="Select") 
        box.operator("g2.select")
        box.prop(settings, "meshes")
        box.prop(settings, "caps")
        box.prop(settings, "tags")
        

class AddonProperties(bpy.types.PropertyGroup): 
    meshes : bpy.props.BoolProperty(name="Meshes",default=False)
    caps : bpy.props.BoolProperty(name="Caps",default=False)
    tags : bpy.props.BoolProperty(name="Tags",default=False)
    

def showMessage(message = "defaultMessage", title = "defaultTitle", icon = 'INFO'):
    differentLines = message.split("\n")
    def draw(self, context):
        for line in differentLines:
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

################################################################################################
##                                                                                            ##
##                                        TAGS FUNCTIONS                                      ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateTags(bpy.types.Operator):
    """ Creates tags for model_root_0 """
    bl_idname = "tag.create"
    bl_label = "Create Tags"

    def execute(self, context):
        
        self.create()
        
        return {'FINISHED'}

    def create(self):
        tags = { # Every tagname 
            0: "*back_0",
            1: "*chestg_0",
            2: "*head_back_0",
            3: "*head_cap_torso_0",
            4: "*head_eyes_0",
            5: "*head_front_0",
            6: "*head_left_0",
            7: "*head_right_0",
            8: "*head_top_0",
            9: "*hip_bl_0",
            10: "*hip_br_0",
            11: "*hip_fl_0",
            12: "*hip_fr_0",
            13: "*hip_l_0",
            14: "*hip_r_0",
            15: "*hips_cap_l_leg_0",
            16: "*hips_cap_r_leg_0",
            17: "*hips_cap_torso_0",
            18: "*hips_l_knee_0",
            19: "*hips_r_knee_0",
            20: "*l_arm_cap_l_hand_0",
            21: "*l_arm_cap_torso_0",
            22: "*l_arm_elbow_0",
            23: "*l_hand_0",
            24: "*l_hand_cap_l_arm_0",
            25: "*l_leg_calf_0",
            26: "*l_leg_cap_hips_0",
            27: "*l_leg_foot_0",
            28: "*lchest_l_0",
            29: "*lchest_r_0",
            30: "*r_arm_cap_r_hand_0",
            31: "*r_arm_cap_torso_0",
            32: "*r_arm_elbow_0",
            33: "*r_hand_0",
            34: "*r_hand_cap_r_arm_0",
            35: "*r_leg_calf_0",
            36: "*r_leg_cap_hips_0",
            37: "*r_leg_foot_0",
            38: "*shldr_l_0",
            39: "*shldr_r_0",
            40: "*torso_cap_head_0",
            41: "*torso_cap_hips_0",
            42: "*torso_cap_l_arm_0",
            43: "*torso_cap_r_arm_0",
            44: "*uchest_l_0",
            45: "*uchest_r_0"
        }
        
        groups = { # These are all the bones the tags are being parented to
            "*back_0": "thoracic",
            "*chestg_0": "upper_lumbar",
            "*head_back_0": "cranium",
            "*head_cap_torso_0": "cervical",
            "*head_eyes_0": "cranium",
            "*head_front_0": "cranium",
            "*head_left_0": "cranium",
            "*head_right_0": "cranium",
            "*head_top_0": "cranium",
            "*hip_bl_0": "lower_lumbar",
            "*hip_br_0": "lower_lumbar",
            "*hip_fl_0": "lower_lumbar",
            "*hip_fr_0": "lower_lumbar",
            "*hip_l_0": "lower_lumbar",
            "*hip_r_0": "lower_lumbar",
            "*hips_cap_l_leg_0": "ltibia",
            "*hips_cap_r_leg_0": "rtibia",
            "*hips_cap_torso_0": "lower_lumbar",
            "*hips_l_knee_0": "ltibia",
            "*hips_r_knee_0": "rtibia",
            "*l_arm_cap_l_hand_0": "lradiusX",
            "*l_arm_cap_torso_0": "lhumerusX",
            "*l_arm_elbow_0": "lradius",
            "*l_hand_0": "lhang_tag_bone",
            "*l_hand_cap_l_arm_0": "lhand",
            "*l_leg_calf_0": "ltibia",
            "*l_leg_cap_hips_0": "ltibia",
            "*l_leg_foot_0": "ltalus",
            "*lchest_l_0": "upper_lumbar",
            "*lchest_r_0": "upper_lumbar",
            "*r_arm_cap_r_hand_0": "rradiusX",
            "*r_arm_cap_torso_0": "rhumerusX",
            "*r_arm_elbow_0": "rradius",
            "*r_hand_0": "rhang_tag_bone",
            "*r_hand_cap_r_arm_0": "rhand",
            "*r_leg_calf_0": "rtibia",
            "*r_leg_cap_hips_0": "rtibia",
            "*r_leg_foot_0": "rtalus",
            "*shldr_l_0": "lclavical",
            "*shldr_r_0": "rclavical",
            "*torso_cap_head_0": "cervical",
            "*torso_cap_hips_0": "lower_lumbar",
            "*torso_cap_l_arm_0": "lhumerusX",
            "*torso_cap_r_arm_0": "rhumerusX",
            "*uchest_l_0": "thoracic",
            "*uchest_r_0": "thoracic",
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
        
        for number in range(46): # 45 tags
            
            if tags[number] not in bpy.data.objects:
                
                mesh = bpy.data.meshes.new(tags[number])
                obj = bpy.data.objects.new(tags[number], mesh)
                mesh.from_pydata(verts[number], edges, faces) # Create Tag
                
                bpy.context.scene.collection.objects.link(obj) # Make the Tag visible
                
                obj.modifiers.new(name="Armature", type='ARMATURE')
                obj.modifiers["Armature"].object = bpy.data.objects["skeleton_root"]
                
                obj.vertex_groups.new(name=groups[obj.name]) # Adds a vertex group
                obj.vertex_groups.active.add([0, 1, 2], 1.0, 'ADD') # Assign weight
                obj.g2_prop_tag = True # Set g2_prop_tag to True
                print(obj.name + " created.")

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
            
            if "_cap_" in object.name or object.g2_prop_tag or "scene_root" in object.name:
                continue
            
            matrixcopy = object.matrix_world.copy() 
            
            object.parent = bpy.data.objects[self.parent(object)]
            object.matrix_world = matrixcopy
        
        return {'FINISHED'}
   
    def parent(self, object):              
  
        parts = {
            "l_leg": "hips",
            "r_leg": "hips",
            "torso": "hips",
            "l_arm": "torso",
            "r_arm": "torso",
            "l_hand": "l_arm",
            "r_hand": "r_arm",
            "head": "torso",
            "hips": "model_root",
        }
        
        # Parent model_root_LOD and skeleton_root to scene_root
        if "model_root" in object.name or "skeleton_root" in object.name:
            return "scene_root"
        
        strippedObj = stripLOD(object)    
        
        for item in parts.keys():
            print(item)
            
            if strippedObj == item:
                return f"{parts.get(strippedObj)}_{getLOD(object)}"
            elif item in strippedObj:
                return f"{item}_{getLOD(object)}"
            
        return f"hips_{getLOD(object)}"
  

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
        
        # Check if pelvis is in the skeleton_root, if not then it's not a humanoid skeleton
        # Throw an error if so
        if "pelvis" not in bpy.data.armatures["skeleton_root"].bones:
            self.report({'ERROR'}, "No playermodel loaded!")
        
            return {'FINISHED'}
        
        for object in bpy.data.objects:
            
            if "_cap_" not in object.name or object.g2_prop_tag or object.type == "EMPTY":
                continue
                
            matrixcopy = object.matrix_world.copy() 
            
            object.parent = bpy.data.objects[self.parent(object)]    
            object.matrix_world = matrixcopy # Same problem was found in caps         
            
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
        
        for object in bpy.data.objects:
            matrixcopy = object.matrix_world.copy()
            object.parent = None 
            object.matrix_world = matrixcopy # We do the same when un-parenting

        
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
    
class OBJECT_OT_CreateSkinFile(bpy.types.Operator):
    """Create model_default.skin file"""
    bl_idname = "file.create_skin"
    bl_label = "Create .SKIN"
    
    folder_path: bpy.props.StringProperty(
        name = "Save to",
        default = "",
        description = "Select a path where to save the .skin file",
        maxlen = 1024,
        subtype = "DIR_PATH"
    )
    
    shadername: bpy.props.StringProperty(name="Enter model name", default = "")
    
    def execute(self, context): 
        
        path = bpy.path.abspath(self.folder_path)
        shadername = self.shadername
        file = open(path + f"\{shadername}.skin", "w")
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
        fiveLines = ""
        index = 0
        
        for object in bpy.data.objects:
            
            if object.type == "EMPTY" or object.active_material is None:
                continue
            
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
            
            if "/" in object.active_material.name:
                lastItem = object.active_material.name.split("/")[-1]
            else:
                lastItem = object.active_material.name
            
            if "." not in lastItem:
                lastItem = lastItem + ".tga"
                
            stringtowrite = object.g2_prop_name + "," + "models/players/" + shadername + "/" + lastItem + "\n"
            
            if index < 6:
                fiveLines = fiveLines + stringtowrite
                index += 1
            
            file.write(stringtowrite)  

        file.write("\n")
        file.write(caps)
        file.close()
        fiveLines = fiveLines + f"Written in path {path}"
        showMessage(fiveLines, "model_default.skin created, showing first 5 lines", "INFO")
        
        return {'FINISHED'}
    
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)


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
                
            self.setProperties(object)
    
        return {'FINISHED'}
        
    # Setting automatically object name as g_prop, off for caps and tag for *tags
    def setProperties(self, object): 
                
        if "_cap_" in object.name:
            object.g2_prop_off = True
            object.g2_prop_tag = False
            
        if "*" in object.name:
            object.g2_prop_tag = True
            object.g2_prop_off = False
            
        object.g2_prop_name = object.name.replace("_" + getLOD(object), "")
        object.g2_prop_shader = ""
            
        # Let people manually set shaders, if needed


class OBJECT_OT_SelectObjectType(bpy.types.Operator):
    bl_idname = "g2.select"
    bl_label = "Model part select"
    
    def execute(self, context): 
        bpy.ops.object.select_all(action='DESELECT')
        settings = bpy.context.scene.settings
            
        for object in bpy.data.objects:
            if object.type == "EMPTY" or object.type == "ARMATURE" or "stupidtriangle" in object.name:
                continue
            
            if settings.meshes and not object.g2_prop_tag and "_cap_" not in object.name:
                object.select_set(True)
            
            if settings.tags and object.g2_prop_tag:
                object.select_set(True)
            
            if settings.caps and "cap" in object.name and not object.g2_prop_tag:
                object.select_set(True)
    
        return {'FINISHED'}
        
    
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
    OBJECT_OT_CreateSkinFile,
    OBJECT_OT_VehicleParent,    
    OBJECT_OT_UnparentAll,
    OBJECT_OT_CreateTags,
    OBJECT_OT_SelectObjectType
]

if __name__ == "__main__":
    register()
