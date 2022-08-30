from concurrent.futures import thread
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
import os
import queue
import threading
from urllib.parse import parse_qs, urlparse

from manga_scan_downloader import MangaDownloader, IteratorDownloader

hostName = "localhost"
serverPort = 80

class Server(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			parsed = urlparse(self.path)
			path = parsed.path
			params = parse_qs(parsed.query)

			if path == '/':
				# Root
				if len(params) == 0:
					self.send_file('index.html')
				else:
					self.parse_command(params)

			elif os.path.exists(self.get_filepath(path)):
				# Get file
				self.send_file(self.get_filepath(path))
			else:
				# Invalid request
				print('Not found:', path)
				self.send_error(404, 'Not found!')
		except Exception as e:
			self.send_error(500, str(e))

	def do_POST(self):
		try:
			parsed = urlparse(self.path)
			path = parsed.path
			params = parse_qs(parsed.query)
			# TODO - Might be too big to read all at once
			data = self.rfile.read(int(self.headers['Content-Length']))
			data = json.loads(data)
			params['POST_DATA'] = data

			if path == "/":
				if len(params) == 0:
					return self.do_GET()
				else:
					self.parse_command(params)
			else:
				self.send_error(400, 'You cannot POST here')
		except Exception as e:
			self.send_error(500, str(e))

	def parse_command(self, params):
		action = params.get('action')
		if action:
			actions = {
				'start': self.start_thread,
				'stop': self.stop_thread,
				'logs': self.get_logs,
				'download': self.download
			}
			func = actions.get(action[0])
			if func:
				func(**params)
			else:
				self.send_error(400, f'{action[0]} is an invalid action')

	def send_file(self, path):
		if not os.path.exists(path):
			print('Not found:', self.path)
			self.send_error(404, 'Not found!')
		else:
			self.send_response(200)
			filetype = mimetypes.guess_type(path)[0] or '*/*'
			self.send_header("Content-type", filetype)
			self.end_headers()

		with open(path, 'rb') as f:
			self.wfile.write(f.read())
	
	def get_filepath(self, path):
		return os.path.normpath(os.path.dirname(__file__) + path)

if __name__ == "__main__":
	import webbrowser
	webServer = HTTPServer((hostName, serverPort), Server)
	url = "http://%s:%s" % (hostName, serverPort)
	print(f"Server started {url}")

	webbrowser.open(url)

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass