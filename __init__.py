bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (3, 1),
    "blender": (4, 2),
    "location": "Object Properties -> Skeleton Tool Panel",
    "description": "This addon has many features that decrease time wasted when preparing a model for JKA.",
    "category": "Modelling / Rigging",
}

from .mod_reload import reload_modules
reload_modules(locals(), __package__, ["operators", "panels", "properties"], [])

import bpy
import jediacademy


from .operators import register_operators, unregister_operators
from .panels import register_panels, unregister_panels
from .properties import register_properties, unregister_properties

def register():
    register_properties()    # Register properties first
    register_operators()     # Register operators that may use these properties
    register_panels()        # Register panels that might display the properties

def unregister():
    unregister_panels()      # Unregister panels first
    unregister_operators()   # Then unregister operators
    unregister_properties()   # Finally, unregister properties

if __name__ == "__main__":
    register()
