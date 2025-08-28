import bpy
from bpy.props import *

class AddonProperties(bpy.types.PropertyGroup): 
    meshes : bpy.props.BoolProperty(name="Meshes",default=False)
    caps : bpy.props.BoolProperty(name="Caps",default=False)
    tags : bpy.props.BoolProperty(name="Tags",default=False)
    folder_path: bpy.props.StringProperty(
        name = "Save to",
        default = "",
        description = "Select a path where to save the .skin file",
        maxlen = 1024,
        subtype = "DIR_PATH"
    )
    
    shadername: bpy.props.StringProperty(name="Enter .skin name", default= "default")
    modelname: bpy.props.StringProperty(name="Enter model name", default="")
    
    object1: bpy.props.StringProperty(name="Replace", search=lambda self, context, edit_text: [o.name for o in bpy.data.objects if edit_text.lower() in o.name.lower()])
    object2: bpy.props.StringProperty(name="With", search=lambda self, context, edit_text: [o.name for o in bpy.data.objects if edit_text.lower() in o.name.lower()])
    action: bpy.props.EnumProperty(
    name="After Replace",
    description="What to do with the old object after replacing",
    items=[
        ('DELETE', "Delete", "Remove the replaced object from the scene"),
        ('UNPARENT', "Unparent", "Unparent the replaced object and rename it"),
        ('KEEP', "Keep", "Leave the replaced object as is, other than reparenting replaced object's children"),
    ],
    default='DELETE',
    )
    
   # Collapsible toggles
    show_parenting : BoolProperty(default=True)
    show_replace : BoolProperty(default=True)
    show_create : BoolProperty(default=True)
    show_set : BoolProperty(default=True)
    show_cleanup : BoolProperty(default=True)
    show_select : BoolProperty(default=True)

def register_properties():
    bpy.utils.register_class(AddonProperties)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=AddonProperties)

def unregister_properties():
    bpy.utils.unregister_class(AddonProperties)
    del bpy.types.Scene.settings