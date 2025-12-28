bl_info = {
    "name": "Skeleton Tool",
    "author": "Maui",
    "version": (4, 6, 0),
    "blender": (5, 0),
    "location": "Press N - Select Skeleton tool",
    "description": "This addon has many features that decrease time wasted when preparing a model for JKA.",
    "category": "Modelling / Rigging",
}

import bpy
import importlib.util
import sys
from collections.abc import Iterable
from .operators import register_operators, unregister_operators
from .panels import register_panels, unregister_panels
from .properties import register_properties, unregister_properties
from pathlib import Path

def find_parent_folder_of_file(filename):
    """
    Recursively search all addon folders for a specific file.
    Returns the parent folder path if found and contains __init__.py, else None.
    """
    for script_path in bpy.utils.script_paths():
        addons_path = Path(script_path) / "addons"
        if not addons_path.exists():
            continue

        for path in addons_path.rglob(filename):
            if path.is_file() and (path.parent / "__init__.py").exists():
                return str(path.parent)

    return None

def import_package_from_file(filenames, package_name=None):
    """
    Find a file or a collection of files in addons and import the parent
    folder as a package.
    Returns the imported package module, or None if not found.
    """
    if isinstance(filenames, (str, Path)):
        filenames = [filenames]

    if not isinstance(filenames, Iterable):
        filenames = [filenames]

    filenames = [str(f) for f in filenames]

    folder_path = None
    for filename in filenames:
        folder_path = find_parent_folder_of_file(filename)
        if folder_path:
            break

    if not folder_path:
        print(f"Parent folder for '{', '.join(filenames)}' not found or missing __init__.py")
        return None

    folder_path = Path(folder_path)
    if package_name is None:
        package_name = folder_path.name

    init_file = folder_path / "__init__.py"
    spec = importlib.util.spec_from_file_location(package_name, str(init_file))
    module = importlib.util.module_from_spec(spec)
    sys.modules[package_name] = module
    spec.loader.exec_module(module)
    print(f"Package '{package_name}' imported from {folder_path}")

    return module

import_package_from_file("JAG2GLM.py")

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
