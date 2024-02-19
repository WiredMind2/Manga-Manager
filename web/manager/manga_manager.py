
import json
import os
import queue
import re
import threading

try:
	from manga_scan_downloader import MangaDownloader
	from iterator_downloader import IteratorDownloader
except ModuleNotFoundError:
	import sys
	sys.path.append(os.path.normpath(__file__ + '\\..\\..\\..'))
	from manga_scan_downloader import MangaDownloader
	from iterator_downloader import IteratorDownloader

try:
	from ..server import BaseServer, start_server
except ImportError:
	import sys
	sys.path.append(os.path.normpath(__file__ + '\\..\\..'))
	from server import BaseServer, start_server


MANGA_ROOT = "~/Documents/webtoons"
MANGA_ROOT = os.path.normpath(os.path.expanduser(MANGA_ROOT))

class ThreadWrapper:
	def __init__(self) -> None:
		# Start thread

		print('Created new thread')
		globals()['MANGA_THREAD'] = self

		self.started = False
		self.log_queue = queue.Queue()
		self.input_queue = queue.Queue()
		self.stop_event = threading.Event()
		self.thread = threading.Thread(target=self.thread)
	
	def start(self):
		self.thread.start()
		self.started = True

	def stop(self):
		self.stop_event.set()
		self.started = False

	def thread(self):
		downloader = MangaDownloader(log_queue=self.log_queue)

		while not self.stop_event.is_set():
			try:
				command, data = self.input_queue.get(block=True, timeout=1)
			except queue.Empty:
				pass
			else:
				try:
					getattr(downloader, command)(data)
				except Exception as e:
					print(f'Error on downloader: {e}')
					
					raise # For testing only
		
		print('Thread stopped')

	def get_logs(self, timeout=None):
		while not self.log_queue.empty():
			try:
				log = self.log_queue.get(block=True, timeout=timeout or 1)
			except queue.Empty:
				break
			else:
				yield log
	
	def call(self, command, data):
		self.input_queue.put((command, data))


class HTTPViewer(BaseServer):
	def find_thread(self, create=True):
		thread = globals().get('MANGA_THREAD')
		
		if create and thread is None:
			thread = self.start_thread(silent=True)
		
		return thread

	def start_thread(self, **kwargs):
		
		thread = self.find_thread(create=False)
		if thread is None or thread.started is False:
			thread = ThreadWrapper()
			thread.start()

		if not kwargs.get('silent'):
			self.send_response(200)
			self.send_header("Content-type", 'text/plain')
			self.end_headers()
			self.wfile.write(b'"Ok"')
		
		return thread
	
	def stop_thread(self, **kwargs):
		thread = self.find_thread(create=False)

		if thread is not None:
			thread.stop()
		
		if not kwargs.get('silent'):
			self.send_response(200)
			self.send_header("Content-type", 'text/plain')
			self.end_headers()
			self.wfile.write(b'"Ok"')

	def get_logs(self, **kwargs):
		thread = self.find_thread()

		data = list(thread.get_logs())

		self.send_response(200)
		self.send_header("Content-type", 'application/json')
		self.end_headers()

		data = json.dumps(data).encode('utf-8')
		self.wfile.write(data)

	def download(self, **kwargs):
		content_fetcher = kwargs.get('POST_DATA')
		
		content = content_fetcher()

		if not content:
			return

		thread = self.find_thread()

		thread.call('download', content)

		
		if not kwargs.get('silent'):
			self.send_response(200)
			self.send_header("Content-type", 'text/plain')
			self.end_headers()
			self.wfile.write(b'"Ok"')
	
	actions = {
		'start': start_thread,
		'stop': stop_thread,
		'logs': get_logs,
		'download': download
	}

	server_root = os.path.dirname(__file__)

server = HTTPViewer

if __name__ == "__main__":
	start_server(instance=HTTPViewer)
