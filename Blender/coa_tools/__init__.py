'''
Copyright (C) 2015 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Cutout Animation Tools",
    "description": "This Addon provides a Toolset for a 2D Animation Workflow.",
    "author": "Andreas Esau",
    "version": (0, 1, 0, "Alpha"),
    "blender": (2, 75, 0),
    "location": "View 3D > Tools > Cutout Animation Tools",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Ndee Tools" }
    
    
import bpy
from bpy.app.handlers import persistent

# load and reload submodules
##################################    
    
from . import developer_utils
modules = developer_utils.setup_addon_modules(__path__, __name__)

from . ui import *
from . ui import preview_collections

# register
################################## 

import traceback

class ExampleAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_donate_icon = bpy.props.BoolProperty(name="Show Donate Icon",default=True)
    sprite_import_export_scale = bpy.props.FloatProperty(name="Sprite import/export scale",default=0.01)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_donate_icon")
        layout.prop(self,"sprite_import_export_scale")


def register():
    
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(__file__),"icons")
    pcoll.load("donate_icon", os.path.join(my_icons_dir,"donate_icon.png"),'IMAGE')
    pcoll.load("twitter_icon", os.path.join(my_icons_dir,"twitter_icon.png"),'IMAGE')
    
    preview_collections["main"] = pcoll    
    
    
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    bpy.types.Object.coa_anim_collections = bpy.props.CollectionProperty(type=AnimationCollections)
    bpy.types.Scene.coa_ticker = bpy.props.IntProperty()
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('view3d.move', 'MIDDLEMOUSE', 'PRESS')
        kmi.active = False  
    
    
def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()
    
    print("Unregistered {}".format(bl_info["name"]))
    bpy.context.window_manager.coa_running_modal = False    
    
@persistent
def update_sprites(dummy):
    bpy.context.scene.coa_ticker += 1
    try:
        for obj in bpy.context.visible_objects:
            if "sprite" in obj and obj.animation_data != None and obj.animation_data.action != None:
                update_uv(bpy.context,obj)
                set_alpha(obj,bpy.context)
    except:
        pass
    if bpy.context.scene.coa_ticker%3 == 0:
        bpy.context.scene.update()
bpy.app.handlers.frame_change_post.append(update_sprites)