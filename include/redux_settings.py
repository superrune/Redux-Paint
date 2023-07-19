#!python3

from include.redux_functions import *

# Settings used across the editor
class Settings (object):
	width = 320
	height = 200
	pixelSize = 2  # 1: C64 singlecolor mode, 2: C64 multicolor mode (only 2 works right now)
	actualWidth = int(width / pixelSize)
	charSize = 8
	
	# Main GUI settings
	toolbarWidth = 448
	colorbarWidth = 448
	
	undoSteps = 99
	image_location = "images/"
	autoSaveTime = 5*60  # Number of seconds between autosaves
	previewTime = 2  # Seconds to wait between redrawing preview
	
	aspectPAL = 0.9375 # 4:3 aspect ratio
	widthPAL = 300 # Not pixel width, but screen width (pixel width multiplied by aspect)
	
	c64color_names = [ "black", "white", "red", "cyan", "purple", "green", "blue", "yellow", "orange", "brown", "pink", "darkgrey", "grey", "lightgreen", "lightblue", "lightgrey"]
	c64color_palette = [ (0, 0, 0), (252, 252, 252), (141, 58, 76), (131, 192, 176), (147, 73, 161), (97, 167, 95), (63, 56, 172), (207, 215, 109), (146, 91, 38), (99, 65, 8), (190, 110, 129), (85, 85, 85), (130, 130, 130), (165, 228, 152), (128, 118, 229), (169, 169, 169) ] # Grabbed from Youtube video of a real C64
	#c64color_palette = [ (0, 0, 0), (255, 255, 255), (129, 51, 56), (117, 206, 200), (142, 60, 151), (86, 172, 77), (46, 44, 155), (237, 241, 113), (142, 80, 41), (85, 56, 0), (196, 108, 113), (74, 74, 74), (123, 123, 123), (169, 255, 159), (112, 109, 235), (178, 178, 178) ] # 'Colodore' palette from www.pepto.de/projects/colorvic/
	#c64color_palette = [ (0, 0, 0), (255, 255, 255), (158, 59, 80), (133, 233, 209), (163, 70, 182), (93, 195, 94), (61, 51, 191), (249, 255, 126), (163, 98, 33), (103, 68, 0), (221, 121, 138), (86, 89, 86), (138, 140, 137), (182, 253, 184), (140, 128, 255), (195, 195, 193) ] # My original DV capture palette
	
	
	# Import window variables and functions
	c64color_paletteswitches = [True] * len(c64color_palette)
	
	# Dither choices and data
	dither_method = [1, 'Posterize', 'Add Matrix', 'Triangular', 'Custom+'] 
	dither_pattern =  [1, 'Bayer', 'Ordered', 'Simple', 'Lines']
	dither_pattern_data = ([(0),(1)], # Dummy, not used
					 [ (0, 8/16.0, 2/16.0, 10/16.0),
					  (12/16.0, 4/16.0, 14/16.0, 6/16.0),
					  (3/16.0, 11/16.0, 1/16.0, 9/16.0),
					  (15/16.0, 7/16.0, 13/16.0, 5/16.0),
					  ] ,
					[ (0.1, 0.8, 0.1, 0.6),
					 (0.9, 0.3, 0.9, 0.2),
					 (0.3, 0.6, 0.4, 0.6),
					 (0.8, 0.2, 0.9, 0.3),
					 (0.1, 0.6, 0.1, 0.7),
					 (0.9, 0.4, 0.9, 0.1),
					 (0.3, 0.6, 0.4, 0.6),
					 (0.7, 0.1, 0.9, 0.4),
					 ] ,
					 [ (0.2, 0.8),
					   (0.8, 0.2),
					 ] ,
					 [ (0.9, 0.8),
					   (0.1, 0.2),
					   (0.9, 0.8),
					   (0.2, 0.1),
					 ],  )
	
	# Conversion options
	# "gamma_options" balances and gamma corrects the RGB values. 
	# Makes color comparison a lot more accurate, but is also slower. 
	gamma_options = [1, 'Gamma On', 'Gamma Off']
	gamma_value = 2.4
	crop_options = [1, 'Crop', 'Fit']
	antialias_options = [1, 'Nearest', 'Antialias']
	aspect_options = [1, 'PAL aspect', '1:1 aspect'] # NTSC to be added later (hopefully)
	#lumabalance = [0.299, 0.587, 0.114]
	#lumabalance = [1-0.299, 1-0.587, 1-0.114]
	#lumabalance = [0.9, 0.7, 1.0] # First testvalues
	#lumabalance = [0.9, 1.0, 0.7]
	#lumabalance = [1.0, 1.0, 1.0] # Debug
	dither_distance = 0
	dither_range = 0.5
	dither_distance_range = dither_distance * dither_range
	
	# Replacement colors
	#replacecolors = [
	#	((0,90,0), 'green'),
	#	]
				
	blendcolors = [
		# Blue gradient
		('black','blue'),
		('blue','lightblue'),
		('lightblue','cyan'),
		('cyan','white'),
		
		# Red gradient
		('black','brown'),
		('brown','red'),
		('red','orange'),
		('orange','pink'),
		('pink','lightgrey'),
		('lightgrey','white'),
		
		# Grey gradient
		('black','darkgrey'),
		('darkgrey','grey'),
		('grey','lightgrey'),
		('lightgrey','yellow'),
		('yellow','white'),
		
		# Green gradient
		('darkgrey','green'),
		('green','lightgreen'),
		('lightgreen','white'),
		
		# Other transitions
		#('brown','green'),
		#('blue','green'),
		
		('blue','purple'),
		('purple','red'),
		
		#('black','red'),
		#('red','pink'),
		#('pink','white'),
		('brown','orange'),
		('orange','yellow'),
		#('lightgrey','yellow'),
		#('lightblue','green'),
		#('green','grey'),
		#('grey','cyan'),
		]
		
	#graddistances = list()
	
	# This will hold the gamma converted c64 palette
	c64color_palette_gamma = list()
	
	# This will hold the master conversion palette
	conversionpalette = list()
	
	# This function builds the master conversion palette by appending all 
	# the color variants (single, replacements and gradients)
	@staticmethod
	def build_conversion_palette():
		Settings.conversionpalette = list()
		Settings.c64color_palette_gamma = list()
		
		for c in range(0, len(Settings.c64color_palette)):
			color = srgb_to_linear(Settings.c64color_palette[c], Settings.gamma_value)
			Settings.c64color_palette_gamma.append((color))
			if Settings.c64color_paletteswitches[c]:
				Settings.conversionpalette.append((color, 'base'))
		
		if Settings.dither_method[0] > 2:
			for grad in Settings.blendcolors:
				index1 = Settings.c64color_names.index(grad[0])
				index2 = Settings.c64color_names.index(grad[1])
				if Settings.c64color_paletteswitches[index1] == True and Settings.c64color_paletteswitches[index2] == True:
					color1 = Settings.c64color_palette_gamma[index1]
					color2 = Settings.c64color_palette_gamma[index2]
					mix_color = ( (color1[0] + color2[0]) *0.5,
								  (color1[1] + color2[1]) *0.5,
								  (color1[2] + color2[2]) *0.5 )
					mix_distance = colordistance(color1, color2)
					Settings.conversionpalette.append((mix_color, 'mix', mix_distance, grad[0], grad[1]))
					
					#print('Precalc mix color ' + grad[0] + '>' + grad[1] + ' with distance ' + str(mix_distance) + '.')
		
		#print (str(Settings.conversionpalette))
		return True
		
	# This function calculates the least distance among the palette colors.
	# It is used for scaling the dither for the two-color method
	@staticmethod
	def calculate_least_distance():
		least_distance = 255
		for c in Settings.conversionpalette:
			for b in Settings.conversionpalette:
				if c != b and c[1] == 'base' and b[1] == 'base':
					dist = colordistance(c[0], b[0])
					if dist < least_distance:
						least_distance = dist
		Settings.dither_distance = least_distance * 2.0
		Settings.dither_distance_range = Settings.dither_distance * Settings.dither_range
		print ('Least distance is: ' + str(Settings.dither_distance))
		return True
		
	@staticmethod
	def calculate_average_distance():
		sum_distance = 0
		colorcounter = 0
		for c in Settings.conversionpalette:
			for b in Settings.conversionpalette:
				if c != b and c[1] == 'base' and b[1] == 'base':
					dist = colordistance(c[0], b[0])
					sum_distance = sum_distance + dist
					colorcounter = colorcounter + 1
		Settings.dither_distance = sum_distance / colorcounter
		Settings.dither_distance_range = Settings.dither_distance * Settings.dither_range
		print ('Average distance is: ' + str(Settings.dither_distance))
		return True
