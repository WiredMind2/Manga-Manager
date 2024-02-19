from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
import os
import shutil
import ssl
import time
from tkinter import messagebox, filedialog
from urllib.parse import parse_qs, unquote_plus, urlparse
import argparse

HOSTNAME = "127.0.0.1"
SERVERPORT = 8000
SSL_CERT = None
MANGA_ROOT = None
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'server_config.json')
CACHE_DURATION = 60*60 # 1 hour

class Server(BaseHTTPRequestHandler):
	def do_GET(self):
		parsed = urlparse(self.path)
		# query = parse_qs(parsed.query)
		# path = query['path']
		path = parsed.path

		if not hasattr(self, 'cached'):
			self.cached = {}

		date, data = self.cached.get(path, (None, None))
		if date is not None and date > time.time():
			self.wfile.write(data)
		
		try:
			if path == '/get_file':
				params = parse_qs(parsed.query)
				return self.get_file(params)
			
			elif path == '/mainpage':
				return self.mainpage()

			filepath = os.path.join(MANGA_ROOT, unquote_plus(path[1:])) # Skips first /

			parent_path = os.path.abspath(MANGA_ROOT)
			child_path = os.path.abspath(filepath)

			if os.path.commonpath([parent_path]) != os.path.commonpath([parent_path, child_path]):
				print('Escaped from the directory!')

				data = {
					'error': "Please don't hack me, here are all the links for the mangas, downloads will be faster from there",
					'url': "https://tetrazero.com/manga_manager/viewer/datalist.json"
				}
				
				self.send_response(403)
				self.send_header("Content-Type", 'application/json')
				self.end_headers()

				self.send(data)
				# self.wfile.write(json.dumps(data).encode('utf-8'))

			if os.path.isdir(filepath):
				self.list_folder(filepath)
			else:
				self.send_file(filepath)
		except ssl.SSLEOFError as e:
			print(f'Error: {e}')
			pass
	
	def do_OPTIONS(self):
		self.send_response(200)
		self.end_headers()

	def list_folder(self, path):
		if not os.path.exists(path):
			print('Folder not found:', path)
			self.send_error(404, 'Folder not found!')
		else:
			files = os.listdir(path)

			out = []
			for f in files:
				fp = os.path.join(path, f)
				if os.path.isdir(fp):
					# Check if there is at least one file in the subfolders
					if self.scan_for_file(fp):
						out.append(f)
				else:
					out.append(f)

			self.send_response(200)
			self.send_header("Content-Type", 'application/json')
			self.end_headers()

			self.send(out)
			self.cached[path] = (time.time() + CACHE_DURATION, out)
			# self.wfile.write(json.dumps(out).encode('utf-8'))

	def scan_for_file(self, root):
		# Should be a pretty efficient function to scan if there is at least one file a folder (or subfolder)
		folders = []
		for f in os.listdir(root):
			if '.' in f[1:]:
				# Has an extension, and not a hidden folder, so most likely a file
				return True
			else:
				path = os.path.join(root, f)
				if os.path.isdir(path):
					folders.append(path)
				elif os.path.isfile(path):
					return True
				else:
					# Not a directory and not a file?? wtf shouldn't happen
					pass
		for path in folders:
			if self.scan_for_file(path):
				return True
			# Otherwise just loop
		
		# If you're here, then there are no files
		return False

	def send(self, obj, use_json=True):
		if use_json:
			json.dump(obj, FilelikeBytes(self.wfile))
		else:
			self.wfile.write(obj)

	def send_file(self, path):
		if not os.path.exists(path):
			print('File not found:', path)
			self.send_error(404, 'File not found!')
		else:
			self.send_response(200)
			filetype = mimetypes.guess_type(path)[0] or '*/*'
			self.send_header("Content-Type", filetype)
			self.end_headers()

			with open(path, 'rb') as f:
				shutil.copyfileobj(f, self.wfile)
			# chunk_size = 1024
			# with open(path, 'rb') as f:
			# 	while True:
			# 		chunk = f.read(chunk_size)
			# 		if not chunk: 
			# 			break
			# 		self.wfile.write(chunk)
			# 		# self.wfile.write(f.read())

	def get_file(self, params):
		manga = params.get('manga')
		if manga is None:
			return self.list_folder(MANGA_ROOT)

		else: # Manga
			manga_path = os.path.join(MANGA_ROOT, manga[0], "images")
			chapter = params.get('chapter')
			if chapter is None:
				return self.list_folder(manga_path)

			else: # Chapter
				mangas = os.listdir(manga_path)
				chapter_index = int(chapter[0])-1
				if chapter_index >= len(mangas):
					self.send_error(404, 'Chapter not found!')
					return

				chapter_path = os.path.join(manga_path, mangas[chapter_index])
				image = params.get('image')
				if image is None:
					return self.list_folder(chapter_path)

				else: # Images
					images = os.listdir(chapter_path)
					index = int(image[0])
					if index >= len(images):
						self.send_error(404, 'Image not found!')
						return

					image_path = os.path.join(chapter_path, images[index])
					data = os.path.relpath(image_path, MANGA_ROOT)

					self.send_response(200)
					self.send_header("Content-type", 'application/json')
					self.end_headers()

					# self.wfile.write(json.dumps(data).encode('utf-8'))
					self.send(data)
					
	def mainpage(self):
		
		out = []

		for manga in os.listdir(MANGA_ROOT):
			path = os.path.join(MANGA_ROOT, manga)
			if os.path.isdir(path):
				chapters = len(os.listdir(os.path.join(path, 'images')))
				out.append((manga, chapters))

		self.send_response(200)
		self.send_header("Content-Type", 'application/json')
		self.end_headers()

		self.send(out)
		self.cached['/mainpage'] = (time.time() + CACHE_DURATION, out)

	def end_headers(self):
		# Override self.end_headers to add more headers
		
		self.send_header("Access-Control-Allow-Origin", "*")
		self.send_header("Access-Control-Allow-Headers", "*")

		super().end_headers()

