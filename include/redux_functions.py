#!python2

import ui
import ImageEnhance
import ImageFilter
import ImageOps
import numpy
import colorsys
from time import time
import math

from PIL import Image
from io import BytesIO


# Convert colors from [0,255] to [0,1]
def color_to_1(color):
	#return (color[0]/255.0, color[1]/255.0, color[2]/255.0, 1.0)
	return (color[0]/255.0, color[1]/255.0, color[2]/255.0)
	

def color_to_255(color):
	return (int(color[0]*255), int(color[1]*255), int(color[2]*255))


# Old function - kept as backup			
def closest_in_palette(match_color, color_palette):
	i = 0
	bestDelta = 1000
	c = 0
	for color in color_palette:
		r = sorted((color[0], match_color[0]))
		g = sorted((color[1], match_color[1]))
		b = sorted((color[2], match_color[2]))
		delta = r[1]-r[0] + g[1]-g[0] + b[1]-b[0]
		if delta < bestDelta:
			i = c
			bestDelta = delta
		c = c + 1
	return color_palette[i]


def closest_color(match_color, conversion_palette):
	color_distances = list()
	for c in conversion_palette:
		color_distances.append((colordistance(match_color, c[0]), c[0]))
	color_distances.sort(key=lambda tup: tup[0])	
	return color_distances[0][1]


# sRGB to linear
# Input and output is in the range of 0..255
def to_linear(value, gamma_value):
	if value <= 0:
		return 0
	if value >= 255:
		return 255
	value = float(value)/255
	if value <= 0.04045:
		return (value/12.92)*255
	return (((value+0.055)/1.055)**gamma_value)*255
	
	# 0 <= S <= 0.04045: L = S/12.92
	# 0.04045 < S <+ 1: L = ((S+0.055)/1.055)**2.4

		
def srgb_to_linear(color, gamma_value):
	color = to_linear(color[0], gamma_value), to_linear(color[1], gamma_value), to_linear(color[2], gamma_value)
	#(rm, gm, bm) = lumabalance
	#color = color[0]*rm, color[1]*gm, color[2]*bm
	return color


# Linear to sRGB
# Input and output is in the range of 0..255
def from_linear(value, gamma_value):
	if value <= 0:
		return 0
	if value >= 255:
		return 255
	value = float(value)/255
	if value <= 0.0031308:
		return (value*12.92)*255
	return ((1.055*value)**(1/gamma_value) - 0.055)*255
	
	# 0 <= L <= 0.0031308: S = L*12.92
	# 0.0031308 < L <= 1: S = (1.055*L)**(1/2.4) - 0.055

		
def linear_to_srgb(color, gamma_value):
	#(rm, gm, bm) = lumabalance
	#color = float(color[0])/rm, float(color[1])/gm, float(color[2])/bm
	color = from_linear(color[0], gamma_value), from_linear(color[1], gamma_value), from_linear(color[2], gamma_value)
	return color


def lumabalance_mult(color):
	#lumabalance = [0.299, 0.587, 0.114]
	#lumabalance = [1-0.299, 1-0.587, 1-0.114]
	#lumabalance = [0.9, 0.7, 1.0] # First testvalues
	#lumabalance = [0.9, 1.0, 0.7]
	#lumabalance = [1.0, 1.0, 1.0] # Debug
	#(rm, gm, bm) = lumabalance
	(rm, gm, bm) = [0.9, 1.0, 0.7]
	color = color[0]*rm, color[1]*gm, color[2]*bm
	return color

def colordistance(col1, col2):
	(r1,g1,b1) = col1[0], col1[1], col1[2]
	(r2,g2,b2) = col2[0], col2[1], col2[2]
	return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

	
			
# Check if number is even or odd, used by dithered paint mode
def is_odd(x):
	return (x % 2)
	
	
def xy_to_index(xcoord, ycoord, actual_width, maximum=31999):
	arrayIndex = int((ycoord*actual_width) + xcoord)
	if arrayIndex > maximum:
		print ('Illegal index:' + str(arrayIndex) + ', coord:[' + str(xcoord) + ',' + str(ycoord) + ']')
		return False
	return arrayIndex
	

# Is this even used?	
def index_to_xy(arrayIndex, actual_width):
	ycoord = int(arrayIndex/actual_width)
	xcoord = arrayIndex - (actual_width * ycoord)
	return (xcoord, ycoord)
	
	
# Convert from PIL Image to ui.image
# Translates image data from the Python Image Lib to the iOS ui
def pil_to_ui(img):
	with BytesIO() as bIO:
		img.save(bIO, 'png')
		return ui.Image.from_data(bIO.getvalue())
		
		
