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
import json
from math import floor, sqrt, ceil
from gimpfu import *


class Sprite():
    # Store the data for a sprite.
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
            "pivot_offset": [0.0, 0.0],
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


    def paste_layer(self, img, name, x, y):
        ''' Paste a layer with offset '''
        layer = img.new_layer(name,
                                 img.width,
                                 img.height)
        floating_layer = pdb.gimp_edit_paste(layer, True)
        pdb.gimp_floating_sel_anchor(floating_layer)
        print(img)
        print(layer)
        pdb.plug_in_autocrop_layer(img, layer)
        print('Offset: {x}, {y}'.format(x=x, y=y))
        pdb.gimp_layer_set_offsets(layer, x, y)
        
    def export_sprite(self, layer):
        ''' Crop and export layer to png '''
        name = '{name}.png'.format(name=layer.name)
        print(name)
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
        # TODO! Get destination path from user save dialog.
        path = '/tmp/{name}'.format(name=name)
        self.save_png(imgtmp, path)
        pdb.gimp_image_delete(imgtmp)
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
        print('Layer Group: {x}, {y}'.format(x=layer.width, y=layer.height))
        img2 = gimp.Image(int(layer.width * gridx), int(layer.height * gridy))
        # TODO! Remove this after debugging is done.
        #pdb.gimp_display_new(img2)
        col = 1
        row = 1
        print('GRID: {x}, {y}'.format(x=gridx, y=gridy))
        name = '{name}.png'.format(name = layer.name)
        for child in layer.children:
            print('COL {col}, ROW {row}'.format(col=col, row=row))
            if len(child.children) > 0:
                print("Nested layer groups not supported, skipping layer")
                continue
            pdb.gimp_image_set_active_layer(self.img, child)
            pdb.plug_in_autocrop_layer(self.img, child)
            # TODO! The offset is a bit off.
            x_delta = child.offsets[0] - layer.offsets[0]
            y_delta = child.offsets[1] - layer.offsets[1]
            print('Offsets Delta: {x}, {y}'.format(x=x_delta, y=y_delta))
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
        flat_layer = pdb.gimp_image_merge_visible_layers(img2, 0)
        # TODO! Get destination path from user save dialog.
        path = '/tmp/{name}.png'.format(name=layer.name)
        self.save_png(img2, path)
        pdb.gimp_image_delete(img2)
        # Store data about the sprite
        sprite = Sprite(name)
        sprite.position = [width, pos, height]
        sprite.resource_path = path
        sprite.tiles_x = int(gridx)
        sprite.tiles_y = int(gridy)
        sprite.frame_index = int(frames)
        return sprite
        

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
        # TODO! Make this whole operation one undo
        # Loop through visible layers
        sprites = {}
        for layer in self.img.layers:
            if layer.visible:
                if len(layer.children) < 1:
                    self.sprites.append(self.export_sprite(layer))
                else:
                    self.sprites.append(self.export_sprite_sheet(layer))
        for sprite in self.sprites:
            print(json.dumps(sprite.get_data(),
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': '))
            )



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
"pivot_offset": [0.0,0.0],
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
