# Using the GIMP exporter for COA Tools 


## Installation

Simply copy the coatools_exporter.py into the GIMP plug-ins folder.

On Linux this is /home/YOU/.gimp2.8/plug-ins/
On Windows this is C:\Users\YOU\.gimp2.8\plug-ins
On OSX this is TODO! Not tested, but should work.

If the plug-in loaded correctly, you should find it under File>Export to CoaTools...


## Usage

Start by drawing a character or object using GIMP. Divide the movable parts up on different layers, like arms, legs, head and so on.

If you want to use multiple frames for one part, simply create a Layer Group, with one child layer for each frame. This can for instance be used to create different mouth shapes for animating dialog.

Choose a destination and name in the export dialog and hit OK.

Each visible layer will be exported to a a separate .png file. The child layers of a Layer Group are exported as a single sprite sheet to a .png file. In addition a writes out a .json file use by CoaTools to put everything back together agani in Blender.

Note that the exporter will overwrite previous exports without asking.


## Limitations

The script uses the Layer>Autocrop Layer function in GIMP to crop the layers down to the size of it's content, rather than looking at the actual Alpha channel of the layer. This will work fine in almost all cases, with a few exceptions. If your layer has a flat color all the way to edge of the image, such as a white border around an old style photograph, this color will be cropped. You can test this, by simply running Layer>Autocrop Layer on your image.

A workaround for this would be to add a 1 pixel transparent border around your layer, and that will get cropped instead, or just add slight noise to the layer.
