#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# CoaTools Exporter
#  by Ragnar Brynjúlfsson
#
# DESCRIPTION
#   CoaTools Exporter is a plug-in for GIMP to export layered cut-out animation
#   characters to CoaTools: 2D Animation tools for Blender 
#   (see https://github.com/ndee85/coa_tools)
#
# INSTALLATION
#   Drop the script in your plug-ins folder. On Linux this is ~/.gimp-2.8/plug-ins/
#
# VERSION
version = "0.0.0"
# AUTHOR 
author = [ 'Ragnar Brynjúlfsson <me@ragnarb.com>', ' ']
# COPYRIGHT
copyright = "Copyright 2016 © Ragnar Brynjúlfsson"
# WEBSITE
website = "https://github.com/ndee85/coa_tools"
plugin = "CoaTools Exporter"
# LICENSE
license = """
CoaTools Exporter
Copyright 2011-2014 Ragnar Brynjúlfsson

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
"""

import os
import gtk
import json
from math import floor, sqrt, ceil
from gimpfu import *


class Sprite():
    ''' Store file and transform data for each sprite '''
    
    def __init__(self, name):
        self.name = name
        self.path = ''
        self.position = [0,0,0]
        self.z = 0
        self.tiles_x = 1
        self.tiles_y = 1
        self.frame = 1

    def get_data(self):
        ''' Return sprite info as json encodable data '''
        data = {
            "name": self.name,
            "type": "SPRITE",
            "resource_path": self.path,
            "offset": [0.0, 0.0],
            "position": self.position,
            "rotation": 0.0,
            "scale": [1.0, 1.0],
            "opacity": 1.0,
            "z": self.z,
            "tiles_x": self.tiles_x,
            "tiles_y": self.tiles_y,
            "frame_index": self.frame,
            "children": []
        }
        return data
            

