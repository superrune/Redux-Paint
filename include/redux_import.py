#!python3

from PIL import Image
from os.path import basename, splitext
from include.redux_settings import Settings
from include.redux_functions import *
import ui

class ImportWindow(ui.View):
	def __init__(self, filename):
		# Variables for conversion
		self.filename = filename
		imgname = splitext(basename(filename))[0]
		self.img = scale_img(Image.open(self.filename).convert('RGBA'), 
				Settings.antialias_options[0], Settings.actualWidth, Settings.height,
				Settings.aspect_options[0], Settings.crop_options[0]) # Open as PIL image
		self.working = False
		
		buttcol = color_to_1(Settings.c64color_palette[12])
		backcol = color_to_1(Settings.c64color_palette[11])
		textcol = 'white'
		#coltwo = 210
		#self.selectedImage = ''
		
		label = ui.Label(frame=(0, 0, self.width, 64), flex='w',font=('HelveticaNeue-Light', 32),
				alignment=ui.ALIGN_CENTER, text='Converting "' + imgname + '"')
		label.name = 'title_label'
		label.text_color = textcol #buttcol
		self.add_subview(label)
		
		#self.frame = (100, 100, 640, 480)
		self.width = 660 # coltwo at 320 required a width of 640
		self.height = 530
		self.center = (ui.get_screen_size()[0]*0.5,ui.get_screen_size()[1]*0.5)
		self.name = 'Image Conversion'
		self.border_width = 2
		self.border_color = buttcol
		self.background_color = backcol
		self.corner_radius = 16
		#self.flex = 'LRTB'
		
		self.filePreview = ui.ImageView(frame=(20,64,300,200))
		self.filePreview.content_mode = ui.CONTENT_SCALE_TO_FILL
		self.add_subview(self.filePreview)
		
		self.convertPreview = ui.ImageView(frame=(340,64,300,200))
		self.convertPreview.background_color = 'black'
		#self.convertPreview.action = image_hls_adjust
		self.convertPreview.content_mode = ui.CONTENT_SCALE_TO_FILL
		self.add_subview(self.convertPreview)
		
		
		# Invisible button over preview window
		self.convertbutton = ui.Button(name='Refresh', frame=(360,84,260,160), action=self.refreshpreview)
		#self.convertbutton.background_color = 'red'
		self.add_subview(self.convertbutton)
		
		
		# Palette buttons
		palbutt_start = 20
		palbutt_end = 640
		palbutt_pad = 10.0
		palbutt_width = (palbutt_end-palbutt_start-(palbutt_pad*(len(Settings.c64color_palette))))/(len(Settings.c64color_palette)+1)
	
		buttcol = color_to_1(Settings.c64color_palette[12])
		backcol = color_to_1(Settings.c64color_palette[11])
		textcol = 'white'
	
		#print ('palbutt_width: ' + str(palbutt_width))
		for c in range(0, len(Settings.c64color_palette)):
			startpos = palbutt_start+(c*palbutt_width)+(c*palbutt_pad)
			
			palbutt = build_button(self, str(c), palbutt_width, (startpos,275), self.toggle_palette, buttcol, backcol, textcol)
			if Settings.c64color_paletteswitches[c] == True:
				palbutt.title = ''
			else:
				palbutt.title = 'X'
			if c == 0:
				palbutt.tint_color = 'white'
			else:
				palbutt.tint_color = 'black'
			palbutt.background_color = color_to_1(Settings.c64color_palette[c])
		
		# Reset palette button
		self.reset_palette = build_button(self, 'R', palbutt_width, (640-palbutt_width,275), self.resetpalette, buttcol, backcol, textcol)
		
		# Image adjustments
		startline = 320	
		self.button_contrast = build_button(self, 'CON', 50, (20,startline), self.resetvalues, buttcol, backcol, textcol)
		self.slider_contrast = ui.Slider(frame=(80,startline,240,32), action=self.image_hls_adjust, value=0.5)
		self.slider_contrast.continuous = True
		self.add_subview(self.slider_contrast)
		
		self.button_brightness = build_button(self, 'BRT', 50, (20,startline+40), self.resetvalues, buttcol, backcol, textcol)
		self.slider_brightness = ui.Slider(frame=(80,startline+40,240,32), action=self.image_hls_adjust, value=0.5)
		self.slider_brightness.continuous = True
		self.add_subview(self.slider_brightness)
		
		self.button_saturation = build_button(self, 'SAT', 50, (20,startline+80), self.resetvalues, buttcol, backcol, textcol)
		self.slider_saturation = ui.Slider(frame=(80,startline+80,240,32), action=self.image_hls_adjust, value=0.5)
		self.slider_saturation.continuous = True
		self.add_subview(self.slider_saturation)
		
		# Transform options
		startline = 480 #320	
		self.button_crop = build_button(self, Settings.crop_options[Settings.crop_options[0]], 90, (20, startline), self.toggle_options, buttcol, backcol, textcol)
		self.button_crop.name = 'crop'
		self.button_antialias = build_button(self, Settings.antialias_options[Settings.antialias_options[0]], 90, (125,startline), self.toggle_options, buttcol, backcol, textcol)
		self.button_antialias.name = 'antialias'
		self.button_aspect = build_button(self, Settings.aspect_options[Settings.aspect_options[0]], 90, (230,startline), self.toggle_options, buttcol, backcol, textcol)
		self.button_aspect.name = 'aspect'
		
		# Conversion options
		startline = 320
		self.ditherbutton = build_button(self, Settings.dither_method[Settings.dither_method[0]], 90, (340,startline), self.setdither, buttcol, backcol, textcol)
		self.ditherpatternbutton = build_button(self, Settings.dither_pattern[Settings.dither_pattern[0]], 90, (440,startline), self.setdither_pattern, buttcol, backcol, textcol)
		self.gamma_optionsbutton = build_button(self, Settings.gamma_options[Settings.gamma_options[0]], 90, (540,startline), self.setgamma_options, buttcol, backcol, textcol)
		
		# Dither range
		startline = startline + 40
		self.button_range = build_button(self, 'RNG', 50, (340,startline), self.resetvalues, buttcol, backcol, textcol)
		self.slider_range = ui.Slider(frame=(400,startline,240,32), action=self.set_dither_range, value=Settings.dither_range)
		self.add_subview(self.slider_range)
		
		startline = startline + 40
		self.autoupdatebutton = ui.Switch(frame=(340,startline,128,32))
		self.add_subview(self.autoupdatebutton)
		self.autoupdatelabel = ui.Label(frame=(400,startline,200,32), text='Auto update preview', text_color=textcol)
		self.add_subview(self.autoupdatelabel)
		
		startline = 480
		self.importbutton = build_button(self, 'Import', 100, (420,startline), self.send_to_editor, buttcol, backcol, textcol)
		self.cancelbutton = build_button(self, 'Cancel', 100, (540, startline), self.close_importwindow, buttcol, backcol, textcol)
		
		
		# Load the image into the preview window
		self.image_hls_adjust(self.slider_contrast)
		self.refreshpreview(self.convertbutton)
		
		#self.filePreview.image = ui.Image.named(filename)
	
	def image_hls_adjust(self, sender):
		#if sender.superview.working == True:
		#	print ('Already working. Skipping.') # This check does not work
		#	return False
		#sender.superview.working = True
		
		contrast = sender.superview.slider_contrast.value*2
		brightness = sender.superview.slider_brightness.value*2
		saturation = sender.superview.slider_saturation.value*2
		img = filter_img(sender.superview.img, contrast=contrast, brightness=brightness, saturation=saturation)
		sender.superview.filePreview.image = pil_to_ui(img)
		
		#print (str(sender))
		#print (str(sender.superview.filename))
		#sender.superview.working = False
		return True
	
	@ui.in_background
	def refreshpreview(self, sender):
		start = time()
		self.image_hls_adjust(sender)
		Settings.build_conversion_palette()
		Settings.calculate_least_distance()
		print('Converting with ' + str(len(Settings.conversionpalette)) + ' colors. Distance range is ' + str(Settings.dither_distance_range))
		
		loadimg = ui_to_pil(sender.superview.filePreview.image)
		if sender.superview.convertPreview.image == None:
			previmg = loadimg.copy()
		else:
			previmg = ui_to_pil(sender.superview.convertPreview.image)
		
		for c in range (0, int(loadimg.height/10)):
			startline = c*10
			endline = (c+1)*10

			img = convert_c64(loadimg, Settings.conversionpalette, Settings.gamma_value, Settings.c64color_palette_gamma, Settings.c64color_names, Settings.dither_method[0], Settings.dither_pattern_data, Settings.dither_pattern, Settings.dither_distance_range, Settings.dither_range, startline=startline, endline=endline)
			
			cropimg = img.crop((0,startline, img.width, endline))
			previmg.paste(cropimg, (0,startline))
			if endline < previmg.height:
				for xcoord in range(0, previmg.width):
					previmg.putpixel((xcoord, endline+1), (255,255,255))
			sender.superview.convertPreview.image = pil_to_ui(previmg)
			
		end = time()
		print('Conversion complete in ' + str(end-start)[:4] + ' seconds.')
		return True
	
	def resetpalette(self, sender):
		for c in range(0, len(Settings.c64color_paletteswitches)):
			Settings.c64color_paletteswitches[c] = True
			sender.superview[str(c)].title = ''
		return True
																												
	def resetvalues(self, sender):
		if sender.name == 'CON':
			sender.superview.slider_contrast.value = 0.5
		elif sender.name == 'BRT':
			sender.superview.slider_brightness.value = 0.5
		elif sender.name == 'SAT':
			sender.superview.slider_saturation.value = 0.5
		elif sender.name == 'RNG':
			sender.superview.slider_range.value = 0.5
			Settings.dither_range = 0.5
			Settings.dither_distance_range = Settings.dither_distance * Settings.dither_range
			return True
		self.image_hls_adjust(sender)
		return True
	
	def toggle_options(self, sender):
		if sender.name == 'crop':
			button_options = Settings.crop_options
		elif sender.name == 'antialias':
			button_options = Settings.antialias_options
		elif sender.name == 'aspect':
			button_options = Settings.aspect_options
		curindex = button_options.index(sender.title)
		# Move to next index
		curindex = curindex + 1
		if curindex > len(button_options)-1:
			curindex = 1
		button_options[0] = curindex
		sender.title = button_options[curindex]
		# Update the file window
		sender.superview.img = scale_img(Image.open(self.filename).convert('RGBA'), 
				Settings.antialias_options[0], Settings.actualWidth, Settings.height,
				Settings.aspect_options[0], Settings.crop_options[0])
		self.image_hls_adjust(sender.superview['CON'])
		return True
	
	
	def toggle_palette(self, sender):
		if Settings.c64color_paletteswitches[int(sender.name)] == False:
			sender.title = ''
			Settings.c64color_paletteswitches[int(sender.name)] = True
		else:
			sender.title = 'X'
			Settings.c64color_paletteswitches[int(sender.name)] = False
		#print (str(Settings.c64color_paletteswitches))
		return True
	
	def setdither(self, sender):
		if Settings.dither_method[0] == len(Settings.dither_method)-1:
			Settings.dither_method[0] = 1
		else:
			Settings.dither_method[0] += 1
		sender.title = Settings.dither_method[Settings.dither_method[0]]
		return True
	
	def setdither_pattern(self, sender):
		if Settings.dither_pattern[0] == len(Settings.dither_pattern)-1:
			Settings.dither_pattern[0] = 1
		else:
			Settings.dither_pattern[0] += 1
		sender.title = Settings.dither_pattern[Settings.dither_pattern[0]]
		return True
	
	def set_dither_range(self, sender):
		Settings.dither_range = sender.value
		Settings.dither_distance_range = Settings.dither_distance * Settings.dither_range
		#print ('value: ' + str(sender.value) + ', dither_distance_range: ' + str(Settings.dither_distance_range))
		return True
				
	def setgamma_options(self, sender):
		# gamma_options = [1, 'Gamma On', 'Gamma Off']
		if Settings.gamma_options[0] == 2:
			# Setting gamma to on
			Settings.gamma_options[0] = 1
			Settings.gamma_value = 2.2
		else:
			Settings.gamma_options[0] = 2
			Settings.gamma_value = 1.0
		print('Gamma set to: ' + str(Settings.gamma_value))
		sender.title = Settings.gamma_options[Settings.gamma_options[0]]
		return True
	
	def send_to_editor(self, sender):
		# Convert UI image to PGN
		base = basename(self.filename )
		new_name = splitext(base)[0]
		import_filename = 'temp/' + new_name + '.png'
		
		img = ui_to_pil(sender.superview.convertPreview.image)
		
		scalefilter = Image.NEAREST
		img = img.resize((Settings.width, Settings.height), scalefilter)
		
		print ('img: ' + str(img))
		print ('import_image: ' + import_filename)
		print ('img.size:' + str(img.size))
		img.save(import_filename, 'PNG')
		
		self.superview['File window'].importfile(import_filename)
		self.superview['debugtext'].text = 'Importing ' + import_filename
		
		self.superview.remove_subview(self)
		return True
																		
	def close_importwindow(self, sender):
		self.superview.remove_subview(self)
		return True





'''
# Load and convert
v = pixelEditor()
v.present('fullscreen')
'''

#v = ImportWindow('../Redux Paint Testing/7eleven.jpg')
#v = ImportWindow('../Redux Paint Testing/testgrad.jpg')
#v.present()
