from multiprocessing import context

import bpy
import bmesh
import json
import os
import re

JAG2Panels = None

# Parent mapping
parents_dict = {
    "head": "torso",
    "torso": "hips",
    "hips": "model_root",
    "l_arm": "torso",
    "r_arm": "torso",
    "l_hand": "l_arm",
    "r_hand": "r_arm",
    "l_leg": "hips",
    "r_leg": "hips"
}
parent_all = False
PARENT_SCALE_RECOVERY_THRESHOLD_METERS = 10.0
PARENT_SCALE_RECOVERY_FACTOR = 10.0
PARENT_SCALE_RECOVERY_TOLERANCE = 0.5

############################################################################################
# UI refresh helper
############################################################################################
def force_ui_refresh(context):
    """Force Blender to redraw all areas and update the depsgraph."""
    # Update depsgraph
    context.view_layer.update()

    # Redraw all areas in all windows
    wm = context.window_manager
    for window in wm.windows:
        screen = window.screen
        if not screen:
            continue
        for area in screen.areas:
            area.tag_redraw()
#end of UI refresh helper
############################################################################################
# Helper function to log actions in the addon log property
############################################################################################
def log_action(context, message: str, level: str = "INFO"):
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    settings = context.scene.settings
    existing = settings.log
    settings.log = (existing + "\n" + entry).strip()
#End of log function

def clear_log(context):
    context.scene.settings.log = ""

class OBJECT_OT_ClearLog(bpy.types.Operator):
    """Clear the action log used for tracking operations and errors within the addon."""
    bl_idname = "log.clear"
    bl_label = "Clear Log"
    bl_description = "Clear all logged messages"

    def execute(self, context):
        clear_log(context)
        force_ui_refresh(context)
        return {'FINISHED'}
