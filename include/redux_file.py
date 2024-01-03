#!python3

import ui
import console
import ImageChops
import ImageOps
from dialogs import share_image, pick_document
from photos import pick_asset, get_assets
from glob import iglob, glob
from os.path import isfile, isdir, getctime, basename, exists, splitext
from os import mkdir, listdir, remove, rename
from shutil import copy2, copytree, rmtree, copyfile
from objc_util import ObjCInstance
from PIL import Image
#from images2gif import writeGif # Missing from latest Pythonista

from include.redux_settings import Settings
from include.redux_import import ImportWindow
from include.redux_functions import *

class FileWindow(ui.View):
	def __init__(self):
		buttcol = color_to_1(Settings.c64color_palette[12])
		backcol = color_to_1(Settings.c64color_palette[11]) #'black'
		textcol = 'white' #color_to_1(Settings.c64color_palette[6]) #'black'
		coltwo = 210
		self.selectedImage = ''
		
		#self.frame = (100, 100, 640, 480)
		self.width = 560 # coltwo at 320 required a width of 640
		self.height = 480
		#self.superview.width, self.superview.height
		
		self.center = (ui.get_window_size()[0]*0.5,ui.get_window_size()[1]*0.5)
		#self.center = (self.superview.width*0.5,self.superview.height*0.5)
		#self.center = self.superview['editor'].center
		#print (str(self.center) + " " + str(ui.get_screen_size()))
		#print (str(ui))
		self.name = 'File window'
		self.border_width = 2
		self.border_color = buttcol
		self.background_color = backcol
		self.corner_radius = 16
		self.flex = 'LRTB'
		
		self.sizeMult = 3
		self.scanlineStrength = 0.2
		
		label = ui.Label(frame=(0, 0, self.width, 64), flex='w', font=('HelveticaNeue-Light', 32),
				alignment=ui.ALIGN_CENTER, text='File Operations')
		label.name = 'title_label'
		label.text_color = textcol #buttcol
		self.add_subview(label)
		
		#self.imagefiles = [basename(x) for x in glob(Settings.image_location + '*.png')]
		#self.imagefiles.sort(key=str.lower)
		self.update_filelist()
		
		filelistData = ui.ListDataSource(self.imagefiles)
		filelistData.tableview_cell_for_row = self.tableview_cell_for_row
		filelistData.highlight_color = 'red'
		filelistData.delete_enabled = False
		
		self.filelist = ui.TableView(frame=(10, 64 ,coltwo-20, 400), data_source=filelistData, name='filelist')
		self.filelist.row_height = 24
		self.filelist.corner_radius = 6
		self.filelist.delegate = self
		self.filelist.separator_color = self.filelist.bg_color = buttcol #'black' #backcol
		self.add_subview(self.filelist)
				
		self.filePreview = ui.ImageView(frame=(coltwo,64,300*1.1,200*1.1))
		#self.filePreview.background_color = (0.2, 0.2, 0.2, 1.0)
		#self.filePreview.border_width = 1
		#self.filePreview.border_color = 'white'
		self.filePreview.content_mode = ui.CONTENT_SCALE_TO_FILL
		self.add_subview(self.filePreview)
		
		#self.previewSlider = ui.Slider(frame=(320,64+200+4,300-32,24))
		#self.previewSlider.value = 1.0
		#self.add_subview(self.previewSlider)
		
		def build_button(button_name, button_width, button_pos, button_action, button_img):
			mybutt = ui.Button(name=button_name, title=button_name)
			#new_button.background_image = (ui.Image.named('icons/'+button_img)))
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
		
		# First group of buttons
		butt_x, butt_y = (coltwo, 300)
		butt_width = 82
		load_button = build_button('Load', butt_width*2, (butt_x,butt_y), self.load, 'tool_load.png')
		new_button = build_button('New', butt_width, (butt_x+(butt_width*2),butt_y), self.new, 'tool_new.png')	
		import_button = build_button('Import', butt_width, (butt_x+(butt_width*3), butt_y), self.importfiles, 'tool_rename.png')
		
		rename_button = build_button('Rename', butt_width, (butt_x, butt_y+32), self.rename, 'tool_rename.png')
		duplicate_button = build_button('Duplicate', butt_width, (butt_x+(butt_width),butt_y+32), self.duplicate, 'tool_delete.png')
		camroll_button = build_button('Photos', butt_width, (butt_x+(butt_width*2), butt_y+32), self.importphoto, 'tool_rename.png')
		delete_button = build_button('Delete', butt_width, (butt_x+(butt_width*3),butt_y+32), self.deletefile, 'tool_delete.png')
		
		# Second group of buttons, share buttons
		butt_x, butt_y = (coltwo, 400)
		#butt_width = 76
		share_button = build_button('Share', butt_width, (butt_x,butt_y), self.save_clean, 'tool_share.png')
		sharecrt_button = build_button('Share CRT', butt_width, (butt_x+(butt_width*1),butt_y), self.save_crt, 'tool_sharecrt.png')
		koala_button = build_button('.koa', butt_width, (butt_x++(butt_width*2),butt_y), self.save_koala, 'tool_koa.png')
		program_program = build_button('.prg', butt_width, (butt_x+(butt_width*3),butt_y), self.save_program, 'tool_prg.png')
		
		# Share image with correct aspect plus optional scale and scanlines
		butt_x, butt_y = (coltwo, 432)
		shareaspect_button = build_button('Share PAL', butt_width, (butt_x,butt_y), self.save_multiply_aspect, 'tool_share.png')
		
		self.slider_size = ui.Slider(frame=(butt_x+(butt_width),butt_y,butt_width,32), action=self.set_scale_multiplier, value=0.5)
		self.add_subview(self.slider_size)
		
		self.slider_scanlines = ui.Slider(frame=(butt_x+(butt_width*2),butt_y,butt_width,32), action=self.set_scanline_strength, value=self.scanlineStrength)
		self.add_subview(self.slider_scanlines)
		
		gif_button = build_button('.gif', butt_width, (butt_x++(butt_width*3),butt_y), self.save_gif, 'tool_koa.png')
		gif_button.enabled = False # This button does not work in the latest Pythonista
		
		ui.delay(self.init_filepreview,0.01)
		
	#def layout(self):
	#	print('File operations layout placeholder')
	#	return True
	
	def set_scale_multiplier(self, sender):
		minScale = 2
		maxScale = 4
		newScale = minScale + ((maxScale - minScale)*sender.value)
		
		self.sizeMult = int(newScale)
		self.superview['debugtext'].text = 'Output scale set to ' + str(self.sizeMult)
		return True
	
	def set_scanline_strength(self, sender):
		self.scanlineStrength = sender.value
		self.superview['debugtext'].text = 'Scanline strength set to ' + str(self.scanlineStrength)
		return True
	
	def init_filepreview(self):
		editorimage = self.superview['editor'].imageName + '.png'
		self.filePreview.image = ui.Image.named(Settings.image_location + editorimage)
		current_index = self.imagefiles.index(editorimage)
		self.filelist.selected_row = (0,current_index)
		self.selectedImage = editorimage
		
	def tableview_did_select(self, tableview, section, row):
		imageFile = tableview.data_source.items[row]
		self.selectedImage = imageFile
		#self.filePreview.background_color = 'red'
		self.filePreview.image = ui.Image.named('images/'+ imageFile)
		self.superview['debugtext'].text = 'Previewing ' + str(imageFile)
	
	def tableview_cell_for_row(self, tableview, section, row):
		cell = ui.TableViewCell()
		
		#cell.content_view.bg_color = None
		#cell.content_view.alpha = 1
		cell.bg_color = color_to_1(Settings.c64color_palette[12])
		
		#cell.content_view.bg_color = None
		#cell.content_view.alpha = 0
		#cell.bg_color = None
		
		# None of these work!
		self.highlight_color = 'red'
		cell.content_view.highlight_color = 'red'
		cell.highlight_color = 'red'
		#print ('bgview: ', str(cell.selected_background_view))
		#cell.selected_background_view.bg_color = 'red'
		
		cell.text_label.text = str(self.imagefiles[row])
		cell.text_label.text_color = 'white'
			
		return cell
		
	def update_filelist(self):
		self.imagefiles = [basename(x) for x in glob(Settings.image_location + '/*.png')]
		self.imagefiles.sort(key=str.lower)
		try:
			self.filelist.data_source.items = self.imagefiles
		except:
			print("Filelist updated outside of UI")
		
	def load(self,sender):
		#print (sender.name)
		#print (sender.superview['filelist'].data_source.items)
		base_name = pngstrip(self.imagefiles[self.filelist.selected_row[1]])
		file_name = "images/" + base_name + '.png'
		if isfile(file_name):
			self.superview['editor'].imageName = base_name
			#print ('Imagename set to "'+ self.superview['editor'].imageName + '"')
			#if self.superview['editor'].zoomState is True:
			#	self.superview['ToolbarView'].zoom(sender)
			self.superview['editor'].loadimage(file_name)
			self.superview['debugtext'].text = 'Loaded ' + base_name
			return True
	
	@ui.in_background
	def new(self, sender):
		if self.superview['editor'].has_image():
			trashMsg = 'Are you sure you want to clear the editor?'
			if console.alert(trashMsg, '', 'Yes', hide_cancel_button=False) == 1:
				image_name = console.input_alert('New Image', '', 'myimage', 'Create New')
				print ('New name returned:' + image_name)
				self.superview['editor'].reset()
				self.superview['editor'].imageName = image_name
				#self.superview['editor'].autosave()
				self.superview['editor'].remove_subview(self.superview['File window'])
		else:
			self.show_error()
	
	@ui.in_background
	def rename(self, sender):
		current_name = pngstrip(self.selectedImage)
		if current_name == '':
			console.hud_alert('You need to select a file first.', 'error')
			return False
		else:
			new_name = console.input_alert('Rename Image', '', current_name, 'Rename Image')
			#print ('Rename returned: ' + str(new_name))
			if new_name+'.png' in self.imagefiles:
				console.hud_alert('Name already exists. Aborting operation.', 'error')
				return False
			else:
				# Rename image file and folder (if it exists)
				rename(Settings.image_location + current_name + '.png', 
						Settings.image_location + new_name + '.png')
				if exists(Settings.image_location + current_name):
					rename(Settings.image_location + current_name, 
						Settings.image_location + new_name)
				# Update list
				self.update_filelist()
				
		return True
	
	@ui.in_background
	def duplicate(self, sender):
		current_name = pngstrip(self.selectedImage)
		if current_name == '':
			console.hud_alert('You need to select a file first.', 'error')
			return False
		else:
			new_name = console.input_alert('Duplicate Image', '', current_name + '_copy', 'Duplicate Image')
			#print ('Rename returned: ' + str(new_name))
			if new_name+'.png' in self.imagefiles:
				console.hud_alert('Name already exists. Aborting operation.', 'error')
				return False
			else:
				# Rename image file and folder (if it exists)
				copy2(Settings.image_location + current_name + '.png', 
						Settings.image_location + new_name + '.png')
				if exists(Settings.image_location + current_name):
					copytree(Settings.image_location + current_name, 
						Settings.image_location + new_name)
				# Update list
				self.update_filelist()
				
		return True
	
	
	@ui.in_background
	def importphoto(self, sender):
		photo_asset = pick_asset(assets=get_assets(),title='Select image for import', multi=False)
		
		if str(photo_asset) == 'None':
			print ('No image selected. Canceling import.')
		else:
			if photo_asset.media_type == 'image':
				# Previous method crashes now. Using a temporary (I hope) workaround.
				#pngdata = ui.Image.from_data(photo_asset.get_image_data().getvalue())
				import_photo = photo_asset.get_image()
				import_photo.save('temp/import_photo.jpg')
				
				pngdata = ui.Image.named('temp/import_photo.jpg')
				
				base = str(ObjCInstance(photo_asset).filename())
				new_name = splitext(base)[0]
				
				while new_name+'.png' in self.imagefiles:
					new_name = console.input_alert('Rename Image', 'Image with an identical name already exists, please rename this image to import it.', new_name, 'Rename')
				
				copied_file = 'temp/' + new_name + splitext(base)[1]
				with open(copied_file,'wb') as f:
					f.write(pngdata.to_png())
				
				iw = ImportWindow(copied_file)
				self.superview.add_subview(iw)
				
			else:
				print ("Not a photo, canceling import.")
				
		
	@ui.in_background
	def importfiles(self, sender):
		picked_file = pick_document(types=['public.data'])
		print('Attempting to import:' + str(picked_file))
		
		if picked_file != None:
			if picked_file.endswith(('.png','.gif','.jpg','.jpeg','.tif','.tiff','.tga','.bmp')):
				base = basename(picked_file)
				new_name = splitext(base)[0]
				while new_name+'.png' in self.imagefiles:
					new_name = console.input_alert('Rename Image', 'Image with a similar name already exists, please rename this image to import it.', new_name, 'Rename')
								
				copied_file = 'temp/' + new_name + splitext(base)[1]
				copyfile(picked_file, copied_file)
				iw = ImportWindow(copied_file)
				
				self.superview.add_subview(iw)
				
			elif picked_file.endswith('.koa'):
				console.hud_alert('Koala can not be imported (yet).', 'error')
				return False
					
			else:
				console.hud_alert('Unsupported file format.', 'error')
				return False
			
			
	def importfile(self, import_file):
		print (import_file)
		
		base = basename(import_file)
		new_name = splitext(base)[0]
		
		# Todo: Should always be PNG, so lets check to be sure
		copyfile(import_file, Settings.image_location + base)
								
		self.superview['editor'].imageName = new_name
		#print ('Imagename set to "'+ self.superview['editor'].imageName + '"')
		#if self.superview['editor'].zoomState is True:
		#	self.superview['ToolbarView'].zoom(sender)
		self.superview['editor'].loadimage(import_file)
		self.superview['debugtext'].text = 'Imported ' + new_name
		self.update_filelist()
		
		#im = file_to_img(picked_file, Settings.actualWidth, height)
		#print (str(new_name) + ' has been resized to ' + str(im.size))
		#im.show()
		return True
		
		
	@ui.in_background
	def deletefile(self, sender):
		current_name = pngstrip(self.selectedImage)
		if current_name == '':
			console.hud_alert('You need to select a file first.', 'error')
			return False
		else:
			trashMsg = 'Are you sure you want to delete the file and its history?\n\nThis operation cannot be undone!'
			if console.alert('Delete Image', trashMsg, 'Yes'):
				# Rename image file and folder (if it exists)
				remove(Settings.image_location + current_name + '.png')
				if exists(Settings.image_location + current_name):
					rmtree(Settings.image_location + current_name)
				# Update list
				self.update_filelist()
				
		return True
																									
	@ui.in_background
	def save_koala(self, sender):
		self.superview['editor'].savebinary(fileFormat='koa')
	
	
	@ui.in_background
	def save_gif(self, sender):
		# Create GIF-animation from all images in folder
		current_name = pngstrip(self.selectedImage)
		image_location = Settings.image_location + current_name
		all_images = glob(image_location + '/*.png')
		all_images.sort(key=str.lower)
		
		# Todo: Find a way to reduce per minute frames
		kept_images = []
		for img in all_images:
			base_name = pngstrip(basename(img))
			if len(base_name) == 11:
				kept_images.append(img)
			else:
				foundMatch = False
				for kept in kept_images:
					if pngstrip(basename(kept))[:-2] == base_name[:-2] :
						foundMatch = True
				if foundMatch == False:
					# print (base_name[:-1])
					kept_images.append(img)
		
		print ('Image list reduced from ' + str(len(all_images)) + 
			' images to ' + str(len(kept_images)) + ' images.')
		
		if len(kept_images) != len(all_images):
			all_images = kept_images			
		
		gifname = current_name + '_progress_hour.gif'
		
		frames = []
		for img in all_images:
			new_img = Image.open(img).convert('RGB')
			new_img = self.multiply_aspect(new_img, self.sizeMult, self.scanlineStrength)
			frames.append(new_img)
		
		if len(frames) < 3:
			console.hud_alert('Not enough frames to create gif from "' + current_name + '".')
			return False
		
		# Duplicate the last frame
		for x in range(6):
			frames.append(frames[-1])
		
		writeGif(gifname, frames, 0.5)	
		sharemsg = console.open_in(gifname)
		remove(gifname)
		
		console.hud_alert('Successfully shared GIF animation.')
		
		return True
		
						
	@ui.in_background
	def save_program(self, sender):
		self.superview['editor'].savebinary(fileFormat='prg')
		
	def save_clean(self, sender):
		pixel_editor = self.superview['editor']
		if pixel_editor.has_image():
			saveimage = pixels_to_png(pixel_editor.background_color, 
					pixel_editor.pixels, pixel_editor.row*2, 
					pixel_editor.column)		
			sharemsg = share_image(saveimage)
			print ('Save_CRT returned: ' + str(sharemsg))
			#clipboard.set_image(image, format='png')
			console.hud_alert('Successfully shared PNG image.')
		else:
			self.show_error()
	
	
	def multiply_aspect(self,img, multiplier, scanline_strength):
		sizeMult = multiplier
		
		if sizeMult == 3:
			img = img.resize((Settings.width*8, Settings.height*8), Image.NEAREST)
			img = img.resize((int(Settings.width*sizeMult*Settings.aspectPAL), Settings.height*sizeMult), Image.ANTIALIAS)
		else:
			img = img.resize((Settings.width*sizeMult, Settings.height*sizeMult), Image.NEAREST)
			img = img.resize((int(Settings.width*sizeMult*Settings.aspectPAL), Settings.height*sizeMult), Image.ANTIALIAS)
		
		if scanline_strength > 0.0:
			# Create repeating data for crt overlay
			crt_img = Image.new("L", (1, Settings.height*sizeMult), 0)
			scanline_colour = int(255-(255*scanline_strength))
			imgdata = [255]*(sizeMult-1)
			imgdata.append(scanline_colour)
			imgdata = imgdata*Settings.height
			
			crt_img.putdata(imgdata)
			crt_img = crt_img.resize((int(Settings.width*sizeMult*Settings.aspectPAL), Settings.height*sizeMult), Image.NEAREST)
			crt_img = crt_img.convert("RGB")
			
			img = img.convert("RGB")
			img = ImageChops.multiply(img, crt_img)
		return img
	
	
	@ui.in_background
	def save_multiply_aspect(self, sender):
		sizeMult = self.sizeMult
		pixel_editor = self.superview['editor']
		if pixel_editor.has_image():
			saveimage = pixels_to_png(pixel_editor.background_color, 
					pixel_editor.pixels, pixel_editor.row*2, 
					pixel_editor.column)
			
			saveimage = self.multiply_aspect(saveimage, self.sizeMult, self.scanlineStrength)				
			sharemsg = share_image(saveimage)
			
			console.hud_alert('Successfully shared PNG image.')
		else:
			self.show_error()
			
	@ui.in_background
	def save_crt(self, sender):
		pixel_editor = self.superview['editor']
		if pixel_editor.has_image():
			# Scale image to match PAL aspect ratio
			saveimage = ui_to_pil(self.superview['preview'].image)
			
			saveimage = saveimage.resize((int(saveimage.width*Settings.aspectPAL), saveimage.height), Image.ANTIALIAS)
			
			sharemsg = share_image(saveimage)
			
			#print ('Save_CRT returned: ' + str(sharemsg))
			#photos.save_image(pil_to_ui(saveimage))
			
			console.hud_alert('Saved shared CRT preview.')
		else:
			self.show_error()

