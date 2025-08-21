import bpy

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
               
        box = layout.box() 
        box.label(text="Parenting")
        
        box.operator("parent.objects")
        box.operator("parent.tags")
        box.operator("parent.caps")
        
        box = layout.box() 
        box.label(text="Create")
        
        box.operator("create.tags")
        box.operator("create.root")
        box.operator("create.skinfile")
        
        box = layout.box() 
        box.label(text="Set")
        
        box.operator("set.armaturemod")
        box.operator("set.g2properties")
        
        box = layout.box()
        box.label(text="Vertex Groups")
        box.operator("remove.emptyvgroups")
         
        box = layout.box()
        box.label(text="Misc") 
        box.operator("remove.parent")
        box.operator("clean.hierarchy")
        
        box = layout.box()
        box.label(text="Select") 
        box.operator("select.object_type")
        box.prop(settings, "meshes")
        box.prop(settings, "caps")
        box.prop(settings, "tags")

def register_panels():
    bpy.utils.register_class(OBJECT_PT_SkeletonTool)

def unregister_panels():
    bpy.utils.unregister_class(OBJECT_PT_SkeletonTool)