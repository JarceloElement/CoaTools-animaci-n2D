

# Cutout Animation Tools - Documentation
This is the Documentation for the Blender/Godot Addon Cutout Animation Tools.

If you like this addon and want to thank me with a small donation feel free to do this here:

[![](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=8TB6CNT9G8LEN)

## Description
The Cutout Animation Tools (COA Tools) Addon for blender is a 2D rigging and animation suite. It offers you similar tools as for example programs like Spine or Spriter. COA Tools offer you a rapid workflow to create 2D Cutout Character/Animations in blender. Thanks to blenders great animation system and and this addon you get a powerfull solution to create 2D animations. It is parted into 3 different components. Photoshop sprite exporter, Blender Addon, Godot importer.

### Photoshop sprite exporter
Quickly export photoshop layers into separate files with json coordinate informations. This can be used in blender to import sprites very quickly.
Features:
- export layers as sprites
- export folder with multiple layers as spritesheets
- generate json data with all layer positions and spritesheet informations

### Cutout Animation Tools Blender
This is the biggest component, as most of the work will be done here.
Features the addon offers are:
- sprite importer (import single sprites or multiple, or use json data as import information)
- animated spritesheet support for meshes
- armature editing - superfast bone creation tool. Just draw bones and click append sprites to bones
- mesh editing - draw vertex countours and fill them quickly with tesselated mesh. filling also unwraps and maps texture data
- weight editing - fast weight editing for tesselated meshes
- fast ik and stretch to constraint generation 
- enhanced animation handling for sprite_objects
- Spriteobject outliner -> displays all containing sprites, armatures with bones for better and quick access to single sprites
- ortho cam operator -> generates an orthogonal camera which can be used to render animations. Camera resolution fits perfectly the pixel space of sprites
- json export - > Exports all sprite_object data to a json file. Supported features are: Bone and Sprite hierarchy export. Baked animation export

### Godot Cutout Animation Importer
This is an advanced importer that helps you get all your exported blender data into godot.
Features:
- Json importer
- sprites, bones and animations get imported
- clever reimport functionality. Offers the possibility to merge local changes that were made in godot to the newly imported scene. This enables a very flexible workflow. Work in blender, then export. Import in godot. Make additions like adding new nodes, adding custom animations. After reimport all local changes will be preserved if merging is enabled.
