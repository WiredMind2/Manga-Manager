import ctypes
import hashlib
import json
import os
import re
import zipfile
from tkinter import filedialog as fd

try:
	from server import BaseServer, start_server
except ModuleNotFoundError:
	import sys
	sys.path.append(os.path.normpath(__file__ + '\\..\\..'))
	from server import BaseServer, start_server

import pygame

MANGA_ROOT = "~/Documents/webtoons"
MANGA_ROOT = os.path.normpath(os.path.expanduser(MANGA_ROOT))

class ViewerUtils():
	def __init__(self, files=None, root=None, save=None):
		self.savePath = save
		self.root = root

		self.current = None
		self.imgpos, self.pos = 0, 0

		self.save_data = {}
		self.get_files = None

		last = None
		if self.savePath is not None and os.path.exists(self.savePath):
			# Load last file from save data
			last, imgpos, pos = self.parseSave()
			if last is not None:
				# A file was saved
				self.root = os.path.dirname(last)
				self.get_files = lambda: [
					os.path.normpath(os.path.join(self.root, f))
					for f in os.listdir(self.root)
					if f.endswith('.cbz')
					or (os.path.isdir(os.path.join(self.root, f)) and len(os.listdir(os.path.join(self.root, f))))
				]
				self.current = last
				self.imgpos, self.pos = imgpos, pos

		if last is None:
			# No file in save data
			if files is not None:
				# Load files from args
				self.get_files = lambda: files

			elif root is not None:
				# Load files from dir in args
				self.get_files = lambda: [os.path.normpath(os.path.join(
					self.root, f)) for f in os.listdir(self.root) if f.endswith('.cbz')]

		# Get files
		self.opened_files = self.get_files() if self.get_files is not None else []

		if self.get_files is None or not self.opened_files:
			# No files opened, ask user to select a dir or some files
			while len(self.opened_files) == 0:
				path = self.file_prompt()
				if not path:
					break

		if len(self.opened_files) == 0:
			# If user refused to select files
			print('No files found!')
			return

		if self.current is None:
			self.current = self.opened_files[0]

	def parseSave(self):
		if not os.path.exists(self.savePath):
			return None, None
		with open(self.savePath, 'r') as f:
			self.save_data = json.load(f)
			last_hash = self.save_data['last']
			file, imgpos, pos = self.save_data[last_hash]
		imgpos, pos = int(imgpos), int(pos)
		return file, imgpos, pos

	def file_prompt(self):
		root = fd.askopenfilename(
			title='Select the folder containing the manga files (.cbz)', initialdir=os.path.expanduser('~'))

		try:
			self.open_file(root)
		except FileNotFoundError as e:
			print(f'Error while opening directory: {e}')

		return root

	def open_file(self, file):
		self.save()
		current = os.path.normpath(file)

		if os.path.isdir(current):
			root = current

			dir_hash = self.hash(os.path.normpath(current))
			file_hash = self.save_data.get(dir_hash, None)

			if file_hash is not None:
				current, imgpos, pos = self.save_data[file_hash]
			else:
				for f in os.listdir(root):
					if f.endswith('.cbz'):
						current = os.path.normpath(os.path.join(root, f))
						break
				else:
					# No call to break -> No file found
					raise FileNotFoundError(
						f'No .cbz file found for path {root}')
				imgpos, pos = 0, 0
		else:
			root = os.path.dirname(current)
			imgpos, pos = 0, 0

		self.root, self.current, self.imgpos, self.pos = root, current, imgpos, pos
		self.get_files = lambda: [os.path.normpath(os.path.join(
			self.root, f)) for f in os.listdir(self.root) if f.endswith('.cbz')]
		self.opened_files = self.get_files()

		self.save()

	def save(self):
		if self.savePath is None:
			return
		if os.path.exists(self.savePath):
			with open(self.savePath, 'r') as f:
				self.save_data = json.load(f)
		else:
			self.save_data = {
			}

		last_hash = self.hash(self.current)
		self.save_data['last'] = last_hash
		self.save_data[last_hash] = self.current, self.imgpos, self.pos

		dir_hash = self.hash(os.path.normpath(os.path.dirname(self.current)))
		self.save_data[dir_hash] = last_hash

		with open(self.savePath, 'w') as f:
			json.dump(self.save_data, f, indent=4)

	def hash(self, data):
		return hashlib.sha1(str(data).encode("utf-8")).hexdigest()


