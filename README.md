![Illustration of Redux Paint on iPad](http://www.superrune.com/tools/images/reduxpaint_starwars.gif)

# Redux Paint

## Overview
 Redux Paint is a work in progress Commodore 64 pixel art application for the Apple iPad. It's written in Python, and runs inside [Pythonista](http://omz-software.com/pythonista/). While still incomplete, it is fully functional, and lets you paint and export artwork for the Commodore 64. I add features when I miss them, so development is pretty much driven by my own needs and sensibilities.
 
 You can read more about why I made it, and see some sample images on [my website](http://www.superrune.com/tools/reduxpaint.php). 
 
## Features
* Interface similar to Deluxe Paint.
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

The icons on the far left are brush sizes. You have 1, 2 and 6 pixel brushes available. 'C' lets you fill an entire character (4x8 pixels).

<img src="/icons/tool_dots.png" width="24" height="24"/> - Dotted line drawing.

<img src="/icons/tool_lines.png" width="24" height="24"/> - Solid line drawing.

<img src="/icons/tool_dither_off.png" width="24" height="24"/> - Toggles different dither modes.

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

Next is the active colour swatch. The box in the middle show the current colour, and the border show the background colour. Setting the background colour is important when checking colour clashes and exporting the image to Koala or PRG. Pressing the active colour swatch will swap the foreground with the background. You can set the background colour by clicking a palette colour twice.

After the current foreground and background colour are the Commodore 64 colours. Press a colour to make it the active drawing colour. You can set the background colour by clicking a palette colour twice.

<img src="/icons/tool_palette_numeric.png" width="48" height="24"/> - Pressing this button will sort the colours by their C64 numeric order, or ordered by their luminance values. The latter is good for making gradients.

<img src="/icons/tool_hold_off.png" width="48" height="24"/> - This button will lock or mask the background colour, either protecting if from drawing or letting you draw only on that colour. Using this function you can quickly, for example, paint over all the blue in the image. 


### The file operations window
<img src="http://www.superrune.com/tools/images/reduxpaint_fileoperations.gif" width="577" height="495"/>


### The import window
<img src="http://www.superrune.com/tools/images/reduxpaint_convert.gif" width="680" height="545"/>


## Known issues
* There is no palm rejection, so be careful when you use the Apple Pencil to draw.
* Undo can on a rare occasion lead to a crash.
* Designed for an iPad. Works on phones, but screen layout it weird.
* Undo does not support image mirroring or offsetting.


