#!python3

# Redux Paint AKA Pythonista C64 Painter AKA Python learning exercise gone rogue
#
# Rune Spaans 2017-2023
#
# Bringest ye holy handgrenades, here be monstrous code and vicious rabbits!
# Some code based on Pythonista Pixel Editor by Sebastian Jarsve
#
#
# Features Todo:
# - Select a rectangular area. Flip and offset content.
# - Save UI options inbetween sessions (brush type, ordered palette, bglock, bgcolor etc).
#   - Use built in Python ini file module?
# - Palm reject option - is that possible in Pythonista?
# - Copy/paste a selection.
# - Import Koala image.
# - Auto-correct clashes when exporting to Koala or PRG. Clash preview?
#
# Fixes/Bugs Todo:
# - Disable draw while file and import windows are open.
# -- Don't exit after exporting.
# - Undoing stroke that goes off-canvas puts a new pixel on the last pixel when painting again.
# - Improve layouts on other devices and orientations.
# - Keep an image changed variable, only autosave when this is tagged? A little quicker than current solution.
# - Optimize draw line, several alternatives to consider.
# - Undo:
# 	- Clear undo stack on new image.
# 	- Undoing first stroke does not work.
# 	- Include mirror and offset operations in undo stack.
# - Add some kind of progress indicator when doing longer redraws, loads and saves.
# - Zoom function sometimes ends by drawing a pixel. Figure out why.
# - Error on exit if there is no image. 'has_image' function fails.
# - Can the preview window be draggable?
# - Code changes have resulted in duplicate and unused functions, go through and clean up.


# Pythonista-specific imports
import clipboard
import console
from dialogs import share_image, pick_document
import photos
import scene
import ui


# Library imports
import copy
from PIL import Image
import ImageChops
import ImageOps
import ImageFilter
import numpy

from io import BytesIO
from os.path import isfile, isdir, getctime, basename, exists, splitext
from os import mkdir, listdir, remove, rename
from time import time, sleep
from datetime import datetime
from glob import iglob, glob
from shutil import copy2, copytree, rmtree


# Redux Paint imports
from include.redux_functions import *
from include.redux_settings import Settings
from include.redux_file import FileWindow
#from redux_file import FileWindow



# The Pixel, an array of these holds the current image
class Pixel (object):
	def __init__(self, x, y, w, h):
		self.rect = scene.Rect(x, y, w, h)  # Important: (x,y) position is the lower-left corner of the pixel
		self.color = (0, 0, 0, 1)
		self.index = 0                      # Used to find neighbors
		self.position = (x, y)              # Used when writing images
		
		
