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



### The file operations window
<img src="http://www.superrune.com/tools/images/reduxpaint_fileoperations.gif" width="577" height="495"/>


### The import window
<img src="http://www.superrune.com/tools/images/reduxpaint_convert.gif" width="680" height="545"/>


## Known issues
* There is no palm rejection, so be careful when you use the Apple Pencil to draw.
* Undo can on a rare occasion lead to a crash.
* Designed for an iPad. Works on phones, but screen layout it weird.
* Undo does not support image mirroring or offsetting.


