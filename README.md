# Skeleton Tool Add-on (Blender 5.2)

A Blender add-on that accelerates preparing models for Jedi Knight: Jedi Academy. It ships with helpers to set Ghoul2 properties, parent tags/caps, clean duplicates, export `.skin` definitions, and keep replaces synchronized without breaking world transforms.

## Compatibility
- Tested with Blender 5.2
- Not tested with Blender 4.5 or lower, feel free to give it a try.

## Installation
1. Copy the `skeleton_tool` folder into `Blender/<version>/scripts/addons/`.
2. Add a copy of a _humanoid.gla inside the addon's folder
3. Enable the add-on from **Edit > Preferences > Add-ons** by searching for _Skeleton Tool_.
4. Press `N` in the 3D Viewport and open the *Skeleton Tool* panel under the sidebar.

## Features
- Batch parenting/tagging for meshes, caps, and tags with automatic triangle cleanup and triangulation safeguards.
- Parenting checks all scene objects for a likely 10x scale error and scales matching objects down by 10 before reparenting.
- `Unparent All` and `Replace Object` keep world matrices intact, even if referenced data is removed mid-operation.
- Export a `model_default.skin` file tailored for Stormtrooper caps and player models.
- Select subsets (meshes, tags, caps) via the selection helper and maintain Ghoul2 property hygiene.
- Armature modifier calculator, empty vertex group remover, and origin/alignment helpers.
- Creates a model_root_0 and/or scene_root when none is present when needed.
- Imports a default _humanoid.gla if present in the addon's folder when needed.

## Usage notes
- When replacing an object, transforms are preserved by capturing and restoring `matrix_world` copies.
- Always run **Set G2 Properties** before exporting or parenting so every mesh follows naming conventions.
- The parenting scale recovery runs across the scene. It only changes objects whose largest dimension is over 10 meters and whose three scale components are all approximately 10; other large objects are left unchanged.

## Contribution
Feel free to open issues or pull requests on the [GitHub repository](https://github.com/Mauii/skeleton_tool/) if you find regressions with Blender releases newer than 4.5.

## Extra note
I used Copilot's agent in helping with certain refactors which otherwise might be taking too long to figure out myself. This goes only for the parenting section of the addon and executing a fine release.