class CoaExport():
    def __init__(self, img):
        self.img = img
        self.sprites = []
        # TODO! Open file chooser dialog to choose name and destination
        self.name = os.path.splitext(os.path.basename(self.img.filename))[0]
        self.path = os.path.dirname(self.img.filename)
        self.dest_dir = '{path}/{name}'.format(path = self.path, name = self.name)
        self.dest_json = '{path}/{name}.json'.format(path = self.dest_dir, name = self.name)

    def paste_layer(self, img, name, x, y):
        ''' Paste a layer with offset '''
        layer = img.new_layer(name,
                                 img.width,
                                 img.height)
        floating_layer = pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_anchor(floating_layer)
        pdb.plug_in_autocrop_layer(img, layer)
        pdb.gimp_layer_set_offsets(layer, x, y)
        
    def export_sprite(self, layer):
        ''' Crop and export layer to png '''
        name = '{name}.png'.format(name=layer.name)
        pdb.gimp_image_set_active_layer(self.img, layer)
        # Find the layer position
        offset = layer.offsets
        width = layer.width / 2 + offset[0]
        height = layer.height / 2 + offset[1]
        pos = pdb.gimp_image_get_item_position(self.img, layer)
        pdb.plug_in_autocrop_layer(self.img, layer)
        # Copy layer into new image and save it out
        pdb.gimp_edit_copy(layer)
        imgtmp = pdb.gimp_edit_paste_as_new()
        path = '{path}/{name}'.format(path=self.dest_dir, name=name)
        self.save_png(imgtmp, path)
        pdb.gimp_image_delete(imgtmp)
        # Return sprite object with relevant data
        sprite = Sprite(name)
        sprite.position = [width, pos, height]
        sprite.resource_path = path
        return sprite

    def export_sprite_sheet(self, layer):
        ''' Export a sprite sheet from a layer group '''
        # Find the layer position
        offset = layer.offsets
        width = layer.width / 2 + offset[0]
        height = layer.height / 2 + offset[1]
        pos = pdb.gimp_image_get_item_position(self.img, layer)
        # Find grid size
        frames = len(layer.children)
        gridx = floor(sqrt(frames))
        gridy = ceil(frames / gridx)
        # TODO! Replace autocrop with a custom function that only crops transparent areas.
        pdb.plug_in_autocrop_layer(self.img, layer)
        img2 = gimp.Image(int(layer.width * gridx), int(layer.height * gridy))
        col = 1
        row = 1
        name = '{name}.png'.format(name = layer.name)
        # Looop through child layers in the layer group
        for child in layer.children:
            if len(child.children) > 0:
                # TODO! Verify that this actually works.
                show_error_msg('Nested layer groups not supported, skipping "{layer}"'.format(layer=child))
                frames = frames - 1
                continue
            pdb.gimp_image_set_active_layer(self.img, child)
            pdb.plug_in_autocrop_layer(self.img, child)
            x_delta = child.offsets[0] - layer.offsets[0]
            y_delta = child.offsets[1] - layer.offsets[1]
            pdb.gimp_edit_copy(child)
            self.paste_layer(img2,
                             '{name}_{col}_{row}'.format(name=child.name, col=col, row=row),
                             (layer.width * (col - 1)) + x_delta,
                             (layer.height * (row - 1)) + y_delta)
            if col % gridx > 0:
                col = col + 1
            else:
                col = 1
                row = row + 1
        # Flatten and save
        flat_layer = pdb.gimp_image_merge_visible_layers(img2, 0)
        path = '{path}/{name}'.format(path=self.dest_dir, name=name)
        self.save_png(img2, path)
        pdb.gimp_image_delete(img2)
        # Return sprite object with relevant data
        sprite = Sprite(name)
        sprite.position = [width, pos, height]
        sprite.resource_path = path
        sprite.tiles_x = int(gridx)
        sprite.tiles_y = int(gridy)
        sprite.frame_index = int(frames)
        return sprite
        

    def mkdir(self):
        ''' Make a destination dir for the sprites and json file '''
        try:
            if not os.path.isdir(self.dest_dir):
                os.makedirs(self.dest_dir)
        except Exception, err:
            show_error_msg(err)


    def save_png(self, img, path):
        ''' Save img to path as png '''
        drw = pdb.gimp_image_active_drawable(img)
        pdb.file_png_save2(img,
                           drw,
                           path,
                           os.path.basename(path),
                           False,
                           9,
                           False,
                           False,
                           False,
                           False,
                           False,
                           1,
                           True)

        
    def export(self):
        ''' Export visible layers and layer groups to CoaSprite '''
        # TODO! Make this whole operation one undo
        # Loop through visible layers
        self.mkdir()
        for layer in self.img.layers:
            if layer.visible:
                
                if len(layer.children) < 1:
                    self.sprites.append(self.export_sprite(layer))
                else:
                    self.sprites.append(self.export_sprite_sheet(layer))
        self.write_json()

    def write_json(self):
        ''' Write out the json config for the character '''
        sprites = []
        for sprite in self.sprites:
            sprites.append(sprite.get_data())
        data = { "name": self.name, "nodes": sprites }
        json_data = json.dumps(data,
                   sort_keys=True,
                   indent=4, separators=(',', ': '))
        sprite_file = open(self.dest_json, "w")
        sprite_file.write(json_data)
        sprite_file.close()
        

def show_error_msg( msg ):
    # Output error messages to the GIMP error console.
    origMsgHandler = pdb.gimp_message_get_handler()
    pdb.gimp_message_set_handler(ERROR_CONSOLE)
    pdb.gimp_message(msg)
    pdb.gimp_message_set_handler(origMsgHandler)

def export_to_coatools(img, drw):
    export = CoaExport(img)
    export.export()
    

register(
    "python_fu_coatools",
    "Tool for exporting layered cut-out animation characters to CoaTools for Blender.",
    "GNU GPL v3 or later.",
    "Ragnar Brynjúlfsson",
    "Ragnar Brynjúlfsson",
    "March 2016",
    "<Image>/Filters/Animation/Export to CoaTools...",
    "RGB*, GRAY*, INDEXED*",
    [
    ],
    [],
    export_to_coatools
)


main()

'''
# Proposed file format
{
"name": "ObjectName",
"nodes": [
{
"name": "layer_name.png",
"type": "SPRITE",
"node_path": "layer_name.png",
"resource_path": "sprites/layer_name.png",
"pivot_offset": [0.0,0.0], # TODO! In the Blender code, this key is "offset" not "pivot_offset". Check that my repos is up to date.
"position": [0.0,0.0],
"rotation": 0.0,
"scale": [1.0,1.0],
"opacity": 1.0,
"z": 0,
"tiles_x": 1,
"tiles_y": 1,
"frame_index": 0,
"children": []
},
...,
...
]
}
'''