class PixelEditor(ui.View):
	# Editor variables
	imageName = ""
	brushSize = 1 		# 1: 1x1 pixel, 2: 1x2 pixels, 6: 2x3 pixels, c: character (4x8 pixels)
	brushArrays = {1: numpy.array([0]), 2: numpy.array([-160,0]), 6: numpy.array([-321,-320,-161,-160,-1,0])}
	brushMinDist = {1:2, 2:2, 6:3}
	toolMode = 'lines'
	prevMode = 'lines' 	# The previous tool
	drawDithered = 0  	# 0:off, 1:dithered drawing, 2:inverse dither, 3:stripe dither, 4:inverse stripe dither
	prevPixel = []
	colorMask = 0 		# 0: off, 1: draw only on bg color, 2:dont draw on bg color
	bgColorLock = False
	hasChanges = False
	colorCheckState = 0 # 0: off, 1: red for illegal characters, 2: green for 1 available colour, 3: orange for 2 available colours
	
	# Preview window
	previewMode = 1  	# 0:off, 1:normal size, 2:double size
	previewPos = 0 		# 0:lower left, 1:lower right
	
	# Grid variables
	gridOpacity = 0.5
	darkGrid = False
	
	# Zoom variables
	zoomLevels = (2, 3, 6, 9)
	zoomCurrent = 1  # What level we're currently zooming to
	zoomState = False
	panStart = [0,0]
	panDistance = [0,0]
	
	# Last autosave and undo time
	lastSave = 0
	lastUndo = 0
	
	# Undo steps are kept in a list composed like this:
	# {stroke color dictionary}, (stroke pixels set), stroke color
	undoData = [[dict(), set(), None] for u in range(Settings.undoSteps) ]
	currentUndoStep = 0
	
	def layout(self):
		# This function will update the Redux Paint layout when the screen size is changed
		# Todo: Find a way to update the file window
		
		screenWidth, screenHeight = int(self.superview.width), int(self.superview.height)
		#screenWidth, screenHeight = ui.get_screen_size()
		print('Screen size changed do x:'+str(screenWidth) + ' y:'+str(screenHeight))
		colorbar = self.superview['colors']
		toolbar = self.superview['toolbar']
		
		toolbarWidth = 448
		toolbarHeight = 64
		toolbarPad = 64
		
		# This part is only for the toolbars
		if screenWidth >= toolbarWidth*2 + toolbarPad*2 or screenWidth > screenHeight:
			# Screen is larger than or equal to maximum
			print('Toolbars are max width')
			sidePad = (screenWidth-(toolbarWidth*2))*0.5
			toolbar.transform = ui.Transform.scale(1.0,1.0)
			colorbar.transform = ui.Transform.scale(1.0,1.0)
			toolbar.x = sidePad
			toolbar.y = toolbarPad/2
			colorbar.x = sidePad+toolbarWidth
			colorbar.y = toolbarPad/2
			self.y = toolbar.height + toolbarPad*0.5
			
		elif screenWidth < (self.x*2)+toolbarWidth:
			# Screen is smaller than toolbar width + padding
			print('Toolbars are double height, scaled down')
			newScale = screenWidth / ((self.x*2)+toolbarWidth)
			toolbar.transform = ui.Transform.scale(newScale, newScale)
			colorbar.transform = ui.Transform.scale(newScale, newScale)
			toolbar.x = colorbar.x = (screenWidth-toolbar.frame[2])/2
			toolbar.y = toolbarPad/2
			colorbar.y = toolbarPad/2 + toolbar.frame[3]
			self.y = toolbar.frame[3]*2 + toolbarPad/2
			
		else:
			# Screen is smaller than maximum
			print('Toolbars are double height')
			toolbar.transform = ui.Transform.scale(1.0,1.0)
			colorbar.transform = ui.Transform.scale(1.0,1.0)
			sidePad = (screenWidth-toolbarWidth)*0.5
			toolbar.x = colorbar.x = sidePad
			toolbar.y = toolbarPad/2
			colorbar.y = toolbarPad/2 + toolbarHeight
			self.y = toolbarHeight*2 + toolbarPad*0.5
			
		#self.draw_grid_image()
		#self.image_view = self.create_image_view()
		
		# Paint editor positioning
		#self.transform = ui.Transform.scale(0.7,0.7)
		self.height = self.width * Settings.height / Settings.widthPAL
		self.position_pixels()
		self.image_view.width, self.image_view.height = self.frame.width, self.frame.height
		self.grid_layout.width, self.grid_layout.height = self.frame.width, self.frame.height
		self.color_check.width, self.color_check.height = self.frame.width, self.frame.height
		self.y = + colorbar.y + colorbar.height + toolbarPad/8
		
		# Preview image position
		self.superview['preview'].y = self.superview.height - (Settings.height * self.previewMode)
		
		#self.redraw_canvas()
		
		# Debug line positioning
		debugtext = self.superview['debugtext']
		debugtext.width = screenWidth - self.x*2
		debugtext.x = self.x
		debugtext.y = self.y + self.height # + toolbarPad/4
		fontsize = 18 #screenWidth*0.017578125
		if screenWidth < 640:
			fontsize = 12
		debugtext.font = ('Courier', fontsize)
		
		self.redraw_canvas()
		
		return True
		
	def debug_undo_stack(self):
		undoNum = 0
		print ("Undo Data:")
		for undos in self.undoData:
			undoString = "num:" + str(undoNum) + ", "
			undoString += "colorDict:" + str(type(undos[0])) + " "
			undoString += "length:" + str(len(undos[0])) + ", "
			undoString += "strokeSet:" + str(type(undos[1])) + " "
			undoString += "length:" + str(len(undos[1])) + ", "
			undoString += "color:" + str(undos[2])
			print (undoString)
			undoNum += 1
		return True
		
	# Shift stack downwards. Wiping the oldest step, making place for a new step.
	def pop_undo_stack(self):
		self.currentUndoStep -= 1
		del self.undoData[0]
		self.undoData.append([dict(), set(), None])
		
	def wipe_undo_stack(self):
		self.undoData = [[dict(), set(), None] for u in range(Settings.undoSteps) ]
		return True
		
	def wipe_undo_step(self, num):
		self.undoData[num] = [dict(), set(), None]
		return True
		
	# Adds data to the stack. Purges the oldest data.
	def next_undo_step(self):
		# Dont move to a new undo step if the current one is empty
		if len(self.undoData[self.currentUndoStep][1]) > 0:
			self.undoData[self.currentUndoStep][2] = (self.current_color[0], self.current_color[1], self.current_color[2])
			self.superview['debugtext'].text += " undoStep:" + str(self.currentUndoStep)
			self.currentUndoStep += 1
			# We have filled the undo stack. Delete the first entry.
			if self.currentUndoStep == Settings.undoSteps:
				self.pop_undo_stack()
			# Erase unda data on current step
			self.undoData[self.currentUndoStep] = [dict(), set(), None]
			#self.debug_undo_stack()
		return True
		
	def store_undo_stroke(self, pixelID):
		# This is called for every pixel as you paint. Needs to be extremely efficient
		if pixelID not in self.undoData[self.currentUndoStep][1]:
			self.undoData[self.currentUndoStep][1].add(pixelID)
			self.undoData[self.currentUndoStep][0][pixelID] = self.pixels[pixelID].color
			
	def fetch_undo_step(self):
		if self.currentUndoStep > 0:
			# Preview image is fetched from Image data, pixels are drawn from Stroke Set
			self.currentUndoStep -= 1
			for i in self.undoData[self.currentUndoStep][1]:
				#self.pixels[i].color = (1,0,0,1)
				self.pixels[i].color = self.undoData[self.currentUndoStep][0][i]
			# Redraw main and preview image
			self.image_view.image = self.draw_index_array(self.image_view.image, self.undoData[self.currentUndoStep][1], noCheck=True)
			self.preview_drawPixels()
			self.superview['debugtext'].text = "Fetched undo step " + str(self.currentUndoStep) + ". "
		else:
			self.superview['debugtext'].text = "No undo steps in memory."
		return True
		
	def fetch_redo_step(self):
		if self.currentUndoStep < Settings.undoSteps-1:
			if len(self.undoData[self.currentUndoStep][1]) > 0:
				for i in self.undoData[self.currentUndoStep][1]:
					self.pixels[i].color = self.undoData[self.currentUndoStep][2]
				# Redraw main and preview image
				self.image_view.image = self.draw_index_array(self.image_view.image, self.undoData[self.currentUndoStep][1], noCheck=True)
				self.preview_drawPixels()
				self.superview['debugtext'].text = "Fetched redo step " + str(self.currentUndoStep) + ". "
				self.currentUndoStep += 1
			else:
				self.superview['debugtext'].text = "No redo data on step " + str(self.currentUndoStep) + ". "
			str(len(self.undoData[self.currentUndoStep][1]))
		return True
		
	# Initialize editor
	def did_load(self):
		self.row = Settings.width/Settings.pixelSize
		self.column = Settings.height
		self.lastSave = int(time())
		self.pixels = []
		self.unfilteredPreview = self.create_new_image()
		self.image_view = self.create_image_view()
		self.grid_layout = self.init_draw_image()
		self.grid_layout.image = self.draw_grid_image()
		self.color_check = self.create_image_view()
		self.crt_overlay = self.create_crt_overlay()
		self.color_check.hidden = True
		self.image_view.image = self.create_new_image()  # Needs to be set twice for some reason..
		self.zoom_frame = self.create_zoom_frame()
		self.grid_layout.alpha = self.gridOpacity
		self.current_color = (1, 1, 1, 1)
		self.background_color = (0,0,0)
		self.wipe_undo_stack()
		
	def check_dither(self, position):
		# Coordinate method: (x+y)&1
		# Index method: (int(index/320)^index)&1
		if self.drawDithered == 0: return True
		if self.drawDithered == 1:
			return (position[0]+position[1])&1
		if self.drawDithered == 2:
			return 1-(position[0]+position[1])&1
		if self.drawDithered == 3:
			return 1-(position[1]&1)
		if self.drawDithered == 4:
			return position[1]&1
		else: return True
		
	def check_mask(self, pixel):
		# 0: off, 1: draw only on bg color, 2:dont draw on bg color
		if self.colorMask == 0:
			return True
		if (self.colorMask == 1 and pixel.color[:3] == self.background_color[:3]) or (self.colorMask == 2 and pixel.color[:3] != self.background_color[:3]):
			return True
		return False
		
	# Check if image is not all black
	def has_image(self):
		im = ui_to_pil(self.image_view.image)
		extrema = im.convert("L").getextrema()
		if extrema == (0, 0):
			# all black
			return False
		else:
			return True
			
	def create_zoom_frame(self):
		zoomWidth = self.width / self.zoomLevels[self.zoomCurrent]
		zoomHeight = self.height / self.zoomLevels[self.zoomCurrent]
		
		# create an movable image showing the zoom area
		with ui.ImageContext(320,200) as ctx:
			ui.set_color('black')
			line_inside = ui.Path.rect(2,2,316,196)
			line_inside.line_width = 4
			line_inside.stroke()
			ui.set_color('white')
			line_outside = ui.Path.rect(0,0,320,200)
			line_outside.line_width = 4
			line_outside.stroke()
			zoomSquare = ctx.get_image()
		zoom_frame = ui.ImageView(hidden=True)
		zoom_frame.bounds = (0,0,zoomWidth,zoomHeight)
		zoom_frame.center = (self.width/2, self.height/2)
		zoom_frame.image = zoomSquare
		self.add_subview(zoom_frame)
		return zoom_frame
		
	def get_zoom_center(self):
		return (self.superview['editor'].zoom_frame.center)
		
	# Todo: Bugs out at zoom level 2!
	def limit_zoom_center(self, position):
		borderWidth = self.superview['editor'].width / self.zoomLevels[self.zoomCurrent] * 0.5
		borderHeight = self.superview['editor'].height / self.zoomLevels[self.zoomCurrent] * 0.5
		xPos = min(max(borderWidth, position[0]), self.superview['editor'].width-borderWidth)
		yPos = min(max(borderHeight, position[1]), self.superview['editor'].height-borderHeight)
		self.superview['editor'].zoom_frame.center = (xPos, yPos)
		return (xPos, yPos)
		
	def set_zoom_size(self):
		zoomWidth = self.width / self.zoomLevels[self.zoomCurrent]
		zoomHeight = self.height / self.zoomLevels[self.zoomCurrent]		
		self.superview['editor'].zoom_frame.width = zoomWidth
		self.superview['editor'].zoom_frame.height = zoomHeight
		
	def set_image(self, image=None):
		# Image is set to provided image or a new is created
		image = image or self.create_new_image()
		self.image_view.image = image
		
	def get_image(self):
		image = self.image_view.image
		return image
		
	# Initializes the image, draws the pixel array, image and grid lines
	def init_pixel_grid(self):
		scale = self.height/self.column #self.width/self.row if self.row > self.column else self.height/self.column
		with ui.ImageContext(int(self.frame[2]),int(self.frame[3])) as ctx:
			for y in range(self.column):
				for x in range(int(self.row)):
					# Fills image with pixels
					# Changing this changes the pixel aspect
					#Pixel(x, y, w, h)  where (x,y) is the lower-left corner
					pixel = Pixel(x*scale*2*Settings.aspectPAL, y*scale, scale*2*Settings.aspectPAL, scale)
					pixel.index = len(self.pixels)
					pixel.position = (x,y)
					self.pixels.append(pixel) #Adds this pixel to the pixels list
		return ctx.get_image()
		
	# Draw the pixel and character grid
	# This function is pretty slow. Find a way to speed it up.
	def draw_grid_image(self):
		(startPos, endPos) = self.get_current_region()
		# Todo: check aspect here
		#yPixelScale = self.width/(endPos[0]-startPos[0]+1)/Settings.pixelSize #self.height/Settings.height
		yPixelScale = (self.width/Settings.aspectPAL)/(endPos[0]-startPos[0]+1)/Settings.pixelSize #self.height/Settings.height
		xPixelScale = yPixelScale * 2 * Settings.aspectPAL
		charSize = Settings.charSize
		charScale = yPixelScale*charSize
		#xRangeStart = int(startPos[0]/charSize*charSize)
		
		# Set our grid objects the same size as the paint canvas
		pixelGrid = ui.Path.rect(0, 0, self.frame[2], self.frame[3])
		characterGrid = ui.Path.rect(0, 0, self.frame[2], self.frame[3])
		
		charDrawColor = (1,1,1,0.5) if self.darkGrid == False else (0,0,0,0.5)
		lineDrawColor = (0.5,0.5,0.5,0.5) if self.darkGrid == False else (0.25,0.25,0.25,0.5)
		
		with ui.ImageContext(self.frame[2], self.frame[3]) as ctx:
			# Fills entire grid with empty color
			ui.set_color((0, 0, 0, 0))
			#pixelGrid.fill()
			pixelGrid.line_width = 1
			
			# Horizontal gridlines
			yEnd = 200 * yPixelScale
			for x in range(int(startPos[0]+1), int(endPos[0]+1)):
				xPos = (x-startPos[0]) * xPixelScale
				if x%4 != 0:
					pixelGrid.move_to(xPos,0)
					pixelGrid.line_to(xPos,yEnd)
				else:
					characterGrid.move_to(xPos,0)
					characterGrid.line_to(xPos,yEnd)
					
			# Vertical gridlines
			xEnd = 160 * xPixelScale
			for y in range(startPos[1]+1, endPos[1]+1):
				yPos = (y-startPos[1]) * yPixelScale
				if y%8 != 0:
					pixelGrid.move_to(0, yPos)
					pixelGrid.line_to(xEnd, yPos)
				else:
					characterGrid.move_to(0, yPos)
					characterGrid.line_to(xEnd, yPos)
					
			ui.set_color(lineDrawColor)
			pixelGrid.stroke()
			ui.set_color(charDrawColor)
			characterGrid.stroke()
			
			return ctx.get_image()
			
			
	def create_new_image(self):
		path = ui.Path.rect(*self.bounds)
		with ui.ImageContext(self.width, self.height) as ctx:
			ui.set_color((0, 0, 0, 0))
			path.fill()
			return ctx.get_image()
			
	def init_draw_image(self):
		image_view = ui.ImageView(frame=self.bounds)
		image_view.image = self.init_pixel_grid()
		self.add_subview(image_view)
		return image_view
		
	def create_image_view(self):
		image_view = ui.ImageView(frame=self.bounds)
		image_view.image = self.create_new_image()
		self.add_subview(image_view)
		return image_view
		
	# Returns the currently zoomed region as x,y coordinates. 0-based
	def get_zoom_region(self):
		zoomCenter = self.zoom_frame.center
		xCenter = Settings.actualWidth / self.image_view.width * self.zoom_frame.center[0]
		yCenter = Settings.height / self.image_view.height * self.zoom_frame.center[1]
		zoomWidth = Settings.actualWidth / self.zoomLevels[self.zoomCurrent]
		zoomHeight = Settings.height / self.zoomLevels[self.zoomCurrent]
		zoomFrom = (int(xCenter-(zoomWidth*0.5)), int(yCenter-(zoomHeight*0.5)))
		zoomTo = (int(xCenter+(zoomWidth*0.5)), int(yCenter+(zoomHeight*0.5)))
		return(zoomFrom,zoomTo)
		
	# Todo: stop this from overshooting into repeat pixels
	def pan_zoom_region(self):
		pixelScale = self.image_view.width / Settings.width
		pixelZoomScale = pixelScale * self.zoomLevels[self.zoomCurrent]
		pixelPanDistance = [self.panDistance[0]/pixelZoomScale/Settings.pixelSize, self.panDistance[1]/pixelZoomScale]
		self.zoom_frame.center = self.limit_zoom_center((self.zoom_frame.center[0]-(pixelPanDistance[0]*pixelScale*Settings.pixelSize) , self.zoom_frame.center[1]-(pixelPanDistance[1]*pixelScale)))
		self.superview['debugtext'].text = "Pan Distance: [" + str(round(pixelPanDistance[0],2)) + ", " + str(round(pixelPanDistance[1],2)) + "], zoomCenter: " + str(self.zoom_frame.center)
		return True
		
	# Returns the currently displayed region as x,y coordinates. 0-based
	def get_current_region(self):
		return (self.get_zoom_region()) if (self.zoomState == True) else ( (0, 0) , ((Settings.width/Settings.pixelSize)-1, Settings.height-1) )
		#return (self.get_zoom_region()) if (self.zoomState == True) else ( (0, 0) , (int(self.width-1), int(self.height-1)) )
		
		
	# Returns the pixels visible at the current zoom level
	def position_pixels(self):
		# Upper right and lower left corner of pixels in the view
		(startPos, endPos) = self.get_current_region()
		# Make sure these are ints
		startPos = (int(startPos[0]), int(startPos[1]))
		endPos = (int(endPos[0]), int(endPos[1]))
		
		pixelScale = (self.width/Settings.aspectPAL) / (endPos[0]-startPos[0]+1) / Settings.pixelSize # Pixel scale
		#print('pixelScale:',str(pixelScale))
		viewPixels = []     # Array holding the pixels in the view
		# Move all pixels off-screen
		if self.zoomState is True:
			for index in range(0,len(self.pixels)):
				self.pixels[index].rect.x = self.pixels[index].rect.y = -100
		# Position zoomed pixels over canvas
		for y in range(startPos[1],endPos[1]+1):
			for x in range(startPos[0],endPos[0]+1):
				curPixel = self.pixels[xy_to_index(x, y, Settings.actualWidth)]
				viewPixels.append(curPixel.index)
				# rect.x, rect.y is components LOWER-left corner
				curPixel.rect.x = (x-startPos[0]) * pixelScale * Settings.pixelSize * Settings.aspectPAL
				curPixel.rect.y = (y-startPos[1]) * pixelScale
				curPixel.rect.width = pixelScale * Settings.pixelSize * Settings.aspectPAL
				curPixel.rect.height = pixelScale
		#print('last pixel',self.pixels[-1].rect.x)
		return viewPixels
		
	# Redraws the main editor window
	def redraw_canvas(self, updategrid=False):
		# Gets the pixels covered by the current zoom level
		zoomPixels = self.position_pixels()
		# Redraw view
		self.image_view.image = self.create_new_image()
		with ui.ImageContext(self.width, self.height) as ctx:
			for i in zoomPixels:
				p = self.pixels[i]
				ui.set_color(p.color)
				pixel_path = ui.Path.rect(p.rect[0],p.rect[1],p.rect[2],p.rect[3])
				pixel_path.fill()
				pixel_path.line_width = 0.5
				pixel_path.stroke()
			self.image_view.image = ctx.get_image()
			## Todo: insert drawing of preview window:
		# Redraw grid
		if updategrid == True:
			self.grid_layout.image = self.draw_grid_image()
			self.grid_layout.alpha = self.gridOpacity
		if self.color_check.hidden is False:
			self.character_colorcheck()
		return True
		
	# Flip colors
	def mirror_image_horizontal(self):
		colorList = list()
		for p in self.pixels:
			colorList.append(p.color)
		for row in range(0,200):
			startIndex = row * 160
			for col in range(0, 160):
				self.pixels[startIndex+col].color = colorList[startIndex+(159-col)]
		del colorList
		self.redraw_canvas()
		self.preview_update()
		return True
		
	def mirror_image_vertical(self):
		colorList = list()
		for p in self.pixels:
			colorList.append(p.color)
		for row in range(0,200):
			for col in range(0, 160):
				self.pixels[(row * 160)+col].color = colorList[((199-row) * 160)+col]
		del colorList
		self.redraw_canvas()
		self.preview_update()
		return True
		
	# Offset colors horizontally
	def offset_colors_horizontal(self, pixelOffset):
		colorList = list()
		for p in self.pixels:
			colorList.append(p.color)
		pixelsPerRow = Settings.width / Settings.pixelSize
		for row in range(0, Settings.height):
			startIndex = row * pixelsPerRow
			if pixelOffset > 0: # Moving pixels to the right
				colorList = colorList[:startIndex] + colorList[startIndex+pixelsPerRow-pixelOffset:pixelsPerRow+startIndex] + colorList[startIndex:startIndex+pixelsPerRow-pixelOffset] + colorList[startIndex+pixelsPerRow:]
			else:
				colorList = colorList[:startIndex] + colorList[startIndex-pixelOffset:startIndex+pixelsPerRow] + colorList[startIndex:startIndex-pixelOffset] + colorList[startIndex+pixelsPerRow:]
		pIndex = 0
		for p in self.pixels:
			p.color = colorList[pIndex]
			pIndex += 1
		del colorList
		self.redraw_canvas()
		self.preview_update()
		return True
		
	# Offset colors vertically
	def offset_colors_vertical(self, lineOffset):
		charRowSize = int(Settings.actualWidth*Settings.charSize)
		colorList = list()
		for p in self.pixels:
			colorList.append(p.color)
		countStart = lineOffset*Settings.actualWidth
		for p in self.pixels:
			if countStart >= Settings.actualWidth*Settings.height:
				countStart -= Settings.actualWidth*Settings.height
			p.color = colorList[countStart]
			countStart += 1
		del colorList
		self.redraw_canvas()
		self.preview_update()
		return True
		
	# increase colorCheck state, then perform a colorCheck
	def next_colorcheck_state(self):
		self.colorCheckState += 1
		if self.colorCheckState == 4:
			self.colorCheckState = 0
		#self.character_colorcheck()
		return True
		
	# Check characters if they have a legal amount of colours
	def character_colorcheck(self):
		stateColor = {1:'red', 2:'orange', 3:'green'}
		if self.colorCheckState == 0:
			self.color_check.hidden = True
			#self.colorCheckState = 0
			self.superview['debugtext'].text = "Color check turned off."
			return True
		if self.colorCheckState > 0 and self.colorCheckState < 4:
			self.color_check.hidden = False
			(startPos, endPos) = self.get_current_region()
			charSize = Settings.charSize
			clashCount = 0
			pixelScale =  (self.width/Settings.aspectPAL)/(endPos[0]-startPos[0]+1)/Settings.pixelSize #self.height/Settings.height
			#s = self.width/self.row if self.row > self.column else self.height/self.column
			with ui.ImageContext(self.width, self.height) as ctx:
				ui.set_color(stateColor[self.colorCheckState])
				# Grid line per character
				for y in range(int(startPos[1]/charSize)*charSize, endPos[1]+1, charSize):
					for x in range(int(startPos[0]/charSize*charSize), endPos[0]+1,4):
						# Check this character for color clash
						charColors ={self.background_color[:3]}
						startIndex = xy_to_index(x, y, Settings.actualWidth)
						if startIndex:
							for pixelRow in range(0, 8):
								for pixelCol in range(0, 4):
									pixelIndex = startIndex + pixelRow*Settings.actualWidth + pixelCol
									charColors.add(self.pixels[pixelIndex].color[:3])
							if (self.colorCheckState == 1 and len(charColors) > 4) or (self.colorCheckState == 2 and len(charColors) == 3) or (self.colorCheckState == 3 and len(charColors) == 2):
								clashCount = clashCount + 1
								pixel_path = ui.Path.rect((x-startPos[0])*pixelScale*2*Settings.aspectPAL, (y-startPos[1])*pixelScale, pixelScale*charSize*Settings.aspectPAL, pixelScale*charSize)
								pixel_path.line_width = 2
								pixel_path.stroke()
					self.color_check.image = ctx.get_image()
			if clashCount == 0:
				self.color_check.image = self.create_new_image() # Clear clash image
			if self.colorCheckState == 1:
				self.superview['debugtext'].text = str(clashCount) + " characters have color clashes."
			if self.colorCheckState == 2:
				self.superview['debugtext'].text = str(clashCount) + " characters have 1 available color."
			if self.colorCheckState == 3:
				self.superview['debugtext'].text = str(clashCount) + " characters have 2 available colors."
			#self.colorCheckState += 1
			return clashCount
	
	def create_crt_overlay(self):
		crt_img = Image.new("RGB", (1, Settings.height*2), (0,0,0))
		# Create repeating data for crt overlay
		imgdata = ((200,200,200),(50,50,50))*Settings.height # height is 200
		crt_img.putdata(imgdata)
		crt_img = crt_img.resize((Settings.width*2, Settings.height*2), Image.NEAREST)
		return crt_img
		
	#@ui.in_background
	def preview_init(self):
		path = ui.Path.rect(0, 0, Settings.width, Settings.height)
		with ui.ImageContext(Settings.width, Settings.height) as ctx:
			ui.set_color((0, 0, 0, 1))
			path.fill()
			self.superview['preview'].image = ctx.get_image()
		return True
		
	# TODO: The image seems to be scaled incorrectly. Investigate!
	@ui.in_background
	def preview_putimg(self, ui_img):
		#self.unfilteredPreview = ui_img
		
		# A simple and fast CRT-emulation for our preview:
		pil_img = pixels_to_png(self.background_color, self.pixels, self.row*2, self.column)
		pil_img = pil_img.resize((Settings.width*2, Settings.height*2), Image.NEAREST)
		pil_img = pil_img.convert("RGB")
		pil_img = ImageChops.multiply(pil_img.filter(ImageFilter.SMOOTH), self.crt_overlay)
		pil_img = ImageChops.screen(pil_img.filter(ImageFilter.GaussianBlur(5)), pil_img)
		# Todo: Crashes in latest Pythonista:
		ui_img = pil_to_ui(pil_img)
		self.superview['preview'].image = ui_img
		return True
		
	@ui.in_background
	def preview_drawPixels(self):
		zoomPixels = self.position_pixels()
		old_img = self.unfilteredPreview
		with ui.ImageContext(Settings.width, Settings.height) as ctx:
			old_img.draw(0,0,Settings.width, Settings.height)
			for i in zoomPixels:
				p = self.pixels[i]
				ui.set_color(p.color)
				pixel_path = ui.Path.rect(p.position[0]*Settings.pixelSize,p.position[1],1*Settings.pixelSize,2)
				pixel_path.line_width = 0.5
				pixel_path.fill()
				#pixel_path.stroke()
			#self.superview['preview'].image = ctx.get_image()
			self.preview_putimg(ctx.get_image())
			return True
			
	def preview_update(self):
		if self.zoomState is False:
			self.preview_putimg(self.image_view.image)
		else:
			self.preview_drawPixels()
			
	def reset(self, row=None, column=None):
		for p in self.pixels:
			p.color = self.background_color
		self.redraw_canvas(updategrid=True)
		self.preview_update()
		#self.pixels = []
		#self.grid_layout.image = self.init_pixel_grid()
		#self.set_image()
		
	def autosave(self, image_name="noname"):
		# Move current image to autobackup folder
		autoback_dir = Settings.image_location + image_name + '/'
		if not isdir(autoback_dir):
			mkdir(autoback_dir)
		timestring = datetime.now().strftime('%Y%m%d_%H%M')#[:-1]
		
		if isfile(Settings.image_location + image_name + ".png"):
			copy2(Settings.image_location + image_name + ".png", autoback_dir + timestring + ".png")
		
		# Save current image to file
		save_name = Settings.image_location + image_name + ".png"
		image = pixels_to_png(self.background_color, self.pixels, Settings.width, Settings.height)
		image.save(save_name)
		
		# Just to be sure: if the autosave has no changes, delete it
		dirfiles = listdir(autoback_dir)
		if len(dirfiles) > 1:
			dirfiles.sort()
			imgcompare = open(autoback_dir+dirfiles[-1],"rb").read() == open(autoback_dir+dirfiles[-2],"rb").read()
			if imgcompare == True: 
				remove(autoback_dir+dirfiles[-1])
				print('No changes in image "' + image_name + '". Skipping autosave.')
				return True
			
		print('Auto saved image at ' + image_name + '/' + timestring)
		return True
		
	#@ui.in_background
	def loadimage(self, file_name, format_img=True):
		self.color_check.hidden = True
		loadImg = file_to_img(file_name, Settings.actualWidth, Settings.height)
		img = self.create_new_image()
		charRowSize = Settings.actualWidth * Settings.charSize
		# We read and draw the image one character line at a time
		#indicator = ui.ActivityIndicator()
		#indicator.center = self.center
		#self.superview.add_subview(indicator)
		#indicator.bring_to_front()
		#indicator.start()
		pixelCol = (0,0,0)
		#self.superview['labelbg'].background_color = (1,0,0)
		for charRow in range(0, int(Settings.height/Settings.charSize)):
			indexArray = []
			startIndex = charRow*charRowSize
			endIndex = charRow*charRowSize + charRowSize
			#print ("Importing subrow: " + str(startIndex) + ", " + str(endIndex))
			for i in range(startIndex, endIndex):
				indexArray.append(i)
				# Todo: getpixel is slow, find an alternative
				pixelCol = loadImg.getpixel(self.pixels[i].position)
				# Find the closest color in the C64 palette
				pixelCol = closest_in_palette(pixelCol, Settings.c64color_palette)
				#pixelCol = closest_in_palette_old(pixelCol)
				self.pixels[i].color = color_to_1(pixelCol)
			img = self.draw_index_array(img, indexArray, noCheck=True)
			# Animate the background color as we load the image, tape loader style :)
			self.superview['labelbg'].background_color = color_to_1(pixelCol)
			self.set_image(img)
		self.preview_putimg(img)
		self.superview['labelbg'].background_color = (0,0,0)
		#indicator.stop()
		#self.superview.remove_subview(indicator)
		return True
		
	# Export image to c64 native binaries
	def savebinary(self, fileFormat='koa'):
	
		# Base character index list
		baseIndices = charLine = numpy.array(range(0,4))
		for c in range(1,8):
			baseIndices = numpy.append(baseIndices,(charLine+(40*4*c)))
			
		# Bit lookup
		bit = {0:'00', 1:'01', 2:'10', 3:'11'}
		
		# Image and colour data
		bgColor = Settings.c64color_palette.index(color_to_255(self.background_color))
		bitmapBytes = []
		screenBytes = []
		colorBytes = []
		
		# We will keep track of chars with too many colours
		problemChars = 0
		
		# Parse through the characters
		for y in range(0,25):
			for x in range (0,40):
				startIndex = (x*4) + (y*8*4*40)
				charIndices = baseIndices + startIndex
				
				charColors = list()
				#colorList = {self.background_color[:3]} #Store in set for efficient count
				colorSet = {bgColor}
				for c in charIndices:
					col = Settings.c64color_palette.index(color_to_255(self.pixels[c].color))
					charColors.append(col)
					colorSet.add(col)
					
				# Uh oh, we're in trouble. Too many colours in character
				if len(colorSet) > 4:
					problemChars += 1
					#print ("Too many colours in character: " + str(startIndex))
					# Todo: Insert code to reduce colours. For now we just exit
					
				# Convert set to list, pad if necessary
				colorSet.remove(bgColor)
				colorList = [bgColor] + list(colorSet)
				if len(colorList) != 4:
					colorList += [0] * (4 - len(colorList))
					
				for c in range(0,8):
					row = charColors[c*4:c*4+4]
					bitmapBytes.append(colorList.index(row[0]) << 6 | colorList.index(row[1]) << 4 | colorList.index(row[2]) << 2 | colorList.index(row[3]))
				screenBytes.append(colorList[1] << 4 | colorList[2])
				colorBytes.append(colorList[3])
				
				#if (x == 2 and y == 0):
				#    print (str(bitmapBytes))
				#    print ("xy:" + str(x) + ',' + str(y) + ' col:' + str(colorList))
				
		if problemChars > 0:
			console.hud_alert('Could not export! Too many colours in ' + str(problemChars) + ' character(s).')
			self.colorCheckState = 1
			self.character_colorcheck()
			return False
			
		# Exports image to disk
		fullformat = {'koa':'C64 Koala image','prg':'C64 .prg executable'}
		fileName = console.input_alert("Exporting as " + fullformat[fileFormat] + ".")
		if fileName[-4:] == "." + fileFormat:
			fileName = fileName[:-4]
		fileName = ('images/' + fileName + '.' + fileFormat)
		
		if fileFormat == 'koa':
			fileBytes = bytearray([0x00, 0x60]) + bytearray(bitmapBytes) + bytearray(screenBytes) + bytearray(colorBytes) + bytearray([bgColor])
			
		# Prg hex is borrowed from https://github.com/fsphil/c64image/blob/master/c64image.py
		elif fileFormat == 'prg':
			fileBytes = bytearray.fromhex(
			('01080c080d089e3230363100000078a240a01f205608a9008d6308a9448d6408a2e' +
			'8a003205608a9008d6308a9d88d6408a2e8a003205608a91c8d18d0a93b8d11d0a9' +
			'188d16d0a9028d00dda9%02X8d20d08d21d04c5308e8c8cad00488d00160ad78088d0' +
			'060ee6008d003ee6108ee6308d003ee64084c5808') % bgColor
			)
			fileBytes += bytearray(bitmapBytes) + bytearray(screenBytes) + bytearray(colorBytes)
		
		# Write temp file
		open(fileName, 'wb').write(fileBytes)
		sharemsg = console.open_in(fileName)
		print ('File export returned: ' + str(sharemsg))
		remove(fileName)
		
		if sharemsg == None:
			console.hud_alert('Error exporting to ' + fullformat[fileFormat] + '.', 'error')
		else:
			console.hud_alert('Successful export to ' + fullformat[fileFormat] + '.')
		
		return True
		
		
	# Draw line between two pixels
	def draw_line(self, prevPixel, pixel, touchState):
		doLine = False
		xDist = 0
		yDist = 0
		if self.prevPixel != []:
			# Debug edge pixel bug
			# print ('time:' + str(time()) + ' prev:' + str(prevPixel.position) + ' self.prev:' + str(self.prevPixel.position) + ' pix:' + str(pixel.position))
			# Only draw lines inside or at the end of touch
			if touchState == "moved" or touchState == "ended":
				# Check if distance is more than 1 pixel on either axis
				xDist = max(pixel.position[0], self.prevPixel.position[0]) - min(pixel.position[0], self.prevPixel.position[0])
				yDist = max(pixel.position[1], self.prevPixel.position[1]) - min(pixel.position[1], self.prevPixel.position[1])
				#print ("x:" + str(xDist) + ", y:" + str(yDist))
				if xDist < self.brushMinDist[self.brushSize] and yDist < self.brushMinDist[self.brushSize]:
					self.draw_brush(pixel)
					self.prevPixel = pixel
					return True
			#self.current_color = 'red' # debug color
			self.draw_brush(prevPixel)
			self.draw_brush(pixel)
			curPixel = None
			linePixels = []
			xStart = prevPixel.position[0]
			yStart = prevPixel.position[1]
			xDir = 1 if xStart < pixel.position[0] else -1
			yDir = 1 if yStart < pixel.position[1] else -1
			yIncr = 0 if yDist == 0 else (float(xDist)/yDist)
			xIncr = 0 if xDist == 0 else (float(yDist)/xDist)
			# Update all pixel objects along the drawn line
			for c in range(1, max(xDist,yDist)):
				if yDist >= xDist:
					#self.current_color = 'yellow' # debug color
					curPixel = self.pixels[ xy_to_index( int(xStart+(yIncr*c*xDir)+0.5), int(yStart+(c*yDir)), Settings.actualWidth )]
				else:
					#self.current_color = 'purple' # debug color
					curPixel = self.pixels[ xy_to_index( xStart+(xDir*c), int(yStart+(xIncr*c*yDir)), Settings.actualWidth )]
				linePixels.append(curPixel.index)
			# Draw the line pixels
			linePixelSet = []
			if self.brushSize != 1:
				for l in linePixels:
					linePixelSet.extend(self.brushArrays[self.brushSize]+l)
			else:
				linePixelSet = linePixels
			self.image_view.image = self.draw_index_array(self.image_view.image, set(linePixelSet), drawColor=self.current_color)
			self.prevPixel = pixel
			return True
			
	# Old draw function. Not used at the moment.
	def draw_single_pixel(self, pixel):
		# colorMask = 0 # 0: off, 1: draw only on bg color, 2:dont draw on bg color
		if pixel.color != self.current_color:
			if self.check_dither(pixel.position):
				if self.check_mask(pixel):
					self.store_undo_stroke(pixel.index)
					pixel.color = self.current_color
					#self.pixel_path.append(pixel)
					old_img = self.image_view.image
					path = ui.Path.rect(*pixel.rect)
					with ui.ImageContext(self.width, self.height) as ctx:
						if old_img:
							old_img.draw()
						ui.set_color(self.current_color)
						pixel_path = ui.Path.rect(*pixel.rect)
						pixel_path.line_width = 0.5
						pixel_path.fill()
						pixel_path.stroke()
						self.set_image(ctx.get_image())
						
	def draw_brush(self,pixel):
		# Quick fix in case the brush lands near the border
		if self.brushSize == 6:
			if (pixel.index%160)==0:
				self.image_view.image = self.draw_index_array(self.image_view.image,
				numpy.array([-320,-160,0])+pixel.index,
				drawColor=self.current_color)
				return True
		self.image_view.image = self.draw_index_array(self.image_view.image,
		self.brushArrays[self.brushSize]+pixel.index,
		drawColor=self.current_color)
		return True
		
	# Draw pixels from array on top of image (ui.image)
	def draw_index_array(self, img, indexArray, drawColor=False, noCheck=False):
		with ui.ImageContext(self.width, self.height) as ctx:
			img.draw()
			for i in indexArray:
				# Drawing negative indices will mess up the image, so only indices from 0 and up
				if i >= 0:
					# Skip checks and undos and just draw the pixels
					if noCheck==True:
						p = self.pixels[i]
						if drawColor != False:
							p.color = drawColor
						ui.set_color(p.color)
						pixel_path = ui.Path.rect(p.rect[0],p.rect[1],p.rect[2],p.rect[3])
						pixel_path.line_width = 0.0
						pixel_path.fill()
						pixel_path.stroke()
					else:
						if self.pixels[i].color != self.current_color:
							if self.check_dither(self.pixels[i].position):
								if self.check_mask(self.pixels[i]):
									self.store_undo_stroke(i)
									p = self.pixels[i]
									if drawColor != False:
										p.color = drawColor
									ui.set_color(p.color)
									#  Path.rect(x, y, width, height)
									pixel_path = ui.Path.rect(p.rect[0],p.rect[1],p.rect[2],p.rect[3])
									pixel_path.line_width = 0.0
									pixel_path.fill()
									pixel_path.stroke()
			img = ctx.get_image()
		return img
		
	# Main pixel action function!
	# Called by 'touch_began', 'touch_moved' and 'touch_ended'
	def action(self, touch, touchState):
		p = scene.Point(*touch.location)
		# Action for drawing modes
		if self.toolMode == 'dots' or self.toolMode == 'lines':
			hit = False
			for pixel in self.pixels:
				if p in pixel.rect:
					hit = True
					if touchState == "began":
						# Clear undo data on current step when stroke starts
						self.prevPixel == []
						self.wipe_undo_step(self.currentUndoStep)
					if self.brushSize == 'c':
						charIndices = get_char(pixel.index)
						self.image_view.image = self.draw_index_array(self.image_view.image,
							charIndices, drawColor=self.current_color)
					else:
						if self.toolMode == 'dots':
							self.draw_brush(pixel)
							self.superview['debugtext'].text = "index:" + str(pixel.index) + ", pos:" + str(pixel.position)
						# Todo: Something in here causes last edge pixels to be drawn
						elif self.toolMode == 'lines':
							self.draw_line(self.prevPixel, pixel, touchState)
							self.prevPixel = pixel
							if touchState == "ended":
								# ToDo: This crashes the program. Fix it.
								self.preview_update()
								self.prevPixel = []
							self.superview['debugtext'].text = "index:" + str(pixel.index) + ", pos:" + str(pixel.position)
					# We will try to merge strokes that are close together in time
					# Only move to new undo level if there is some time between strokes
					# (disabled at the moment, undo time used to update preview)
					if touchState == "ended":
						# Move to next undo level
						#self.prevPixel == []
						self.next_undo_step()
						undoDelta = int(time()) - self.lastUndo
						if undoDelta > Settings.previewTime:
							#self.preview_update()
							self.lastUndo = int(time())
						# Auto-save image
						saveDelta = int(time()) - self.lastSave
						self.superview['debugtext'].text += ' Time to autosave: ' + str(Settings.autoSaveTime-saveDelta)
						if saveDelta > Settings.autoSaveTime:
							self.superview['debugtext'].text = "Autosaving..."
							self.autosave(self.imageName)
							self.lastSave = int(time())
			
			# Store undo if painting leaves canvas
			# Seems to give a performance hit. Please check.	
			if hit == False:
				if touchState == "ended":
					self.next_undo_step()
					
				# self.superview['debugtext'].text = 'Outside bounds'
				
			return True
		# Zoom mode
		elif self.toolMode == 'zoom':
			self.limit_zoom_center(touch.location)
			zoomCenter = self.zoom_frame.center
			(zoomFrom, zoomTo) = self.get_zoom_region()
			self.superview['debugtext'].text = "Zoom location: [" + str(zoomFrom) + "," + str(zoomTo) + "], zoom center:" + str(zoomCenter) + "" #+ "loc: " + str(touch.location)
			# When the finger is released, we draw the zoomed view
			if touchState == "ended":
				#self.superview['debugtext'].text = "Zooming in"
				self.zoomState = True
				self.redraw_canvas(updategrid=True)
				self.zoom_frame.hidden = True
				# Return to previous tool mode
				self.toolMode = self.prevMode
				self.superview['debugtext'].text = "Mode set back to " + self.toolMode
				self.superview['toolbar'].set_toolMode(self.toolMode)
				# Todo: Sometimes, random dots get drawn after this command
				# Investigate why
				# Update preview image
			return True
		elif self.toolMode == 'pan':
			if touchState == "began":
				self.panStart = touch.location
			self.panDistance = [touch.location[0] - self.panStart[0], touch.location[1] - self.panStart[1]]
			self.superview['debugtext'].text = "Pan Distance: " + str(self.panDistance)
			self.image_view.x = self.grid_layout.x = self.panDistance[0]
			self.image_view.y = self.grid_layout.y = self.panDistance[1]
			#print str(self.image_view.image.frame)
			if touchState == "ended":
				self.image_view.x = self.grid_layout.x = 0
				self.image_view.y = self.grid_layout.y = 0
				self.pan_zoom_region()
				self.redraw_canvas(updategrid=True)
				#print "Pandistance: " + str(self.panDistance)
			return True
			
	def touch_began(self, touch):
		self.action(touch, "began")
		
	def touch_moved(self, touch):
		self.action(touch, "moved")
		
	def touch_ended(self, touch):
		self.action(touch, "ended")
		
		