# Convert from ui.image to PIL Image
def ui_to_pil(img):
	return Image.open(BytesIO(img.to_png()))
	
	
def pixels_to_png(bg_color, pixels, width, height):
	# Create image
	bgColor = color_to_255(bg_color)
	im = Image.new("RGB", (width, height), bgColor)
	# Fill with pixels
	for p in pixels:
		pixelCol = bgColor
		# convert pixel data from RGBA 0..1 to RGB 0..255
		pixelCol = color_to_255(p.color)
		im.putpixel((int(p.position[0]*2), p.position[1]), pixelCol)
		im.putpixel((int(p.position[0]*2)+1, p.position[1]), pixelCol)
	return im
	
	
def pixels_to_file(bg_color, pixels, width, height, filename):
	im = pixels_to_png(bg_color, pixels, width, height)
	im.save(filename)
	return True

		
def file_to_img(filename, actual_width, height, antialias=False):
	# Do a check for file type
	im = Image.open(filename).convert('RGBA') # Open as PIL image
	scalefilter = Image.NEAREST
	
	print('Loading image ' + str(filename) + ' with size:' + str(im.size))
	
	# If the image is 320 by 200 pixels, we resize it to 160 by 200
	if im.size == (actual_width*2, height):
		#print('Scale mode 1 on ' + str(filename))
		im = im.resize((actual_width, height), scalefilter)
	
	# Image size differs, we crop the image and do an aspect ratio conversion
	else:
		#print('Scale mode 2 on ' + str(filename))
		im = ImageOps.fit(im, (300,200))
		im = im.resize((actual_width, height), scalefilter)
	
	return im
	
	
# Takes character index as an input at returns all indices for the character that index contains
def get_char(index):
	# charNum = ((index/1280)*40) + (int(index/4)%40)
	charNum = numpy.array([0,1,2,3,160,161,162,163,320,321,322,323,480,481,482,483,
	640,641,642,643,800,801,802,803,960,961,962,963,1120,1121,1122,1123])
	firstCharIndex = (int(index/1280)*1280) + ((int(index/4)%40)*4)
	charArray = charNum + firstCharIndex
	return charArray

		
def pngstrip(basestring):
	if basestring[-4:] == '.png':
		return basestring[:-4]
	else:
		return basestring


def build_button(self, button_name, button_width, button_pos, button_action, buttcol, backcol, textcol):
		mybutt = ui.Button(name=button_name, title=button_name)
		mybutt.height = 32-2
		mybutt.width = button_width-2
		mybutt.center = (button_pos[0]+(button_width*0.5), button_pos[1]+16)
		#mybutt.background_color = 'black'
		mybutt.background_color = buttcol
		mybutt.tint_color = textcol
		mybutt.corner_radius = 6
		mybutt.action = button_action
		self.add_subview(mybutt)
		return mybutt
	

	
#def convert_c64(img, conversion_palette, gamma_value, palette_gamma, c64color_names, dither_method, dither_pattern_data, dither_pattern, Settings, startline=0, endline=20): #dither_distance_range, startline=0, endline=20):
#	dither_distance_range = Settings.dither_distance_range

def convert_c64(img, conversion_palette, gamma_value, palette_gamma, c64color_names, dither_method, dither_pattern_data, dither_pattern, dither_distance_range, dither_range, startline=0, endline=20):	
	for ycoord in xrange(startline, endline):
		for xcoord in xrange(0, img.width):
			#if ycoord%10 > 4:
			#	img.putpixel((xcoord,ycoord),img.getpixel((xcoord,ycoord)))
			#else:
			pixelcol = srgb_to_linear(img.getpixel((xcoord,ycoord)), gamma_value)
			if dither_method == 2:
				# Additive dither
				pixelcol = dither_additive(pixelcol, (xcoord,ycoord), conversion_palette, dither_pattern_data, dither_pattern, dither_distance_range)
			elif dither_method == 3:
				# Triangle dither
				pixelcol = dither_blends(pixelcol, conversion_palette, palette_gamma, c64color_names, (xcoord,ycoord), dither_range, dither_pattern_data, dither_pattern)
			else:
				# Nearest color
				pixelcol = closest_color(pixelcol, conversion_palette)
			
			pixelcol = max(0, pixelcol[0]), max(0, pixelcol[1]), max(0, pixelcol[2])
			pixelcol = linear_to_srgb(pixelcol, gamma_value)
			img.putpixel((xcoord,ycoord),((int(pixelcol[0])),int(pixelcol[1]),int(pixelcol[2])))
	return img


