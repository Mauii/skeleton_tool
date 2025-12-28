# Skeleton Tool Add-on (Blender 4.5)

A Blender add-on that accelerates preparing models for Jedi Knight: Jedi Academy. It ships with helpers to set Ghoul2 properties, parent tags/caps, clean duplicates, export `.skin` definitions, and keep replaces synchronized without breaking world transforms.

## Compatibility
- Tested with Blender 4.5+.
- Add-on version **4.5.0** reflects the Blender version it targets and contains safeguards against `ReferenceError` leaks when dangling objects disappear.

## Installation
1. Copy the `skeleton_tool` folder into `Blender/<version>/scripts/addons/`.
2. Enable the add-on from **Edit > Preferences > Add-ons** by searching for _Skeleton Tool_.
3. Press `N` in the 3D Viewport and open the *Skeleton Tool* panel under the sidebar.

## Features
- Batch parenting/tagging for meshes, caps, and tags with automatic triangle cleanup and triangulation safeguards.
- `Unparent All` and `Replace Object` keep world matrices intact, even if referenced data is removed mid-operation.
- Export a `model_default.skin` file tailored for Stormtrooper caps and player models.
- Select subsets (meshes, tags, caps) via the selection helper and maintain Ghoul2 property hygiene.
- Armature modifier calculator, empty vertex group remover, and origin/alignment helpers.

## Usage notes
- When replacing an object, transforms are preserved by capturing and restoring `matrix_world` copies.
- Always run **Set G2 Properties** before exporting or parenting so every mesh follows naming conventions.

## Contribution
Feel free to open issues or pull requests on the [GitHub repository](https://github.com/Mauii/skeleton_tool/) if you find regressions with Blender releases newer than 4.5.