class LocalViewer(ViewerUtils):
	def __init__(self, files=None, root=None, save=None):
		super.__init__(files=files, root=root, save=save)

		self.width = None

		pygame.init()
		pygame.font.init()
		pygame.display.set_caption('Manga Reader')

		self.font = pygame.font.SysFont('Comic Sans MS', 20)

		scroll_off = 100
		scroll_off_continuous = scroll_off // 5

		# TODO - Top bar menu
		self.screen_pos = (0, 50)  # (0, 50)

		self.size = self.width, self.height = (500, 800)

		self.update_size()

		self.imgs = {}
		self.parse_file(self.current)

		if len(self.imgs[self.current]) == 0:
			print('No images found!')
			return
		img = self.imgs[self.current][0]
		self.size = self.width, self.height = img.width, self.height

		self.update_size()

		pressed = []

		self.update()

		self.fps = 60
		self.clock = pygame.time.Clock()

		running = True
		while running:
			self.clock.tick(self.fps)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.opened_files = self.get_files()
					if event.button == pygame.BUTTON_LEFT:
						self.next_file()
					elif event.button == pygame.BUTTON_RIGHT:
						self.last_file()
					elif event.button == pygame.BUTTON_WHEELUP:
						multiplier = 1
						if pygame.key.get_mods() & pygame.K_LCTRL:
							multiplier = 10
						self.pos = self.pos - scroll_off * multiplier
						self.update()
					elif event.button == pygame.BUTTON_WHEELDOWN:
						multiplier = 1
						if pygame.key.get_mods() & pygame.K_LCTRL:
							multiplier = 10
						self.pos = self.pos + scroll_off * multiplier
						self.update()
				elif event.type == pygame.VIDEORESIZE:
					self.size = self.width, self.height = event.w, event.h
					self.update_size()
					self.parse_file(self.current)
					self.update()
				elif event.type == pygame.DROPFILE:
					# Drag and drop a file
					self.open_file(event.file)
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RIGHT or event.key == pygame.K_SPACE:
						# Open next file
						self.next_file()
					elif event.key == pygame.K_LEFT:
						# Open precedent file
						self.last_file()
					elif event.key == pygame.K_o:
						# Prompt user for a new file / folder to open
						self.file_prompt()
					elif event.key == pygame.K_v:
						# User copy pasted a file
						if event.mod & pygame.KMOD_LCTRL:
							# get clipboard
							types = pygame.scrap.get_types()

							if 'FileName' in types:
								filename = pygame.scrap.get(
									'FileName')[:-1].decode()

								try:
									# TODO - Check when it's not needed
									filename = self.GetLongPathName(filename)
								except:
									pass

								self.open_file(filename)
					else:
						if False:
							print(event.key, [
								  k for k, v in pygame.__dict__.items() if v == event.key])
						if event.key not in pressed:
							pressed.append(event.key)
				elif event.type == pygame.KEYUP:
					if event.key in pressed:
						pressed.remove(event.key)
			# print(pressed)
			for key in pressed:
				multiplier = 1
				if pygame.key.get_mods() & pygame.K_LCTRL:
					multiplier = 10
				if key == pygame.K_UP:
					self.pos = self.pos - scroll_off_continuous * multiplier
					self.update()
				elif key == pygame.K_DOWN:
					self.pos = self.pos + scroll_off_continuous * multiplier
					self.update()

		self.save()

	def next_file(self):
		i = list(self.opened_files).index(self.current)
		if i+1 < len(self.opened_files)-1:
			self.save()
			self.current = list(self.opened_files)[i+1]
			self.parse_file(self.current)
			self.imgpos, self.pos = 0, 0
			self.update()

	def last_file(self):
		i = list(self.opened_files).index(self.current)
		if i-1 >= 0:
			self.save()
			self.current = list(self.opened_files)[i-1]
			self.parse_file(self.current)
			self.imgpos, self.pos = 0, 0
			self.update()

	def update(self):
		for img, pos in self.get_img_inview():
			size = (
				self.width,
				int(img.height*self.width/img.width)
			)
			if int(img.height*self.width/img.width) != img.height:
				img.update(pygame.transform.smoothscale(img.img, size))

			self.screen.blit(img.img, (0, pos))

		self.display.blit(self.screen, self.screen_pos)
		pygame.display.update(self.screen.get_rect(topleft=self.screen_pos))
		self.update_topbar()

	def update_topbar(self):
		self.topbar.fill("#FFFFFF")

		# Title text
		text = self.font.render(
			f'{os.path.basename(self.current)}', False, (0, 0, 0))
		self.topbar.blit(text, (10, 10))

		self.display.blit(self.topbar, (0, 0))
		pygame.display.update(self.topbar.get_rect(topleft=(0, 0)))

	def update_size(self):
		self.display = pygame.display.set_mode(
			(self.size[0], self.size[1]+self.screen_pos[1]), pygame.RESIZABLE)
		self.screen = pygame.Surface(self.size)
		self.topbar = pygame.Surface((self.size[0], self.screen_pos[1]))
		self.topbar.fill('#FFFFFF')

		if not pygame.scrap.get_init():
			pygame.scrap.init()

	def get_img_inview(self):
		i = 0
		imgs = self.imgs[self.current]

		if self.imgpos < 0:
			self.imgpos = 0
		elif self.imgpos > len(imgs)-1:
			self.imgpos = len(imgs)-1

		img = imgs[self.imgpos]

		while self.pos > img.height and self.imgpos < len(imgs)-1:
			self.pos -= img.height
			self.imgpos += 1
			img = imgs[self.imgpos]

		while self.pos < 0 and self.imgpos > 0:
			self.imgpos -= 1
			img = imgs[self.imgpos]
			self.pos += img.height

		if self.pos < 0 and self.imgpos == 0:
			self.pos = 0

		tmp_imgpos = self.imgpos
		tmp_pos = -self.pos
		out = []

		while tmp_pos < self.height and tmp_imgpos <= len(imgs)-1:
			img = imgs[tmp_imgpos]
			out.append((img, tmp_pos))
			tmp_pos += img.height
			tmp_imgpos += 1

		if tmp_pos < self.height and tmp_imgpos == len(imgs):
			self.pos -= self.height - tmp_pos
			return self.get_img_inview()

		return out

	def open_file(self, file):
		super().open_file(file)

		try:
			self.parse_file(self.current)
		except Exception as e:
			print('Error while parsing file:', e)

	def save(self):
		super().save()
		self.update()

	def parse_file(self, file):
		if file is None or not os.path.exists(file):
			return

		if not pygame.get_init():
			# Can't import images if pygame isn't initialized
			# Maybe force initialization here?
			return

		self.imgs[file] = []

		if os.path.isfile(file):
			with zipfile.ZipFile(file, 'r') as f:
				for name in f.namelist():
					img_file = f.open(name, 'r')

					# data = self.parseImg(img_file)
					data = Manga_Image(
						lambda img_file=img_file: self.parseImg(img_file))

					# if len(self.imgs[file]) > 0:
					# 	data['start'] = self.imgs[file][-1]['start'] + self.imgs[file][-1]['height']

					self.imgs[file].append(data)
		elif os.path.isdir(file):
			for name in sorted(os.listdir(file), key=lambda e: ''.join(map(lambda s: s.zfill(3) if s.isdigit() else '', e.split('-')))):
				img_file = open(os.path.join(file, name))

				data = Manga_Image(
					lambda img_file=img_file: self.parseImg(img_file))

				# if data is not None:
				# 	if len(self.imgs[file]) > 0:
				# 		data['start'] = self.imgs[file][-1]['start'] + self.imgs[file][-1]['height']

				self.imgs[file].append(data)

	def parseImg(self, img_file):
		if type(img_file) == pygame.Surface:
			img = img_file
		else:
			try:
				img = pygame.image.load(img_file).convert()
			except Exception as e:
				print(f'Error on image: {img_file} - {e}')
				return None

		if self.width is None:
			self.width = img.get_width()

		if img.get_width() != self.width:
			size = (
				self.width,
				int(img.get_height()*self.width/img.get_width())
			)
			img = pygame.transform.smoothscale(img, size)

		data = {
			'img': img,
			'height': img.get_height(),
			'width': img.get_width(),
			'start': 0
		}
		return img

	def GetLongPathName(self, path):
		GetLongPathName = ctypes.windll.kernel32.GetLongPathNameW
		buffer = ctypes.create_unicode_buffer(GetLongPathName(path, 0, 0))

		GetLongPathName(path, buffer, len(buffer))
		return buffer.value


