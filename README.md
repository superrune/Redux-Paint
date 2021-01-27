![Illustration of Redux Paint on iPad](http://www.superrune.com/tools/images/reduxpaint_starwars.gif)

# Redux Paint

## Overview
 Redux Paint is a work in progress Commodore 64 pixel art application for the Apple iPad. It's written in Python, and runs inside [Pythonista](http://omz-software.com/pythonista/). While still incomplete, it is fully functional, and lets you paint and export artwork for the Commodore 64. Features have been added as I have needed them, so development is pretty much driven by my own wants and sensibilities.
 
 You can read more about why I made it, and see some sample images on [my website](http://www.superrune.com/tools/reduxpaint.php). 
 
## Features
* Interface similar to Deluxe Paint.
* Pixels are PAL aspect ratio for correct simulation of an actual CRT screen.
* PNG, Koala and PRG export.
* CRT emulated image can be exported to the Camera Roll.
* Configurable levels of Undo and Redo.
* Zoom mode.
* CRT emulated preview while drawing.
* Dark or light grids, with two levels of transparency.
* Color clash checker.
* Show chars with available colors.
* Custom importer with advanced conversion options.
* Protect single color or draw on single color.
 
## How to install
1. On Safari on your iPad, download the .zip from the Redux Paint Github repo.
2. Go into Files, move the zip from "iCloud Drive" -> "Downloads" to your "iCloud Drive" -> "Desktop".
3. Hold-select over the zip file and select "Uncompress".
4. You will get a folder named "Redux-Paint-master". Hold-select the folder and choose "Move".
5. Select your "iCloud Drive" -> "Pythonista 3" folder as the destination.
6. Close and reopen Pythonista (just in case).
7. You should find the "Redux-Paint-master" folder under "Script Library" -> "iCloud"
8. Click on the "redux_paint.py" file and run it.

## How to use Redux Paint
### The toolbar
![Toolbar image](http://www.superrune.com/tools/images/reduxpaint_toolbar.gif)

Here are a quick run-though of the icons, from left to right:

<img src="http://www.superrune.com/tools/images/reduxpaint_toolbar_brushes.gif" width="48" height="48"/> The icons on the far left are brush sizes. You have 1, 2 and 6 pixel brushes available. 'C' lets you fill an entire character (4x8 pixels).

<img src="/icons/tool_dots.png" width="24" height="24"/> - Dotted line drawing.

<img src="/icons/tool_lines.png" width="24" height="24"/> - Solid line drawing.

<img src="/icons/tool_dither_off.png" width="24" height="24"/> - Toggles different dither modes. Redux Paint can do checkerboard dither and line dithering.

<img src="/icons/tool_grid.png" width="24" height="24"/> - Toggles different grid states and colours.

<img src="/icons/tool_zoom.png" width="24" height="24"/> - Activates the zoom mode. Drag the zoom frame to pick an area to zoom into. Also exits the zoom mode.

<img src="/icons/tool_zoomlevel.png" width="24" height="24"/> - Toggles between different zoom levels.

<img src="/icons/tool_pan.png" width="24" height="24"/> - Pan tool, for use when you are zoomed in.

<img src="/icons/tool_preview.png" width="24" height="24"/> - Turns the CRT preview on and off, and toggles its size.

<img src="/icons/tool_preview_position.png" width="24" height="24"/> - Toggles the CRT preview position.

<img src="/icons/tool_selection.png" width="24" height="24"/> - Selects an area (not implemented).

<img src="/icons/tool_undo.png" width="48" height="24"/> - Undo one step.

<img src="/icons/tool_redo.png" width="48" height="24"/> - Redo one step.

<img src="/icons/tool_flipx.png" width="24" height="24"/> - Flips/mirrors the image horizontally.

<img src="/icons/tool_flipy.png" width="24" height="24"/> - Flips/mirrors the image vertically.

<img src="/icons/tool_offset_up.png" width="24" height="24"/> - Shifts the image one character (8 pixels) up.

<img src="/icons/tool_offset_down.png" width="24" height="24"/> - Shifts the image one character (8 pixels) down.

<img src="/icons/tool_offset_right.png" width="24" height="24"/> - Shifts the image one character (8 pixels) to the right.

<img src="/icons/tool_offset_left.png" width="24" height="24"/> - Shifts the image one character (8 pixels) to the left.

<img src="/icons/tool_file.png" width="48" height="24"/> - Opens the File Operations windows (see below).

<img src="/icons/tool_exit.png" width="48" height="24"/> - Exits Redux Paint.

<img src="/icons/tool_charinfo.png" width="24" height="24"/> - Toggles different colour info modes. First will examines the image for colour clashes, characters marked in red have too many colours. Two next modes will mark characters with two or one colour available. See the info text at the bottom of Redux Paint window for more information. Cycling this button will also turn off the colour info mode, which will slow down Redux Paint if kept active.

<img src="/icons/tool_palette_lock_off.png" width="24" height="24"/> - Locks the background colour selection, so that it cannot be changed. You can set the background colour by clicking a palette colour twice. This is easy to do by accident, so locking the background is good practice when you are checking colour clashes.

<img src="http://www.superrune.com/tools/images/reduxpaint_toolbar_colourbox.gif" width="48" height="32"/> Next is the active colour indicator. The box in the middle show the current colour, and the are around show the background colour. Setting the background colour is important when checking colour clashes and exporting the image to Koala or PRG. Pressing the active colour box will swap the foreground with the background. You can set the background colour by clicking a palette colour twice.

<img src="http://www.superrune.com/tools/images/reduxpaint_toolbar_palette.gif" width="128" height="32"/> After the current foreground and background colour are the Commodore 64 colours. Press a colour to make it the active drawing colour. You can set the background colour by clicking a palette colour twice.

<img src="/icons/tool_palette_numeric.png" width="48" height="24"/> - Pressing this button will sort the colours by their C64 numeric order, or ordered by their luminance values. The latter is good for making gradients.

<img src="/icons/tool_hold_off.png" width="48" height="24"/> - This button will lock or mask the background colour, either protecting if from drawing or letting you draw only on that colour. Using this function you can quickly, for example, paint over all the blue in the image. 


### The file operations window
<img src="http://www.superrune.com/tools/images/reduxpaint_fileoperations.gif" width="577" height="495"/>

Clicking the 'File" button on the toolbar opens the File Operations window. This window lets you **Load**, **Rename** and **Duplicate** existing images. It also lets you create a **New** image and **Delete** the selected image.

*A couple of buttons need some further explanation:*

**Import** - This button imports an image file from the iOS Files app. Most still image formats are supported. See the Import Window below for import options.

**Photos** - This button imports an image from the iOS Photo library. See the Import Window below for import options.

**Share** - This will share the current image on the canvas. The image will have a 1:1 pixel aspect, so it will not look like an actual C64 image, but this is the best format for exporting your image to work in another program.

**Share CRT** - This will save the CRT preview to your Camera Roll. This image will be in PAL aspect ratio and have scanlines and other CRT emulation effects.

**.koa** - This will share the current canvas as a C64 Koala Painter file. This is a very common file format on the C64, and should load in most C64 paint applications. Make sure that you have the correct background colour selected. The image will not export if there are any colour clashes present.

**.prg** - This will share the current canvas as a C64 PRG executable. This program will run on a C64 or emulator, and will display your image. Make sure that you have the correct background colour selected. The image will not export if there are any colour clashes present.

### The import window
<img src="http://www.superrune.com/tools/images/reduxpaint_convert.gif" width="680" height="545"/>

When importing an image file or a photo, this window will automatically appear. This window will let you tweak several settings to ensure you get the best possible import into Redux Paint. The sliders and buttons are not interactive, you need to press the rightmost image (the result) to see how your settings affect the converted image. Pressing **Import** loads the current image into the Redux Paint canvas.

You can click any colour in the palette row to exclude that colour from the conversion. The excluded colours are marked with an 'X'. Press the **R** button to reset all exclusions.

**CON** - This slider changes the contrast of the source image. Press the button to reset the slider.

**BRT** - This slider changes the image brightness. Press the button to reset the slider.

**SAT** - This slider changes the image saturation. The C64 has somewhat desaturated colours, I find reducing the saturation creates a more accurate conversion.

**Add Matrix** - This button changes the colour match method. I've decided to add multiple methods, and recommend you try the different ones and see how they behave on your image.

**Bayer** - This is the dither algorithm used. Try the different ones and see how they affect your image.

**Gamma Off** - This will do a gamma conversion before and after the image conversion process. **Gamma On** should be the mathematically correct option, but I find the conversion to look better with the **Gamma Off**. Try it out and see what you prefer.

**RGB** - This slider sets the range or size of the dithering. If you set the slider to the left, you can get a very small section of dither inbetween each solid colour. Press the button to reset the slider.

**Crop** - Clicking this button will swap between a cropped version or a full version (with black borders) of the image.

**Nearest** - The image needs to be scaled down to 160x240 pixels. Clicking this button will swap between an antialiased or nearest neighbor scaled version of the image.

**PAL Aspect** - This will turn on and off PAL image aspect at import. I would suggest leaving this on, since the main canvas is PAL ratio at the moment. I hope to support NTSC and square aspect at some point.


## Known issues
* There is no palm rejection, so be careful when you use the Apple Pencil to draw.
* Undo can on a rare occasion lead to a crash.
* Designed for an iPad. Works on phones, but screen layout it weird.
* Undo does not support image mirroring or offsetting.