def resize_into_img(img, width, height, scalefilter=Image.NEAREST):
	if float(img.width)/float(img.height) < float(width)/float(height):
		print ('Image is taller than wide')
		resize_width = img.width * height / img.height
		resize_height = height
	else:
		resize_width = width
		resize_height = img.height * width / img.width
	image_resize = img.resize((resize_width, resize_height), scalefilter)
	print('Image scaled to:' + str(image_resize.size))
	background = Image.new('RGBA', (width, height), (0, 0, 0, 255))
	offset = ((width - resize_width) / 2, (height - resize_height) / 2)
	#offset = (50,50)
	background.paste(image_resize, offset)
	return background.convert('RGB')


def scale_img(img, antialias_method, width, height, aspect_method, crop_method):
	
	scalefilter = Image.NEAREST
	if antialias_method == 2:
		scalefilter = Image.ANTIALIAS
	
	#img = img.filter(ImageFilter.SMOOTH_MORE)
				
	# Image size differs, we crop the image and do an aspect ratio conversion
	if img.size != (width*2, height):
		if aspect_method == 1:
			imgwidth = 300
		else:
			imgwidth = 320
		if crop_method == 1:
			img = ImageOps.fit(img, (imgwidth,200))
		else:
			img = resize_into_img(img, imgwidth, 200, scalefilter)
	# Finally, resize to C64 non-square pixels
	img = img.resize((width, height), scalefilter)
	
	return img


def filter_img(img, contrast=1.0, brightness=1.0, saturation=1.0):
	enhancer = ImageEnhance.Brightness(img)
	img = enhancer.enhance(brightness)
	
	enhancer = ImageEnhance.Contrast(img)
	img = enhancer.enhance(contrast)
	
	enhancer = ImageEnhance.Color(img) # Saturation
	img = enhancer.enhance(saturation)
	
	# Blur the color channel to reduce color noise
	#colorsys.rgb_to_hls(r, g, b)
	#img = img.convert('HSV')
	#(old_h, old_s, old_v) = img.split()
	
	#img = img.filter(ImageFilter.BLUR)
	#(blur_h, blur_s, blur_v) = img.split()
	#img = Image.merge('HSV', (blur_h, old_s, old_v))
	
	#img = img.convert('RGB')
	
	#img = img.filter(ImageFilter.MedianFilter(3))
	#img = img.filter(ImageFilter.SMOOTH_MORE)
	
	return img



# Not used at the moment
def dither_twocolors(match_color, conversion_palette, c64_color_names, palette_gamma, dither_distance_range, dither_pattern_data, dither_pattern, index, pos):
	# Todo: Revise this, something isnt quite working
	distance = conversionpalette[index][2]
	color1index = c64color_names.index(conversionpalette[index][3])
	color2index = c64color_names.index(conversionpalette[index][4])
	color1 = palette_gamma[color1index]
	color2 = palette_gamma[color2index]
	
	dist1 = colordistance(match_color, color1)
	dist2 = colordistance(match_color, color2)
	
	safezone = dither_distance_range
	
	dithertable = dither_pattern_data[dither_pattern[0]]
	
	ditherx = pos[0]%len(dithertable[0])
	dithery = pos[1]%len(dithertable)
	ditherlookup = dithertable[dithery][ditherx]
	dist = 0.5
	
	#if ditherx == 0 and dithery == 0:
	#	return (128,0,0)
	
	#temprgb1 = int(dist1)
	#temprgb2 = int(dist2)
	#return (temprgb1, 0, temprgb2)
	
	if dist1 < dist2:
		dist = (dist1-safezone) / (distance-safezone*2)
	else:
		dist = 1.0 - ( (dist2-safezone) / (distance-safezone*2) )
	
	if ditherlookup > dist:
		return color1
	else:
		return color2


