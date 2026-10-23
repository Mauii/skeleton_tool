import bpy
from bpy.props import *

class AddonProperties(bpy.types.PropertyGroup):
    meshes : bpy.props.BoolProperty(name="Meshes",default=False) # pyright: ignore[reportInvalidTypeForm]
    caps : bpy.props.BoolProperty(name="Caps",default=False) # pyright: ignore[reportInvalidTypeForm]
    tags : bpy.props.BoolProperty(name="Tags",default=False) # pyright: ignore[reportInvalidTypeForm]
    folder_path: bpy.props.StringProperty(
        name = "Save to",
        default = "",
        description = "Select a path where to save the .skin file",
        maxlen = 1024,
        subtype = "DIR_PATH"
    ) # pyright: ignore[reportInvalidTypeForm]

    shadername: bpy.props.StringProperty(name="Enter .skin name", default= "default") # pyright: ignore[reportInvalidTypeForm]
    modelname: bpy.props.StringProperty(name="Enter model name", default="") # pyright: ignore[reportInvalidTypeForm]

    object1: bpy.props.StringProperty(name="Replace", search=lambda self, context, edit_text: [o.name for o in bpy.data.objects if edit_text.lower() in o.name.lower()]) # pyright: ignore[reportInvalidTypeForm]
    object2: bpy.props.StringProperty(name="With", search=lambda self, context, edit_text: [o.name for o in bpy.data.objects if edit_text.lower() in o.name.lower()]) # pyright: ignore[reportInvalidTypeForm]
    action: bpy.props.EnumProperty(
    name="After Replace",
    description="What to do with the old object after replacing",
    items=[
        ('DELETE', "Delete", "Remove the replaced object from the scene"),
        ('UNPARENT', "Unparent", "Unparent the replaced object and rename it"),
        ('KEEP', "Keep", "Leave the replaced object as is, other than reparenting replaced object's children"),
    ],
    default='DELETE',
    ) # pyright: ignore[reportInvalidTypeForm]

    # Collapsible toggles
    show_parenting : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    show_replace : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    show_create : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    show_set : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    show_cleanup : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    show_select : bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]

    # Hold the log messages to be displayed in the UI panel
    log: bpy.props.StringProperty(name="Log", default="") # pyright: ignore[reportInvalidTypeForm]

    # Toggle to show/hide the log in the UI panel
    show_log: bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]

def register_properties():
    bpy.utils.register_class(AddonProperties)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=AddonProperties)

def unregister_properties():
    bpy.utils.unregister_class(AddonProperties)
    del bpy.types.Scene.settings