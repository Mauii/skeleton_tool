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

def register_properties():
    bpy.utils.register_class(AddonProperties)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=AddonProperties)

def unregister_properties():
    bpy.utils.unregister_class(AddonProperties)
    del bpy.types.Scene.settings