class ColorView (ui.View):
	c64color_gradient = [0, 6, 9, 2, 11, 4, 8, 14, 12, 5, 10, 3, 15, 7, 13, 1]
	
	c64hex = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0A", "0B", "0C", "0D", "0E", "0F"]
	
	palette_type = 'numeric'
	
	def did_load(self):
		self.color = {'r': 0, 'g': 0, 'b': 0, 'a': 1}
		for subview in self.subviews:
			self.init_action(subview)
		self.subviews[2].title = ""
		self.subviews[2].background_image = ui.Image.named('icons/tool_palette_numeric.png')
		self.subviews[3].title = ""
		self.subviews[3].background_image = ui.Image.named('icons/tool_hold_off.png')
		self.subviews[4].title = ""
		self.subviews[4].background_image = ui.Image.named('icons/tool_charinfo.png')
		self.subviews[5].title = ""
		self.subviews[5].background_image = ui.Image.named('icons/tool_palette_lock_off.png')
		self.subviews[6].title = "" # Colour button
		
		self.set_palette(self.palette_type)
		
	def init_action(self, subview):
		if hasattr(subview, 'action'):
			subview.action = self.choose_color if subview.name != 'clear' else self.clear_user_palette
		if subview.name == 'set_palette':
			subview.action = self.set_palette
		if subview.name == 'chartest':
			subview.action = self.chartest
		if subview.name == 'hold':
			subview.action = self.hold
		if subview.name == 'lockbg':
			subview.action = self.lockbg
		if subview.name == 'current_color':
			subview.action = self.swap_color
		if hasattr(subview, 'subviews'):
			for sv in subview.subviews:
				self.init_action(sv)
				
	def palette_list(self):
		for subview in self['palette'].subviews:
			print (subview.title + ": (" + str(int(subview.background_color[0]*255)) + ", " + str(int(subview.background_color[1]*255)) + ", " + str(int(subview.background_color[2]*255)) + ")")
			
	def set_palette(self, sender):
		num = 0
		if self.palette_type == 'numeric':
			for subview in self['palette'].subviews:
				subview.background_color = color_to_1(Settings.c64color_palette[num])
				subview.title = self.c64hex[num]
				num = num + 1
			self.palette_type = "gradient"
			self.subviews[2].background_image = ui.Image.named('icons/tool_palette_numeric.png')
			try:
				self.superview['debugtext'].text = "Palette set to numeric"
			except Exception as e:
				pass
		elif self.palette_type == 'gradient':
			for subview in self['palette'].subviews:
				subview.background_color = color_to_1(Settings.c64color_palette[self.c64color_gradient[num]])
				subview.title = self.c64hex[self.c64color_gradient[num]]
				num = num + 1
			self.palette_type = "numeric"
			self.subviews[2].background_image = ui.Image.named('icons/tool_palette_gradient.png')
			self.superview['debugtext'].text = "Palette set to gradient"
			
	def hold(self, sender):
		self.superview['editor'].colorMask += 1
		if self.superview['editor'].colorMask > 2:
			self.superview['editor'].colorMask = 0
			self.subviews[3].background_image = ui.Image.named('icons/tool_hold_off.png')
			self.superview['debugtext'].text = 'No color masking'
		if self.superview['editor'].colorMask == 1:
			self.subviews[3].background_image = ui.Image.named('icons/tool_mask_bg.png')
			self.superview['debugtext'].text = 'Background color used as mask'
		if self.superview['editor'].colorMask == 2:
			self.subviews[3].background_image = ui.Image.named('icons/tool_hold_bg.png')
			self.superview['debugtext'].text = 'Background color hold'
		return True
		
	def get_color(self):
		return tuple(self.color[i] for i in 'rgba')
		
	def set_color(self, color=None):
		color = color or self.get_color()
		if self.superview['editor'].toolMode != 'dots' and self.superview['editor'].toolMode != 'lines':
			self.superview['editor'].toolMode = self.superview['editor'].prevMode
			self.superview['toolbar'].set_toolMode(self.superview['editor'].toolMode)
		if self['current_color'].background_color == color and self.superview['editor'].bgColorLock == False:
			# Set color twice, and the image bg color will be set
			self['bg_color'].background_color = color
			self.superview['editor'].background_color = color
			self.superview['debugtext'].text = "BG color set to " + str(color_to_255(color))
			if not self.superview['editor'].color_check.hidden:
				self.superview['editor'].character_colorcheck()
		else:
			self['current_color'].background_color = color
			self.superview['editor'].current_color = color
			self.superview['debugtext'].text = "Brush color set to " + str(color_to_255(color))
			
	@ui.in_background
	def choose_color(self, sender):
		if sender.name in self.color:
			self.color[sender.name] = sender.value
			self.set_color()
		elif sender in self['palette'].subviews:
			self.set_color(sender.background_color)
		elif sender.name == 'color_input':
			try:
				c = sender.text if sender.text.startswith('#') else eval(sender.text)
				v = ui.View(background_color=c)
				self['color_input'].text = str(v.background_color)
				self.set_color(v.background_color)
			except Exception as e:
				console.hud_alert('Invalid Color', 'error')
				
	def chartest(self, sender):
		self.superview['editor'].next_colorcheck_state()
		self.superview['editor'].character_colorcheck()
		
	def lockbg(self, sender):
		self.superview['editor'].bgColorLock = not self.superview['editor'].bgColorLock
		if self.superview['editor'].bgColorLock == False:
			self.subviews[5].background_image = ui.Image.named('icons/tool_palette_lock_off.png')
		else:
			self.subviews[5].background_image = ui.Image.named('icons/tool_palette_lock_on.png')
			
	def swap_color(self, sender):
		self['bg_color'].background_color, self['current_color'].background_color = self['current_color'].background_color, self['bg_color'].background_color
		self.superview['editor'].current_color = self['current_color'].background_color
		self.superview['debugtext'].text = "Swapped BG/FG colours."
		
		