#End of log clear operator
#
################################################################################################
##                                                                                            ##
##                                        CREATE TAGS                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateTags(bpy.types.Operator):
    """
    Create all tags for each model_root in the scene, using premade JSON data.
    """

    bl_idname = "create.tags"
    bl_label = "Create Tags"
    bl_description = "Create all tags (if not existing yet)"

    def execute(self, context):
        # Get the current directory of the addon
        addon_directory = os.path.dirname(os.path.realpath(__file__))
        clear_log(context)
        counter = 0
        # Define the JSON file path within the addon directory
        file_path = os.path.join(addon_directory, "tags.json")

        if not os.path.exists(file_path):
            self.report({'ERROR'}, "Tags data file not found.")
            log_action(context, "Tags data file not found. Cannot create tags.", level="WARNING")
            return {'CANCELLED'}

        # Load JSON data
        mesh_data_list = self.load_mesh_data(file_path)

        # Find all model_root_X objects
        model_roots = self.get_all_model_roots()

        if not model_roots:
            self.report({'ERROR'}, "No model_root objects found.")
            log_action(context, "No model_root objects found. Cannot create tags.", level="ERROR")
            return {'CANCELLED'}

        for lod in model_roots:
            for mesh_data in mesh_data_list:
                self.create_mesh_from_data(mesh_data, lod)
                counter = counter + 1

        self.report({'INFO'}, f"Tags created for {len(model_roots)} model_root(s).")
        log_action(context, f"Tags created for {len(model_roots)} model_root(s). ({counter} objects processed.)", level="INFO")
        force_ui_refresh(context)
        return {'FINISHED'}

    def load_mesh_data(self, file_path):
        """Loads mesh data from a JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def create_mesh_from_data(self, mesh_data, lod):
        """Creates a mesh from extracted data and assigns vertex groups and weights"""

        # Construct unique object name
        name = f"{mesh_data['name']}_{lod}"

        # Check if the object already exists
        if name in bpy.data.objects:
            self.report({'INFO'}, f"Object '{name}' already exists, skipping creation.")
            log_action(bpy.context, f"Object '{name}' already exists, skipping creation.", level="INFO")
            return bpy.data.objects[name]

        # Create a new mesh and object
        mesh = bpy.data.meshes.new(name)
        object = bpy.data.objects.new(name, mesh)

        # Link the object to the Scene Collection
        bpy.context.scene.collection.objects.link(object)

        # Create a BMesh
        bm = bmesh.new()

        # Add vertices
        vertex_map = {}
        for vert in mesh_data['vertices']:
            vertex = bm.verts.new(vert)
            vertex_map[len(vertex_map)] = vertex  # Store the vertex by index

        # Add faces
        for face in mesh_data['faces']:
            bm.faces.new([vertex_map[i] for i in face])

        # Finish BMesh and write to the mesh
        bm.to_mesh(mesh)
        bm.free()

        # Assign vertex groups and weights
        if 'vertex_groups' in mesh_data:
            for group_name, vertices_weights in mesh_data['vertex_groups'].items():
                # Create the vertex group
                vertex_group = object.vertex_groups.new(name=group_name)

                # Assign weights
                for vw in vertices_weights:
                    vertex_index = vw['vertex_index']
                    weight = vw['weight']
                    vertex_group.add([vertex_index], weight, 'REPLACE')

        # Scale the object
        object.scale = (object.scale[0] / 10, object.scale[1] / 10, object.scale[2] / 10)

        # Apply transformations
        bpy.context.view_layer.objects.active = object
        object.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        object.select_set(False)

        try:
            # Add Armature modifier
            object.modifiers.new(name="Armature", type='ARMATURE')
            object.modifiers["Armature"].object = bpy.data.objects["skeleton_root"]
        except:
            print(f"WARNING: 'skeleton_root' not found, cannot assign to {object.name}")
            log_action(context, f"'skeleton_root' not found, cannot assign to {object.name}", level="WARNING")

        # set ghoul2 specific properties
        object.g2_prop.name = mesh_data['name']  # pyright: ignore [reportAttributeAccessIssue]
        object.g2_prop.shader = ""  # pyright: ignore [reportAttributeAccessIssue]
        object.g2_prop.off = False  # pyright: ignore [reportAttributeAccessIssue]
        object.g2_prop.tag = True   # pyright: ignore [reportAttributeAccessIssue]
        if JAG2Panels is not None:
            JAG2Panels.markG2Configured(object)

        return object

    def get_all_model_roots(self):
        """
        Finds all objects named like 'model_root_X' and returns their numbers as a sorted list.
        """
        pattern = re.compile(r"^model_root_(\d+)$")
        model_roots = []

        for obj in bpy.data.objects:
            match = pattern.match(obj.name)
            if match:
                model_roots.append(int(match.group(1)))

        return sorted(model_roots)


################################################################################################
##                                                                                            ##
##                                        PARENT TAGS                                         ##
##                                                                                            ##
################################################################################################

class ParentingOperator:
    """Shared execution and transform-preserving parenting behavior."""

    triangulate_meshes = False
    completion_message = "Parenting complete."

    def execute(self, context):
        if not parent_all:
            clear_log(context)

        processed = 0
        warnings = 0
        errors = 0

        context.view_layer.update()

        # A snapshot is needed because the body operator can delete objects.
        for child in tuple(bpy.data.objects):
            try:
                self.recover_parent_scale(context, child)

                if self.should_skip(child):
                    continue

                if self.triangulate_meshes and child.type == 'MESH':
                    triangulate(child)

                parent = self.get_parent(child)
                if parent is None:
                    warnings += 1
                    self.log(
                        context,
                        "No parent was found for '{child}'.",
                        child=child.name,
                        level="WARNING",
                    )
                    continue

                self.set_parent(context, child, parent)
                processed += 1
            except Exception as error:
                errors += 1
                self.log(
                    context,
                    "{} failed: {}",
                    child.name,
                    error,
                    level="ERROR",
                )

        self.log(
            context,
            "{} ({processed} objects, {warnings} warnings, {errors} errors)",
            self.completion_message,
            processed=processed,
            warnings=warnings,
            errors=errors,
        )
        force_ui_refresh(context)
        return {'FINISHED'}

    def recover_parent_scale(self, context, child: bpy.types.Object) -> None:
        dimensions_meters = max(abs(value) for value in child.dimensions)
        dimensions_meters *= context.scene.unit_settings.scale_length
        scale_components = tuple(abs(value) for value in child.scale)
        expected_scale = PARENT_SCALE_RECOVERY_FACTOR
        tolerance = PARENT_SCALE_RECOVERY_TOLERANCE

        if dimensions_meters <= PARENT_SCALE_RECOVERY_THRESHOLD_METERS:
            return

        if not all(
            expected_scale - tolerance <= component <= expected_scale + tolerance
            for component in scale_components
        ):
            return

        old_scale = tuple(child.scale)
        child.scale = tuple(
            component / PARENT_SCALE_RECOVERY_FACTOR
            for component in child.scale
        )
        context.view_layer.update()
        self.log(
            context,
            "Recovered likely 10x parent scale on '{child}' "
            "(largest dimension {dimension:.2f} m, scale {old_scale} -> {new_scale}).",
            child=child.name,
            dimension=dimensions_meters,
            old_scale=old_scale,
            new_scale=tuple(child.scale),
            level="WARNING",
        )

    def log(self, context, template, *args, level="INFO", **kwargs):
        """Format positional or named message values before logging."""
        log_action(context, template.format(*args, **kwargs), level=level)

    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object | None:
        raise NotImplementedError(
            f"{type(self).__name__} must define a parent rule for {child.name!r}."
        )

    def should_skip(self, child: bpy.types.Object) -> bool:
        raise NotImplementedError(
            f"{type(self).__name__} must define a skip rule for {child.name!r}."
        )

    def set_parent(
        self,
        context,
        child: bpy.types.Object,
        parent: bpy.types.Object,
    ) -> None:
        world_matrix = child.matrix_world.copy()
        child.parent = parent
        child.matrix_world = world_matrix
        self.log(
            context,
            "'{child}' parented to '{parent}'.",
            child=child.name,
            parent=parent.name,
        )


class OBJECT_OT_TagParent(bpy.types.Operator, ParentingOperator):
    """Parent tags to their corresponding body objects."""

    bl_idname = "parent.tags"
    bl_label = "Parent Tags"
    bl_description = "Parent all tags to their respective parents."
    completion_message = "Tag parenting complete."

    def execute(self, context):
        return ParentingOperator.execute(self, context)

    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object | None:
        name_parts = child.name[1:].split('_')
        if not name_parts or not name_parts[-1]:
            return None

        base = name_parts[0]
        lod = name_parts[-1]
        if base in {'l', 'r'}:
            if len(name_parts) < 3:
                return None
            parent_name = f"{base}_{name_parts[1]}_{lod}"
        elif base in {'hips', 'head'}:
            parent_name = f"{base}_{lod}"
        else:
            parent_name = f"torso_{lod}"

        return bpy.data.objects.get(parent_name)

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if not object.g2_prop.tag:
            return True

        return False


################################################################################################
##                                                                                            ##
##                                  SET BODY PARENTING                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_BodyParent(bpy.types.Operator, ParentingOperator):
    """Parent regular model objects to their corresponding body objects."""

    bl_idname = "parent.objects"
    bl_label = "Parent Objects"
    bl_description = "Parent all objects to their respective parents and apply triangulate if needed."
    triangulate_meshes = True
    completion_message = "Body parenting complete."

    def execute(self, context):
        return ParentingOperator.execute(self, context)

    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object | None:
        name_parts = child.name.split("_")

        if "skeleton_root" in child.name or "model_root" in child.name:
            return bpy.data.objects.get("scene_root")

        if len(name_parts) > 1 and name_parts[1].isnumeric():
            parent_key = child.name[:-2]
            parent_type = parents_dict.get(parent_key)
            if parent_type is None:
                return None
            parent_name = f"{parent_type}_{child.name[-1]}"
        elif child.name.startswith(("l_", "r_")):
            if len(name_parts) > 3:
                parent_name = (
                    f"{name_parts[0]}_{name_parts[1]}_{child.name[-1]}"
                )
            else:
                parent_key = child.name[:-2]
                parent_type = parents_dict.get(parent_key)
                if parent_type is None:
                    return None
                parent_name = f"{parent_type}_{child.name[-1]}"
        else:
            parent_name = f"{name_parts[0]}_{child.name[-1]}"

        return bpy.data.objects.get(parent_name)

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if "stupidtriangle" in object.name:
            print(f"{object.name} deleted.")
            bpy.data.objects.remove(object, do_unlink=True)
            return True

        if object.g2_prop.tag or object.name == "scene_root" or ("_cap_" in object.name and "_off" in object.name[:-2]) or object.name.startswith("*"):
            return True

        return False


################################################################################################
##                                                                                            ##
##                                  SET CAP PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CapParent(bpy.types.Operator, ParentingOperator):
    """Parent cap meshes to their corresponding body objects."""

    bl_idname = "parent.caps"
    bl_label = "Parent Caps"
    bl_description = "Parent all caps to their respective parents and apply triangulate if needed."
    triangulate_meshes = True
    completion_message = "Cap parenting complete."

    def execute(self, context):
        return ParentingOperator.execute(self, context)

    def get_parent(self, child: bpy.types.Object) -> bpy.types.Object | None:
        name_parts = child.name.split("_")
        if name_parts[0] in {"l", "r"}:
            if len(name_parts) < 4:
                return None
            parent_name = f"{name_parts[0]}_{name_parts[1]}_{name_parts[-1]}"
        else:
            parent_name = f"{name_parts[0]}_{name_parts[-1]}"

        return bpy.data.objects.get(parent_name)

    def should_skip(self, object: bpy.types.Object) -> bool:
        return (
            object.type != 'MESH'
            or "_cap_" not in object.name
            or object.g2_prop.tag
        )


################################################################################################
##                                                                                            ##
##                                  SET ALL PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_AllParent(bpy.types.Operator):

    bl_idname = "parent.all"
    bl_label = "Parent All"
    bl_description = "Parent everything at once."

    def execute(self, context):
        global parent_all
        parent_all = True
        clear_log(context)

        try:
            bpy.ops.parent.objects()
            bpy.ops.parent.tags()
            bpy.ops.parent.caps()
        finally:
            parent_all = False

        log_action(context, "All parenting operations complete.", level="INFO")
        return {'FINISHED'}


################################################################################################
##                                                                                            ##
##                                  SET G2 PROPERTIES                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_SetG2Properties(bpy.types.Operator):
    """
    This class makes sure to set all g2_properties for all objects within the scene. This is needed for
    JKA to be able to run this model at all. Even modview needs it.

    If you want to set a custom shader, change g2_prop_shader after using this function or it will be
    overwritten by emptiness.

    ---------
    Methods:
    ---------
    set_g2_properties(self, object)
        This takes an object and sets any Ghoul2 property to what it should be.

    should_skip(self, object)
        This runs a check if it is a stupidtriangle or a specific reason to skip the current object.
        If none of these have a reason to skip, it will return False so the main function continues.
    """

    bl_idname = "set.g2properties"
    bl_label = "Set G2 Properties"
    bl_description = "Set all Ghoul2 properties"

    def execute(self, context):
        
        clear_log(context)
        counter = 0
        self.meshes_counter = 0
        self.tags_counter = 0
        self.caps_counter = 0
        self.tags_fixed = False
        self.caps_fixed = False
        self.meshes_fixed = False

        for object in bpy.data.objects:

            if self.should_skip(object):
                continue

            self.set_g2_properties(object)
            counter += 1
        log_action(context, f"G2 properties set for all objects. ({counter} objects processed.)", level="INFO")
        log_action(context, f"{self.meshes_counter} meshes, {self.tags_counter} tags, {self.caps_counter} caps processed.", level="INFO")
        force_ui_refresh(context)
        return {'FINISHED'}

    def set_g2_properties(self, object: bpy.types.Object) -> None:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if not object.g2_prop.name or not object.g2_prop.name == object.name[:-2]:
            object.g2_prop.name = object.name[:-2]
            log_action(bpy.context, f"{object.name} has an unexpected name format, g2_prop_name set to {object.name}", level="WARNING")

        object.g2_prop.shader = ""
        object.g2_prop.scale = 100.0

        if "_off" in object.name[:-2]:
            self.caps_fixed = False
            if object.g2_prop.off  is not True:
                object.g2_prop.off = True
                log_action(bpy.context, f"{object.name} Off=True.", level="INFO")
                self.caps_fixed = True
            if object.g2_prop.tag is not False:
                object.g2_prop.tag = False
                log_action(bpy.context, f"{object.name} Tag=False.", level="INFO")
                self.tags_fixed = True
            if self.caps_fixed:
                self.caps_counter += 1

        elif object.name.startswith("*"):
            self.tags_fixed = False
            if object.g2_prop.tag is not True:
                object.g2_prop.tag = True
                log_action(bpy.context, f"{object.name} Tag=True.", level="INFO")
                self.tags_fixed = True
            if object.g2_prop.off  is not False:
                object.g2_prop.off = False
                log_action(bpy.context, f"{object.name} Off=False.", level="INFO")
                self.tags_fixed = True
            if self.tags_fixed:
                self.tags_counter += 1
        else:
            self.meshes_fixed = False
            if object.g2_prop.tag is not False:
                object.g2_prop.tag = False
                log_action(bpy.context, f"{object.name} Tag=False.", level="INFO")
                self.meshes_fixed = True
            if object.g2_prop.off is not False:
                object.g2_prop.off = False
                log_action(bpy.context, f"{object.name} Off=False.", level="INFO")
                self.meshes_fixed = True
            if self.meshes_fixed:
                self.meshes_counter += 1

        if JAG2Panels is not None:
            JAG2Panels.markG2Configured(object)

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if "root" in object.name:
            return True

        return False

################################################################################################
##                                                                                            ##
##                               REMOVE ALL PARENTING                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_UnparentAll(bpy.types.Operator):
    """ Remove all child-parent relations """

    bl_idname = "remove.parent"
    bl_label = "Unparent All"

    def execute(self, context):
        
        clear_log(context)
        counter = 0

        for object in bpy.data.objects:
            matrixcopy = object.matrix_world.copy()
            object.parent = None
            object.matrix_world = matrixcopy
            counter = counter + 1
        force_ui_refresh(context)
        log_action(context, f"All parenting removed. ({counter} objects processed.)")
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                                   CLEAN DUPLICATES                                         ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_Clean(bpy.types.Operator):
    """ Delete all objects with atleast .00 in their names """

    bl_idname = "clean.hierarchy"
    bl_label = "Clean duplicates"

    def execute(self, context):
        
        clear_log(context)
        counter = 0

        for object in bpy.data.objects:

            if ".00" in object.name:
                object.select_set(True)
                bpy.ops.object.delete(use_global=True, confirm=True)
                counter = counter + 1

        log_action(context, f"Duplicate cleaning complete. ({counter} objects deleted.)")
        force_ui_refresh(context)
        return {'FINISHED'}

################################################################################################
##                                                                                            ##
##                              CREATE MODEL_DEFAULT.SKIN                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateSkinFile(bpy.types.Operator):
    """ Create a model_default.skin file """
    bl_idname = "create.skinfile"
    bl_label = "Create .SKIN"

    def draw(self, context):
        props = context.scene.settings

        layout = self.layout

        # Create a split layout with custom proportions
        split = layout.split(factor=0.3)  # 30% for the label, 70% for the field

        # Add properties to the split layout
        col = split.column()  # Label column
        col.label(text="Folder Path:")
        col = split.column()  # Property field column
        col.prop(props, "folder_path", text="")

        split = layout.split(factor=0.3)
        col = split.column()
        col.label(text="Shader Name:")
        col = split.column()
        col.prop(props, "shadername", text="")

        split = layout.split(factor=0.3)
        col = split.column()
        col.label(text="Model Name:")
        col = split.column()
        col.prop(props, "modelname", text="")

    def execute(self, context):
        props = context.scene.settings
        path = bpy.path.abspath(props.folder_path)
        shadername = props.shadername
        modelname = props.modelname

        try:
            with open(path + f"/model_{shadername}.skin", "w") as file:
                modelparts = ""
                caps = ""
                roots = ("skeleton_root", "model_root", "scene_root")

                for object in bpy.data.objects:
                    # Skip model_root, scene_root and skeleton_root, tags and objects without an active_material set.
                    if object.type != "MESH" or object.g2_prop.tag or any(root in object.name for root in roots):
                        continue

                    if object.g2_prop.off:
                        caps += f"{object.g2_prop.name},models/players/stormtrooper/caps.tga\n"
                        continue

                    materialname = (re.sub(r'\.\d+$', '', self.get_image(object))) if self.get_image(object) else None
                    modelparts += f"{object.g2_prop.name},models/players/{modelname}/{materialname}.tga\n"

                output = f"{modelparts}\n{caps}"

                # Write to the file
                file.write(output)

            self.report({'INFO'}, "model_default.skin created.")
            log_action(context, "model_default.skin created successfully.")
            force_ui_refresh(context)
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to create .skin file: {e}")
            log_action(context, f"Error: Failed to create .skin file: {e}")
            return {'CANCELLED'}

    def invoke(self, context, event) -> None:
        return context.window_manager.invoke_props_dialog(self)

    def get_image(self, object) -> str:
        if object.active_material:
            material = object.active_material

            # Check if the material uses nodes
            if material.use_nodes:
                # Get the node tree of the material
                nodes = material.node_tree.nodes

                # Find the Principled BSDF node
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        # Check if Base Color is linked
                        base_color_input = node.inputs['Base Color']

                        if base_color_input.is_linked:
                            # Get the node linked to Base Color
                            linked_node = base_color_input.links[0].from_node

                            if linked_node.type == 'TEX_IMAGE':
                                # Get the image from the image texture node
                                image = linked_node.image
                            else:
                                print("Base Color is not linked to an image texture.")
                                log_action(bpy.context, "Base Color is not linked to an image texture.")
                        else:
                            print("Base Color is not linked.")
                            log_action(bpy.context, "Base Color is not linked.")
                        break
                else:
                    print("Principled BSDF node not found.")
                    log_action(bpy.context, "Principled BSDF node not found.")
        else:
            return object.active_material.name.split("/")[-1][:-4]
        return image.name[:-4]

################################################################################################
##                                                                                            ##
##                                     SELECT OBJECT TYPE                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_SelectObjectType(bpy.types.Operator):
    """ Select all (caps/tags/objects) or both """

    bl_idname = "select.object_type"
    bl_label = "Model part select"

    def execute(self, context):
        

        bpy.ops.object.select_all(action='DESELECT')

        settings = bpy.context.scene.settings
        scene_collection = bpy.context.scene.collection
        mesh_counter = 0
        tag_counter = 0
        cap_counter = 0
        for object in bpy.data.objects:
            if self.should_skip(object):
                continue

            try:
                if settings.meshes and (not object.g2_prop.tag and "_cap_" not in object.name):
                    object.select_set(True)
                    mesh_counter = mesh_counter + 1

                if settings.tags and object.g2_prop.tag:
                    object.select_set(True)
                    tag_counter = tag_counter + 1

                if settings.caps and object.g2_prop.off:
                    object.select_set(True)
                    cap_counter = cap_counter + 1
            except:
                if object.name not in scene_collection.objects:
                    print(f"WARNING: {object.name} was not selected. It's in a different collection.")
                    log_action(context, f"WARNING: {object.name} was not selected. It's in a different collection.")
                else:
                    print(f"WARNING: {object.name} was not selected, reason unknown.")
                    log_action(context, f"WARNING: {object.name} was not selected, reason unknown.")

        log_action(context, f"Object selection complete. ({mesh_counter} meshes, {tag_counter} tags, {cap_counter} caps selected.)")
        force_ui_refresh(context)
        return {'FINISHED'}

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if object.type != 'MESH':
            return True

        return False

################################################################################################
##                                                                                            ##
##                                        SET ARMATURE                                        ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_SetArmature(bpy.types.Operator):
    """
    This class will set the skeleton_root to all objects if they don't have it already.
    """

    bl_idname = "set.armaturemod"
    bl_label = "Set Armature Modifier"
    bl_description = "Setup an armature modifier with skeleton_root"

    def execute(self, context):
        
        clear_log(context)
        counter = 0

        for object in bpy.data.objects:

            if self.should_skip(object):
                continue

            # Make sure we have only 1 armature modifier
            for mod in object.modifiers:
                if mod.type == 'ARMATURE':
                    object.modifiers.remove(mod)
                    counter = counter + 1

            object.modifiers.new("Armature", type="ARMATURE")
            object.modifiers["Armature"].object = bpy.data.objects["skeleton_root"]

        log_action(context, f"Armature modifier set on all objects. ({counter} objects processed.)")
        force_ui_refresh(context)
        return {'FINISHED'}

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if object.type != 'MESH':
            return True

        return False

################################################################################################
##                                                                                            ##
##                                REMOVE EMPTY VERTEX GROUPS                                  ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_RemoveEmptyVertexGroups(bpy.types.Operator):
    """
    This class will check every object for empty vertex groups.
    """

    bl_idname = "remove.emptyvgroups"
    bl_label = "Remove Empty VGroups"

    def execute(self, context):
        
        clear_log(context)
        counter = 0
        try:
            for object in bpy.data.objects:

                if self.should_skip(object):
                    continue

                self.remove_vertex_groups(object)
                counter = counter + 1
        except:
            print(f"WARNING: No possible object selected.")
            log_action(context, f"WARNING: No possible object selected.")

        log_action(context, f"Empty vertex group removal complete. ({counter} objects processed.)")
        force_ui_refresh(context)
        return {'FINISHED'}

    def remove_vertex_groups(self, object: bpy.types.Object) -> None:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        # List to store vertex groups to remove
        vertex_groups_to_remove = []

        # Iterate through the vertex groups
        for vgroup in object.vertex_groups:
            # Initialize the count and weight sum for this vertex group
            count = 0
            weight_sum = 0.0

            # Count the number of vertices assigned to this vertex group and their weights
            for vertex in object.data.vertices:
                for group in vertex.groups:
                    if group.group == vgroup.index:
                        count += 1
                        weight_sum += group.weight  # Get the weight of the vertex for this group
                        break  # No need to check other groups for this vertex

            # Check the conditions: count < 5 or weight_sum < 0.50
            if count < 5 or weight_sum < 0.100:
                vertex_groups_to_remove.append(vgroup)

        # Remove the empty vertex groups
        for vgroup in vertex_groups_to_remove:
            object.vertex_groups.remove(vgroup)

    def should_skip(self, object: bpy.types.Object) -> bool:
        if not isinstance(object, bpy.types.Object):
            raise TypeError(f"{object.name} must be an Object.")

        if object.type != 'MESH' or "root" in object.name:
            return True

        return False

################################################################################################
##                                                                                            ##
##                                CREATE SCENE/MODEL ROOT                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_CreateRoot(bpy.types.Operator):
    """ Create scene_root and model_root_0 """
    bl_idname = "create.root"
    bl_label = "Create Model/Scene"

    def execute(self, context):
        
        scene_collection = context.scene.collection

        # Ensure 'scene_root' exists in the Scene Collection
        if "scene_root" not in bpy.data.objects:
            # Create the Empty object data container
            scene_root = bpy.data.objects.new("scene_root", None)
            scene_root.empty_display_type = 'PLAIN_AXES'
            scene_root.location = (0, 0, 0)
            # Link it directly to the Scene Collection
            scene_collection.objects.link(scene_root)
        else:
            scene_root = bpy.data.objects["scene_root"]
            # Optional: If it already exists but is hidden in another collection, link it to the root
            if scene_root.name not in scene_collection.objects:
                scene_collection.objects.link(scene_root)

        # Ensure 'model_root_0' exists in the Scene Collection
        if "model_root_0" not in bpy.data.objects:
            model_root = bpy.data.objects.new("model_root_0", None)
            model_root.empty_display_type = 'PLAIN_AXES'
            model_root.location = (0, 0, 0)
            scene_collection.objects.link(model_root)
        else:
            model_root = bpy.data.objects["model_root_0"]
            if model_root.name not in scene_collection.objects:
                scene_collection.objects.link(model_root)

        # Clean up selection
        bpy.ops.object.select_all(action='DESELECT')

        # Custom functions from your original script
        log_action(context, "Scene and Model root created in Scene Collection.")
        force_ui_refresh(context)

        return {'FINISHED'}


################################################################################################
##                                                                                            ##
##                                     ORIGIN TO GEOMETRY                                     ##
##                                                                                            ##
################################################################################################

class OBJECT_OT_OrigintoGeometry(bpy.types.Operator):
    """ Set Origin to Geometry on all objects """

    bl_idname = "origin.geometry"
    bl_label = "Set Origin to Geometry"

    def execute(self, context):
        
        clear_log(context)
        counter = 0

        for object in bpy.context.scene.objects:
            if object.type == 'MESH':
                bpy.context.view_layer.objects.active = object
                object.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                object.select_set(False)
                counter = counter + 1

        print("Origin to Geometry set on all objects.")
        log_action(context, f"Origin to Geometry set on all objects. ({counter} objects processed.)")

        return {'FINISHED'}

class OBJECT_OT_ReplaceObject(bpy.types.Operator):
    """
    This class will assist your kitbashing even further. Instead of unparenting everything, you can now
    define object 1 (object to replace) and object 2 (object to replace object 1 with).

    It will rename object 2 to the name of object 1, it will also parent object 2 to the parent of
    object 1. Then it will see what children object 1 has and parent those to object 2.

    ------
    METHODS:
    ------

        copy_parenting(self, object1, object2):
            This will copy every parent-child relations of object1 to object2
    """

    bl_idname = "object.replace_object"
    bl_label = "Replace Object"
    bl_description = "Replace Object 1 with Object 2 (Rename & Take over child-parent relations)"

    def execute(self, context):
        props = context.scene.settings
        object1_name = props.object1
        object2_name = props.object2
        action = props.action

        if object1_name == "" or object2_name == "":
            self.report({'ERROR'}, "Please select both objects")
            log_action(context, "ERROR: Please select both objects.")
            return {'CANCELLED'}

        if object1_name == object2_name:
            self.report({'ERROR'}, "Cannot replace an object with itself")
            log_action(context, "ERROR: Cannot replace an object with itself.")
            return {'CANCELLED'}

        object1 = bpy.data.objects[object1_name]
        object2 = bpy.data.objects[object2_name]

        if not object1 or not object2:
            self.report({'ERROR'}, "Objects not found")
            log_action(context, "ERROR: Objects not found.")
            return {'CANCELLED'}

        if action == 'DELETE':
            self.copy_parenting(object1, object2)

            old_name = object1.name
            bpy.data.objects.remove(object1)  # delete Object 1
            object2.name = old_name           # rename Object 2

        elif action == 'UNPARENT':
            self.copy_parenting(object1, object2)

            old_name = object1.name
            log_action(context, f"Object 1 old name: {old_name}")
            log_action(context, f"Object 2 old name: {object2.name}")
            object1.name = f"replaced_{old_name}"
            object2.name = old_name           # rename Object 2
            log_action(context, f"Object 2 new name: {object2.name}")

            matrixcopy = object1.matrix_world.copy()
            object1.parent = None
            object1.matrix_world = matrixcopy


        elif action == 'KEEP':
            self.copy_parenting(object1, object2)

            old_name = object1.name
            object1.name = f"replaced_{old_name}"
            object2.name = old_name           # rename Object 2


        self.report({'INFO'}, f"Replaced {object1_name} with {object2_name}")
        log_action(context, f"Replaced {object1_name} with {object2_name} using action: {action}")
        force_ui_refresh(context)
        return {'FINISHED'}

    def copy_parenting(self, object1: bpy.types.Object, object2: bpy.types.Object) -> None:
        if not isinstance(object1, bpy.types.Object):
            raise TypeError(f"{object1.name} must be an Object.")
        if not isinstance(object2, bpy.types.Object):
            raise TypeError(f"{object2.name} must be an Object.")

        # Give object2 the same parent as object1
        object2.parent = object1.parent
        object2.matrix_parent_inverse = object1.matrix_parent_inverse.copy()

        # Reparent all children of object1 to object2
        for child in object1.children:
            child.parent = object2
            child.matrix_parent_inverse = object2.matrix_world.inverted() @ child.matrix_world

        print(f"Copied parenting from {object1.name} to {object2.name}")
        log_action(bpy.context, f"Copied parenting from {object1.name} to {object2.name}")

def triangulate(object: bpy.types.Object) -> None:
    if not isinstance(object, bpy.types.Object):
        raise TypeError(f"{object.name} must be an Object.")

    mesh = object.data

    # Check for non-triangulated faces
    if any(len(face.vertices) > 3 for face in mesh.polygons):
        object.modifiers.new(name="Triangulate", type='TRIANGULATE')
        object.modifiers['Triangulate'].quad_method = 'BEAUTY'
        object.modifiers['Triangulate'].ngon_method = 'BEAUTY'
        object.modifiers['Triangulate'].min_vertices = 4  # Minimum vertices for ngons

        # Apply the modifier
        bpy.context.view_layer.objects.active = object
        bpy.ops.object.modifier_apply(modifier="Triangulate")


classes = [
    OBJECT_OT_ReplaceObject,
    OBJECT_OT_AllParent,
    OBJECT_OT_BodyParent,
    OBJECT_OT_CapParent,
    OBJECT_OT_TagParent,
    OBJECT_OT_UnparentAll,
    OBJECT_OT_SetG2Properties,
    OBJECT_OT_CreateTags,
    OBJECT_OT_Clean,
    OBJECT_OT_CreateSkinFile,
    OBJECT_OT_SelectObjectType,
    OBJECT_OT_SetArmature,
    OBJECT_OT_RemoveEmptyVertexGroups,
    OBJECT_OT_CreateRoot,
    OBJECT_OT_OrigintoGeometry,
    OBJECT_OT_ClearLog,
]

def register_operators():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister_operators():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)