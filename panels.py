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
            row.prop(settings, toggle_prop, text=label, icon="TRIA_DOWN" if getattr(settings, toggle_prop) else "TRIA_RIGHT", emboss=False)
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

        def draw_log(box):
            layout = self.layout
            layout.alert = False

            # Filter checkboxes in a dropdown row
            filter_box = box.box()
            row = filter_box.row()
            row.label(text="Show:", icon="FILTER")
            row = filter_box.row(align=True)
            row.prop(settings, "log_show_errors",   toggle=True)
            row.prop(settings, "log_show_warnings", toggle=True)
            row.prop(settings, "log_show_details",  toggle=True)
            row.prop(settings, "log_show_summary",  toggle=True)

            box.operator("log.clear", icon="TRASH")

            lines = [l for l in settings.log.split("\n") if l.strip()]

            if lines:
                errors   = [l for l in lines if "[ERROR]" in l]
                warnings = [l for l in lines if "[WARNING]" in l]
                details  = [l for l in lines if "[INFO]" in l]
                summaries = [l for l in lines if "[SUMMARY]" in l]

                if settings.log_show_errors and errors:
                    for line in errors:
                        layout.alert = True
                        layout.label(text=line, icon='CANCEL')
                        layout.alert = False
                    if (settings.log_show_warnings and warnings) or \
                    (settings.log_show_details and details) or \
                    (settings.log_show_summary and summaries):
                        box.separator()

                if settings.log_show_warnings and warnings:
                    for line in warnings:
                        layout.label(text=line, icon='ERROR')
                    if (settings.log_show_details and details) or \
                    (settings.log_show_summary and summaries):
                        box.separator()

                if settings.log_show_details and details:
                    for line in details:
                        layout.label(text=line, icon='INFO')
                    if settings.log_show_summary and summaries:
                        box.separator()

                if settings.log_show_summary and summaries:
                    for line in summaries:
                        layout.label(text=line, icon='CHECKMARK')

                # Show a hint if all filters are off
                if not any([
                    settings.log_show_errors,
                    settings.log_show_warnings,
                    settings.log_show_details,
                    settings.log_show_summary
                ]):
                    box.label(text="All filters hidden.", icon="INFO")
            else:
                box.label(text="No actions logged yet.", icon="INFO")

        draw_box("Log", "show_log", draw_log)

def register_panels():
    bpy.utils.register_class(OBJECT_PT_SkeletonTool)

def unregister_panels():
    bpy.utils.unregister_class(OBJECT_PT_SkeletonTool)