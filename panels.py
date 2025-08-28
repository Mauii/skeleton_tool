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
        layout = self.layout
        settings = context.scene.settings

        # Helper for collapsible boxes
        def draw_box(label, toggle_prop, draw_content):
            row = layout.row()
            row.prop(settings, toggle_prop, text=label, icon="REMOVE" if getattr(settings, toggle_prop) else "PLUS", emboss=False)
            if getattr(settings, toggle_prop):
                box = layout.box()
                draw_content(box)

        draw_box("Parenting", "show_parenting", lambda box: [
            box.operator("parent.all"),
            box.operator("parent.objects"),
            box.operator("parent.tags"),
            box.operator("parent.caps"),
            box.operator("remove.parent")
        ])

        draw_box("Replace", "show_replace", lambda box: [
            box.prop(settings, "object1"),
            box.prop(settings, "object2"),
            box.prop(settings, "action"),
            box.operator("object.replace_object", icon="ARROW_LEFTRIGHT")
        ])

        draw_box("Create", "show_create", lambda box: [
            box.operator("create.tags"),
            box.operator("create.root"),
            box.operator("create.skinfile")
        ])

        draw_box("Set", "show_set", lambda box: [
            box.operator("set.armaturemod"),
            box.operator("set.g2properties"),
            box.operator("origin.geometry")
        ])

        draw_box("Cleanup", "show_cleanup", lambda box: [
            box.operator("remove.emptyvgroups"),
            box.operator("clean.hierarchy")
        ])

        draw_box("Select", "show_select", lambda box: [
            box.operator("select.object_type"),
            box.prop(settings, "meshes"),
            box.prop(settings, "caps"),
            box.prop(settings, "tags")
        ])

def register_panels():
    bpy.utils.register_class(OBJECT_PT_SkeletonTool)

def unregister_panels():
    bpy.utils.unregister_class(OBJECT_PT_SkeletonTool)