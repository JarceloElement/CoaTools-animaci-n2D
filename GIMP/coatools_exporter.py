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

from math import floor, sqrt, ceil
from gimpfu import *

class Sprite():
    # Store the data for a sprite.
    def __init__(self, name):
        self.name = name
        self.pos = [0,0,0]
        self.tilesize = [1,1]

    def info(self):
        print('Name: {name}'.format(name=self.name))
        print('Position: {pos}'.format(pos=self.pos))
        print('Tilesize: {tilesize}'.format(tilesize=self.tilesize))


def export_to_coatools(img, drw):
    # TODO! Make this whole operation one undo
    # Loop through visible layers
    sprites = {}
    for layer in img.layers:
        if layer.visible:
            if len(layer.children) > 0:
                minx, miny, maxx, maxy = 100000, 100000, 0, 0
                frames = 0
                for child in layer.children:
                    if len(child.children) > 0:
                        print("Nested layer groups not supported")
                        continue
                    pdb.plug_in_autocrop_layer(img, child)
                    frames = frames + 1
                    x1, y1 = child.offsets
                    x2 = child.width + x1
                    y2 = child.height + y1
                    if x1 < minx:
                        minx = x1
                    if y1 < miny:
                        miny = y1
                    if x2 > maxx:
                        maxx = x2
                    if y2 > maxy:
                        maxy = y2
                width = maxx - minx
                height = maxy - miny
                # Calculate optimal tiles and image size.
                gridx = floor(sqrt(frames))
                gridy = ceil(frames / gridx)
                img2 = gimp.Image(int(width * gridx), int(height * gridy))
                col = 1
                row = 1
                print('GRIDX {gridx}'.format(gridx=gridx))
                for child in layer.children:
                    print('COL {col}, ROW {row}'.format(col=col, row=row))
                    if len(child.children) > 0:
                        continue
                    if col % gridx > 0:
                        # TODO! Same as below, move copy/paste function out.
                        col = col + 1
                    else:
                        # Copy layer to col, row with correct offset
                        pdb.gimp_edit_copy(child)
                        tmplayer = img2.new_layer('{name}_{col}_{row})'.format(name=child.name, col=col, row=row),
                                                  width,
                                                  height)
                        floating_layer = pdb.gimp_edit_paste(tmplayer, True)
                        pdb.gimp_floating_sel_anchor(floating_layer)
                        # TODO! Position the pasted image correctly in the grid.
                        # Start in new row next loop
                        col = 1
                        row = row + 1
                pdb.gimp_display_new(img2)
            else:
                name = '{name}.png'.format(name=layer.name)
                print(name)
                pdb.gimp_image_set_active_layer(img, layer)
                # Find the layer position
                offset = layer.offsets
                width = layer.width / 2 + offset[0]
                height = layer.height / 2 + offset[1]
                pos = pdb.gimp_image_get_item_position(img, layer)
                sprites[name] = Sprite(name)
                sprites[name].pos = [width, pos, height]
                sprites[name].info()
                pdb.plug_in_autocrop_layer(img, layer)
                # Copy layer into new image and save it out
                pdb.gimp_edit_copy(layer)
                img2 = pdb.gimp_edit_paste_as_new()
                drw2 = pdb.gimp_image_active_drawable(img2)
                pdb.file_png_save2(img2,
                                   drw2,
                                   '/tmp/{layer}'.format(layer=name),
                                   name,
                                   False,
                                   9,
                                   False,
                                   False,
                                   False,
                                   False,
                                   False,
                                   1,
                                   True)
                pdb.gimp_image_delete(img2)


def show_error_msg( msg ):
    # Output error messages to the GIMP error console.
    origMsgHandler = pdb.gimp_message_get_handler()
    pdb.gimp_message_set_handler(ERROR_CONSOLE)
    pdb.gimp_message(msg)
    pdb.gimp_message_set_handler(origMsgHandler)


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
