# Changelog

## 2025-12-12
- Allow `import_package_from_file` to accept a sequence of lookup files so other scripts can register themselves from a single call.
- Have the tag/body/cap operators pull real `bpy.data.objects` parents, rely on `== 'MESH'` comparisons, and stop clearing the console so Blender 5 actually parents the objects.
- Standardize Ghoul2 property access on `obj.g2_prop.*` (instead of `g2_prop_name`, `g2_prop_tag`, etc.) across creation, tagging, and selection operators.