class FilelikeBytes:
	"""Wraps a file-like objet, but convert any string in .write() to bytes"""
	def __init__(self, stream) -> None:
		self.stream = stream
	
	def read(self, *args, **kwargs):
		return self.stream(*args, **kwargs)
	
	def write(self, data):
		return self.stream.write(data.encode('utf-8'))

def load_settings():
	keys = ('HOSTNAME', 'SERVERPORT', 'SSL_CERT', 'MANGA_ROOT')
	if os.path.exists(SETTINGS_PATH):
		with open(SETTINGS_PATH, 'r') as f:
			settings = json.load(f)

			for key in keys:
				value = settings.get(key, None)
				if value:
					globals()[key] = value

def save_settings():
	keys = ('HOSTNAME', 'SERVERPORT', 'SSL_CERT', 'MANGA_ROOT')
	settings = {key: globals().get(key, None) for key in keys}
	with open(SETTINGS_PATH, 'w') as f:
		json.dump(settings, f, indent=4)

def parseArgs():
	parser = argparse.ArgumentParser(description='Manga remote server for https://tetrazero.com')
	
	parser.add_argument('--use_ssl', type=int, choices=[0, 1],
                    help='Use either the http or the https protocol\n0=False / 1=True')
	
	args = parser.parse_args()
	use_ssl = args.use_ssl
	if use_ssl is None:
		use_ssl = True
	elif use_ssl in (0, 1):
		use_ssl = bool(use_ssl)
	else:
		raise ValueError('--use_ssl must be either 0 or 1')
	
	return use_ssl

def main():
	global MANGA_ROOT, SSL_CERT
	use_ssl = parseArgs()
	load_settings()

	if MANGA_ROOT is None:
		path = None
		while not path:
			path = filedialog.askdirectory(title="Please select your mangas directory")

		MANGA_ROOT = path
		
	if use_ssl and SSL_CERT is None:
		has_cert = messagebox.askyesno(title="SSL keys", message="Do you have a cert.pem file?")
		if has_cert:
			path = filedialog.askopenfilename(title="Please select your cert.pem file", filetypes=[('.pem file', '*.pem')])
			if path:
				SSL_CERT = path
	
	save_settings()

	webServer = HTTPServer((HOSTNAME, SERVERPORT), Server)
	
	if use_ssl:
		print('Using ssl socket')
		if SSL_CERT is not None:
			try:
				context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

				context.load_cert_chain(certfile=SSL_CERT)
			except ssl.SSLError:
				print('Error while loading the cert.pem file, ignoring')
			else:
				webServer.socket = context.wrap_socket(webServer.socket, server_side=True)

	url = "http://%s:%s" % (HOSTNAME, SERVERPORT)
	print(f"Server started {url}")

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		# Stopped
		pass

if __name__ == "__main__":
	main()