# Triangle dithering: 
# Scalar projects the pixel down to the vector of the two colors to be dithered.
# Calculates the dither based on where the projection lands on the line.
def dither_triangle(match_color, conversion_palette, c64color_names, palette_gamma, index, position, dither_range, dither_pattern_data, dither_pattern):
	if match_color[0] <= palette_gamma[0][0] and match_color[1] <= palette_gamma[0][1] and match_color[2] <= palette_gamma[0][2]:
		return palette_gamma[0]
	if match_color[0] >= palette_gamma[1][0] and match_color[1] >= palette_gamma[1][1] and match_color[2] >= palette_gamma[1][2]:
		return palette_gamma[1]
	
	# Todo: This might need a gamma and luma correction
	color1index = c64color_names.index(conversion_palette[index][3])
	color2index = c64color_names.index(conversion_palette[index][4])
	col1 = palette_gamma[color1index]	# Darker color
	col2 = palette_gamma[color2index]	# Brighter color
	
	# Unit vector of col1->col2
	colvec = (col2[0]-col1[0], col2[1]-col1[1], col2[2]-col1[2])
	#coldist = math.sqrt((colvec[0]*colvec[0])+(colvec[0]*colvec[0])+(colvec[0]*colvec[0]))
	coldist = conversion_palette[index][2]
	
	# Calculate scalar projection of matchcol->col1 onto col1->col2
	matchvec = (match_color[0]-col1[0], match_color[1]-col1[1], match_color[2]-col1[2])
	projlength = float((matchvec[0]*colvec[0])+(matchvec[1]*colvec[1])+(matchvec[2]*colvec[2])) / coldist
	
	# Divide the length by the precalc length. This will be our gradient ratio!
	gradratio = projlength / coldist
	
	if dither_range == 0:
		return col2
		#if gradratio < 0.5:
		#	return col1
		#else:
		#	return col2
	
	if dither_range != 1:
		# Offset 0 by the dither range, make sure it doesnt get negative
		# gradratio and dither_range runs between 0 and 1
		
		#gradratio = gradratio -(dither_range* 0.5) 
		#gradratio = ((gradratio+0.5) / dither_range)
		
		gradratio = (gradratio / dither_range) #- (gradratio * 0.5)
		#gradratio = (gradratio-0.5)*2
		
		#gradratio = (gradratio / dither_range)
		#gradratio = (-0.5 * (1.0 - dither_range)) + (gradratio / dither_range)
		
		#return (int(projlength), 0, 0)
		#return (int(gradratio*255), 0, 0)
	
	# Debug colours	
	#if position[1]%66 > 33:
	#	return(int(255*gradratio), 0, 0)
				
	dithertable = dither_pattern_data[dither_pattern[0]]
	ditherx = position[0]%len(dithertable[0])
	dithery = position[1]%len(dithertable)
	ditherlookup = dithertable[dithery][ditherx]
	
	if ditherlookup > gradratio:
		return col1
	else:
		return col2

		
def dither_blends(match_color, conversion_palette, palette_gamma, c64color_names, position, dither_range, dither_pattern_data, dither_pattern):
	i = 0
	best_distance = 1000
	
	for c in range(0, len(conversion_palette)):
		if conversion_palette[c][1] == 'mix':
			palette_color = conversion_palette[c][0]
			distance = colordistance(palette_color, match_color)
			if distance < best_distance:
				i = c
				best_distance = distance
			c = c + 1
		
	#### Temp color test!
	#return conversion_palette[i][0]
	####			
	
	#### Temp color test!
	return dither_triangle(match_color, conversion_palette, c64color_names, palette_gamma, i, position, dither_range, dither_pattern_data, dither_pattern)
										
	if conversion_palette[i][1] == 'base':
		return conversion_palette[i][0]

	elif conversion_palette[i][1] == 'replace':
		colorname = conversion_palette[i][2]
		return palette_gamma[c64color_names.index(colorname)] 

	elif conversion_palette[i][1] == 'mix':
		return dither_triangle(match_color, conversion_palette, c64color_names, palette_gamma, i, position, dither_range, dither_pattern_data, dither_pattern)
		
	else: 
		return (0,0,255)

			
def dither_additive(match_color, position, conversion_palette, dither_pattern_data, dither_pattern, dither_distance_range):
	# Add dither matrix to match_color
	dithertable = dither_pattern_data[dither_pattern[0]]
	ditherx = position[0]%len(dithertable[0])
	dithery = position[1]%len(dithertable)
	#ditherlookup = dithertable[dithery][ditherx] * -40
	#ditherlookup = ( dithertable[dithery][ditherx] * dither_distance_range )
	ditherlookup = (dithertable[dithery][ditherx] * dither_distance_range * 1.7) - (dither_distance_range*1.0)
	match_color = match_color[0] + ditherlookup, match_color[1] + ditherlookup, match_color[2] + ditherlookup
	
	# Debug
	#return match_color
				
	# Calculate the distance to all colors in the palette, then sort by distance
	closest_match = closest_color(match_color, conversion_palette)
	
	# Return the closest color
	return closest_match
	