class Manga_Image:
	def __init__(self, img):
		self.update(img)

	@property
	def height(self):
		if self._height is None:
			if self.img is None:
				self.img = self.caller()
			self._width, self._height = self.img.get_size()
		return self._height

	@property
	def width(self):
		if self._width is None:
			if self.img is None:
				self.img = self.caller()
			self._width, self._height = self.img.get_size()
		return self._width

	def update(self, img):
		if callable(img):
			self.caller = img
			self.img = None
			self._width, self._height = None, None
		else:
			self.img = img
			self._width, self._height = self.img.get_size()


class HTTPViewer(BaseServer):
	def get_image(self, **params):
		manga = params.get('manga')
		chapter = params.get('chapter')
		image = params.get('image')

		if not manga or not chapter or not image:
			return self.send_error(400, 'Invalid arguments')

		manga = manga[0]
		chapter = int(chapter[0])
		image = int(image[0])

		path = os.path.join(MANGA_ROOT, manga, 'images', f'Chapter {str(chapter).zfill(5)}')

		if not os.path.exists(path):
			return self.send_error(404)
		
		for img in os.listdir(path):
			if int(img.split('-', 1)[0]) == image:
				return self.send_file(os.path.join(path, img))

		return self.send_error(404)

	def parse_manga(self, params):
		manga = params.get('manga')

		if not manga:
			self.send_error(400, 'Please specify a manga')
			return False, False

		manga = manga[0]
		path = os.path.join(MANGA_ROOT, manga, 'images')
		if not os.path.exists(path):
			self.send_error(404)
			return False, False
		
		return manga, path

	def manga_data(self, **params):
		manga, path = self.parse_manga(params)
		if not manga:
			return 


		files = os.listdir(path)
		data = {
			'count': len(files),
			'chapters': {}
		}

		for f in files:
			# TODO - Error handling
			chapter = int(f.split(' ', 1)[1])

			imgs = os.listdir(os.path.join(path, f))

			data['chapters'][chapter] = len(imgs)

		return self.send_json(data)
		
	def manga_list(self, **params):
		out = []

		for manga in os.listdir(MANGA_ROOT):
			path = os.path.join(MANGA_ROOT, manga, 'images')
			if os.path.exists(path):
				data = {
					'title': manga,
					'url': f'?action=manga_info&manga={manga}',
					'picture': f'?action=manga_thumbnail&manga={manga}',
					'chapters_count': len(os.listdir(path))
				}

				out.append(data)

		return self.send_json(out)

	def manga_thumbnail(self, **params):
		manga, path = self.parse_manga(params)
		if not manga:
			return 

		for root, dirs, files in os.walk(path, topdown=True):
			for file in files:
				filepath = os.path.join(root, file)
				if os.path.isfile(filepath):
					_, ext = os.path.splitext(file)
					if ext in ('.jpg', '.png', '.webp'): # TODO - Add more ext?
						self.send_file(filepath)
						return 

	def manga_info(self, **params):
		# Return the info page
		
		manga, path = self.parse_manga(params)
		if not manga:
			return 
		
		self.send_response(200)
		self.send_header("Content-type", 'text/html')
		self.end_headers()

		with open(self.get_filepath('manga_info.html'), 'rb') as f:
			page = f.read()

			updated_page = re.sub(b'MANGA_TITLE = (null);', f'MANGA_TITLE = "{manga}";'.encode(), page)
			
			self.wfile.write(updated_page)

	def get_manga_info(self, **params):
		manga, path = self.parse_manga(params)
		if not manga:
			return 

		count = 0

		for file in os.listdir(path):
			filepath = os.path.join(path, file)
			if not os.path.isdir(filepath):
				continue

			try:
				idx = int(file.rsplit(' ', 1)[1])
			except:
				continue
			
			count += 1

		data = {
			'chapters': count, 
			'picture': f'?action=manga_thumbnail&manga={manga}',
			'title': manga
		}

		return self.send_json(data)

	def get_chapter(self, **params):
		manga, path = self.parse_manga(params)
		if not manga:
			return 

		chapter = params.get('chapter')
		if not chapter:
			self.send_error(400, 'Please specify a chapter')
			return False, False

		chapter = chapter[0]
		path = os.path.join(MANGA_ROOT, manga, 'images', f'Chapter {str(chapter).zfill(5)}')
		if not os.path.exists(path):
			self.send_error(404)
			return False, False

		img_count = len(os.listdir(path))

		data = {'title': manga, 'chapter': chapter, 'img_count': img_count}

		self.send_response(200)
		self.send_header("Content-type", 'text/html')
		self.end_headers()

		with open(self.get_filepath('manga_reader.html'), 'rb') as f:
			page = f.read()

			for k, v in data.items():
				page = re.sub(
					f'const MANGA_{k.upper()} = null;'.encode(), 
					f'const MANGA_{k.upper()} = "{v}";'.encode(), 
					page
				)
			
			self.wfile.write(page)
		
	actions = {
		'get_image': get_image,
		'manga_data': manga_data,
		'manga_list': manga_list,
		'manga_thumbnail': manga_thumbnail,
		'manga_info': manga_info,
		'get_manga_info': get_manga_info,
		'get_chapter': get_chapter
	}

	server_root = os.path.dirname(__file__)

server = HTTPViewer

if __name__ == "__main__":
	print("Content-Type: text/plain")    # HTML is following
	print() 
	# root = "C:/Users/moi/Documents/Series/Webtoons/Versatile Mage"
	# files = [os.path.normpath(os.path.join(root, f)) for f in os.listdir(root)]
	# LocalViewer(save="save_data.json")

	start_server(instance=HTTPViewer)