class ToolbarView (ui.View):

	# Customize view after loading UI file
	def did_load(self):
		toolImagenames = {'Dot':'dots', 'Undo':'undo', 'File':'file', 'Save':'save',
		'Prev':'preview', 'Zoom':'zoom', 'Load':'load', 'Grd':'grid',
		'Lin':'lines', 'Exit': 'exit', 'Lvl': 'zoomlevel', 'Dith': 'dither_off',
		'Char':'charinfo', 'Pan': 'pan', 'Bru1':'brush_1', 'Bru2':'brush_2',
		'Bru6':'brush_6', 'BruC':'brush_char', 'Redo':'redo',
		'MirX':'flipx', 'MirY':'flipy', 'Pan':'pan', 'PPos':'preview_position',
		'Sel':'selection','Up':'offset_up','Down':'offset_down','Left':'offset_left'
		,'Right':'offset_right','Prg':'prg','Koa':'koala'}
		#counter = 0
		for subby in self.subviews[0].subviews:
			#print "subview " + str(counter) + ": " + subby.title
			#counter += 1
			fileName = 'icons/tool_' + toolImagenames[subby.title] + '.png'
			subby.background_image = ui.Image.named(fileName)
			subby.title = ""
		#self.set_toolMode(self.superview['editor'].toolMode)
			
	# Automatically assigns functions to toolbar buttons with same name
	def init_actions(self, subview):
		if hasattr(subview, 'action'):
			# Overriding the automatic function assignment for the brushes
			if subview.name == 'brush1' or subview.name == 'brush2' or subview.name == 'brush6' or subview.name == 'brushc':
				subview.action = eval('self.brushsize')
			elif hasattr(self, subview.name):
				subview.action = eval('self.{}'.format(subview.name))
			#else:
			#  subview.action = self.set_mode
		if hasattr(subview, 'subviews'):
			for sv in subview.subviews:
				self.init_actions(sv)
				
	def show_error(self):
		console.hud_alert('Editor has no image', 'error', 0.8)
		
	def set_toolMode(self, toolName):
		self.superview['debugtext'].text = "Entering " + toolName + " mode"
		self.superview['editor'].toolMode = toolName
		# Setting the tool icon
		self['tools']['paintdots'].background_image = ui.Image.named('icons/tool_dots.png')
		self['tools']['paintlines'].background_image = ui.Image.named('icons/tool_lines.png')
		self['tools']['zoom'].background_image = ui.Image.named('icons/tool_zoom.png')
		self['tools']['pan'].background_image = ui.Image.named('icons/tool_pan.png')
		if toolName == 'dots':
			self['tools']['paintdots'].background_image = ui.Image.named('icons/tool_dots_on.png')
		if toolName == 'lines':
			self['tools']['paintlines'].background_image = ui.Image.named('icons/tool_lines_on.png')
		if toolName == 'zoom':
			self['tools']['zoom'].background_image = ui.Image.named('icons/tool_zoom_on.png')
		if toolName == 'pan':
			self['tools']['pan'].background_image = ui.Image.named('icons/tool_pan_on.png')
			
	def brushsize(self, sender):
		# Reset all icons
		self['tools']['brush1'].background_image = ui.Image.named('icons/tool_brush_1.png')
		self['tools']['brush2'].background_image = ui.Image.named('icons/tool_brush_2.png')
		self['tools']['brush6'].background_image = ui.Image.named('icons/tool_brush_6.png')
		self['tools']['brushc'].background_image = ui.Image.named('icons/tool_brush_char.png')
		if sender.name[-1:] == '1':
			# By clicking the existing brush-size, the dither will be reset
			if self.superview['editor'].brushSize == 1: 
				self.resetDither()
			self.superview['editor'].brushSize = 1
			self['tools']['brush1'].background_image = ui.Image.named('icons/tool_brush_1_on.png')
			self.superview['debugtext'].text = "Brush set to 1 pixel"
		if sender.name[-1:] == '2':
			if self.superview['editor'].brushSize == 2: 
				self.resetDither()
			self.superview['editor'].brushSize = 2
			self['tools']['brush2'].background_image = ui.Image.named('icons/tool_brush_2_on.png')
			self.superview['debugtext'].text = "Brush set to 2 pixels"
		if sender.name[-1:] == '6':
			if self.superview['editor'].brushSize == 6: 
				self.resetDither()
			self.superview['editor'].brushSize = 6
			self['tools']['brush6'].background_image = ui.Image.named('icons/tool_brush_6_on.png')
			self.superview['debugtext'].text = "Brush set to 6 pixels"
		if sender.name[-1:] == 'c':
			if self.superview['editor'].brushSize == 'c': 
				self.resetDither()
			self.superview['editor'].brushSize = 'c'
			self['tools']['brushc'].background_image = ui.Image.named('icons/tool_brush_char_on.png')
			self.superview['debugtext'].text = "Brush set to character"		
			
	def paintdots(self, sender):
		self.set_toolMode('dots')
		self.superview['editor'].zoom_frame.hidden = True
		
	def paintlines(self, sender):
		self.set_toolMode('lines')
		self.superview['editor'].zoom_frame.hidden = True
		
	def mirrory(self, sender):
		self.superview['editor'].mirror_image_vertical()
		
	def mirrorx(self, sender):
		self.superview['editor'].mirror_image_horizontal()
		
	def movedown(self, sender):
		self.superview['editor'].offset_colors_vertical(-8)
		
	def moveup(self, sender):
		self.superview['editor'].offset_colors_vertical(8)
		
	def moveright(self, sender):
		self.superview['editor'].offset_colors_horizontal(4)
		
	def moveleft(self, sender):
		self.superview['editor'].offset_colors_horizontal(-4)
		
	def dither(self, sender):
		if self.superview['editor'].drawDithered == 0:
			self.superview['editor'].drawDithered = 1
			self.superview['debugtext'].text = "Dithered drawing on"
			self['tools']['dither'].background_image = ui.Image.named('icons/tool_dither.png')
		elif self.superview['editor'].drawDithered == 1:
			self.superview['editor'].drawDithered = 2
			self.superview['debugtext'].text = "Inverse dithered drawing"
			self['tools']['dither'].background_image = ui.Image.named('icons/tool_dither_inverse.png')
		elif self.superview['editor'].drawDithered == 2:
			self.superview['editor'].drawDithered = 3
			self.superview['debugtext'].text = "Striped drawing on"
			self['tools']['dither'].background_image = ui.Image.named('icons/tool_ditherlines.png')
		elif self.superview['editor'].drawDithered == 3:
			self.superview['editor'].drawDithered = 4
			self.superview['debugtext'].text = "Inverse striped drawing"
			self['tools']['dither'].background_image = ui.Image.named('icons/tool_ditherlines_inverse.png')
		else:
			self.superview['editor'].drawDithered = 0
			self.superview['debugtext'].text = "Dithered drawing off"
			self['tools']['dither'].background_image = ui.Image.named('icons/tool_dither_off.png')
		return True
	
	# Turn off the dither. This function is run if you re-select the current brush size.
	def resetDither(self):
		self.superview['editor'].drawDithered = 0
		self.superview['debugtext'].text = "Dithered drawing off"
		self['tools']['dither'].background_image = ui.Image.named('icons/tool_dither_off.png')		
							
	def grid(self, sender):
		self.superview['editor'].gridOpacity = self.superview['editor'].grid_layout.alpha = self.superview['editor'].grid_layout.alpha - 0.5
		if self.superview['editor'].gridOpacity < 0:
			self.superview['editor'].darkGrid = not self.superview['editor'].darkGrid
			#print ("Darkgrid: " + str(self.superview['editor'].darkGrid))
			self.superview['editor'].grid_layout.image = self.superview['editor'].draw_grid_image()
			self.superview['editor'].gridOpacity = self.superview['editor'].grid_layout.alpha = 1.0
		return True
		
	def zoom(self, sender):
		if self.superview['editor'].zoomState is False:
			self.superview['editor'].set_zoom_size()
			self.superview['editor'].zoom_frame.hidden = False
			if self.superview['editor'].toolMode != 'zoom':
				self.superview['editor'].prevMode = self.superview['editor'].toolMode
			# The zoom tool action will now be used
			self.set_toolMode('zoom')
		elif self.superview['editor'].zoomState is True:
			self.superview['editor'].zoom_frame.hidden = True
			self.set_toolMode(self.superview['editor'].prevMode)
			self.superview['editor'].zoomState = False
			self.superview['editor'].redraw_canvas(updategrid=True)
			self.superview['editor'].preview_update()
			self['tools']['zoom'].background_image = ui.Image.named('icons/tool_zoom.png')
			
			
	def changezoom(self, sender):
		prevCenter = self.superview['editor'].get_zoom_center()
		if self.superview['editor'].zoomCurrent == len(self.superview['editor'].zoomLevels)-1:
			self.superview['editor'].zoomCurrent = 0
		else:
			self.superview['editor'].zoomCurrent += 1
		self.superview['editor'].set_zoom_size()
		self.superview['editor'].limit_zoom_center(prevCenter)
		self.superview['debugtext'].text = "Zoom level: " + str(self.superview['editor'].zoomLevels[self.superview['editor'].zoomCurrent])
		# Redraw canvas if we are zoomed in
		if self.superview['editor'].zoomState == True:
			self.superview['editor'].redraw_canvas(updategrid=True)
			
	def pan(self, sender):
		# Set a new tool mode
		if self.superview['editor'].zoomState == True:
			if self.superview['editor'].toolMode == 'pan':
				self.set_toolMode(self.superview['editor'].prevMode)
				self['tools']['pan'].background_image = ui.Image.named('icons/tool_pan.png')
				return True
			if self.superview['editor'].toolMode != 'pan':
				if self.superview['editor'].toolMode != 'zoom':
					self.superview['editor'].prevMode = self.superview['editor'].toolMode
				self.set_toolMode('pan')
				return True

	def undo(self, sender):
		self.superview['editor'].fetch_undo_step()
		
	def redo(self, sender):
		self.superview['editor'].fetch_redo_step()
		
	#@ui.in_background
	def preview(self, sender):
		previewMode = self.superview['editor'].previewMode
		if previewMode == 2:
			self.superview['preview'].hidden = True
			self.superview['editor'].previewMode = 0
		elif previewMode == 0:
			self.superview['preview'].hidden = False
			self.superview['preview'].width = Settings.width * Settings.aspectPAL
			self.superview['preview'].height = Settings.height
			self.superview['preview'].y = 560
			self.superview['editor'].previewMode = 1
		elif previewMode == 1:
			self.superview['preview'].hidden = False
			self.superview['preview'].width = Settings.width * Settings.aspectPAL * 2
			self.superview['preview'].height = Settings.height * 2
			self.superview['preview'].y = 560 - Settings.height
			self.superview['editor'].previewMode = 2
		self.prevpos(self, update=False)
			
	def prevpos(self, sender, update=True):
		# Default is x:0 y:360, iPad Pro 11 inch: width: 1194.0 height: 834.0
		numPrevPos = 2
		prevsize = ''
		prevMode = self.superview['editor'].previewMode
		
		if update == True:
			self.superview['editor'].previewPos = (self.superview['editor'].previewPos + 1) % numPrevPos
			print("Updating preview position")
		
		self.superview['preview'].y = self.superview.height - (Settings.height * prevMode)
		
		if self.superview['editor'].previewPos == 0:
			self.superview['preview'].x = 0
		elif self.superview['editor'].previewPos == 1:
			self.superview['preview'].x = self.superview.width - (Settings.width * Settings.aspectPAL * prevMode)
		
		return True	
			
	def file(self, sender):
		self.superview['editor'].autosave(self.superview['editor'].imageName)
		
		# Remove the file operations window if it exists
		if self.superview['File window']:
			self.superview.remove_subview(self.superview['File window'])
			self.superview['debugtext'].text = 'File window closed.'
		# Build the file operations window
		else:
			fv = FileWindow()
			#self.superview['editor'].add_subview(fv)
			self.superview.add_subview(fv)
			self.superview['debugtext'].text = ('File window opened.')
		return True

	def exit(self, sender):
		msg = 'Are you sure you want to quit the pixel editor?'
		if console.alert('Quit', msg, 'Yes'):
			# ToDo: Fix the error when exiting
			try:
				self.superview['editor'].autosave(self.superview['editor'].imageName)
			except Exception as e: 
				print(e)
			
			self.superview.close()
		else:
			self.show_error()
		return True

		
def __init__():

	v = ui.load_view('redux_paint')
	
	# Store the toolbar widths, the layout function needs them
	Settings.colorbarWidth = v['colors'].width
	Settings.toolbarWidth = v['toolbar'].width
	
	toolbar = v['toolbar']
	editor = v['editor']
	#toolbar.pixel_editor = v['editor']
	for subview in toolbar.subviews:
		toolbar.init_actions(subview)
	toolbar.set_toolMode(editor.toolMode)
	v.flex='WH'
	v.present(style = 'fullscreen', hide_title_bar=True)
	
	# If there is a recently saves image, we load it into the editor
	newestFile = max(iglob('images/*.png'), key=getctime)
	if newestFile:
		editor.loadimage(newestFile) #, colorcheck=False)
		baseName = newestFile[7:-4]	
		editor.imageName = baseName
		editor.superview['debugtext'].text = ("Loaded image '" + baseName + "'")
	editor.preview_init()
	
__init__()

