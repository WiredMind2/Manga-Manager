import logging
import os
import queue
import threading
import zipfile

from manga_data import data_list
from downloaders import *

class IteratorDownloader:
	def __init__(self, url, fields):
		self.url, self.fields = url, fields

		self.que = queue.Queue()
		self.archive_event = threading.Event()
		self.archive_thread = None
		self.stop = False
		self.threads = []
		self.avoid = {}

		if USE_DDL == "selenium":
			dll = SeleniumDownloader
		elif USE_DDL == "requests":
			dll = RequestsDownloader

		root, img_folder = self.prepare_files()

		with dll() as self.downloader:
			self.init_threads(img_folder, root)

			for f in self.iterator():
				url = self.url.format(**f)
				file = self.get_filename(f)

				path = os.path.join(img_folder, file)
				args = (url, path, f)

				self.que.put(args)
			for i in range(max(1, MAX_THREADS)):
				self.que.put("STOP")

			self.download_all()
			self.create_archives(img_folder, root)

			self.finish()

	def __enter__(self):
		pass

	def __exit__(self, *args):
		return True

	def init_threads(self, img_folder, root):
		self.archive_thread = threading.Thread(
			target=self.archive_thread_worker, args=(img_folder, root), daemon=True)
		self.archive_thread.start()

		if USE_THREADS:
			for i in range(MAX_THREADS):
				t = threading.Thread(
					target=self.dll_thread_worker, daemon=True)
				t.start()
				self.threads.append(t)

	def dll(self, url, path, f, h={}):
		if not os.path.exists(path):
			if f['chapter'] in self.avoid and self.avoid[f['chapter']] < f['episode']:
				return "OUT"

			if self.stop:
				return "OUT"

			if LOG_DDL:
				logging.info(f"Downloading: {url}")
			try:
				r = self.downloader.get(url, h=h, decode=False)
			except requests.exceptions.HTTPError as e:
				if e.response is not None and e.response.status_code == 404:
					if f['chapter'] in self.avoid:
						if self.avoid[f['chapter']] > f['episode']:
							self.avoid[f['chapter']] = f['episode']
					else:
						logging.info(f"Completed chapter: {f['chapter']}")
						self.avoid[f['chapter']] = f['episode']

					return "OK"
				else:
					logging.warning(f"Error on url: {url} - {e}")
					if isinstance(e, requests.exceptions.NewConnectionError):
						return "CANCEL"
					return "ERROR"
			except Exception as e:
				logging.warning(f"Error on url: {url} - {e}")
			else:
				with open(path, 'wb') as file:
					file.write(r)

			return "OK"

	def dll_thread_worker(self):
		while True:
			data = self.que.get()
			if data == "STOP":
				return
			status = self.dll(*data)
			if status == "OK":
				self.archive_event.set()
			elif status == "RETRY":
				self.que.put(data)
			elif status == "CANCEL":
				self.stop = True
				break

	def create_archives(self, img_folder, root):
		files = os.listdir(img_folder)

		for chap, max_eps in list(self.avoid.items()):
			complete = True
			for eps in range(self.fields['episode'][0], max_eps):
				file = self.get_filename(
					{'': fields['title'], 'chapter': chap, 'episode': eps})
				if file not in files:
					complete = False
					break
			if complete:  # All files have been downloaded
				archive_path = os.path.join(
					root, "archives", f'{self.fields["title"]}-{chap}.cbz')
				if not os.path.exists(archive_path):
					if LOG_ARCHIVE:
						logging.info(f"Writing archive: {archive_path}")
					with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as z:
						eps_padding = len(str(max_eps))
						for eps in range(self.fields['episode'][0], max_eps):
							file = f"{fields['title']}-chapter{str(chap).zfill(4)}-episode{str(eps).zfill(eps_padding)}.jpg"
							path = os.path.join(img_folder, file)
							z.write(path, arcname=file)

	def archive_thread_worker(self, *args):
		while not self.stop:
			self.archive_event.wait()
			self.create_archives(*args)
		self.create_archives(*args)

	def download_all(self):
		if not USE_THREADS:
			self.dll_thread_worker()

	def prepare_files(self):
		root = os.path.join(OUTPUT, "iterator")
		if not os.path.exists(root):
			os.mkdir(root)

		for sub in ("images", "archives"):
			path = os.path.join(root, sub)
			if not os.path.exists(path):
				os.mkdir(path)

		img_folder = os.path.join(root, "images")

		return root, img_folder

	def get_filename(self, arg):
		return "-".join("".join(map(str, e)) for e in arg.items()) + ".jpg"

	def iterator(self):
		for chap in range(self.fields['chapter'][0], self.fields['chapter'][1]+1):
			for ep in range(self.fields['episode'][0], self.fields['episode'][1]+1):
				yield {'': fields['title'], 'chapter': chap, 'episode': ep}

	def finish(self):
		if len(self.threads) == 0:
			return

		for t in self.threads:
			t.join()

		logging.info("Everything downloaded!")

		self.stop = True
		self.archive_thread.join()

if __name__ == "__main__":
	url = "https://lelscans.net/mangas/fairy-tail/{chapter:02d}/{episode}.jpg"
	url = "https://lelscans.net/mangas/solo-leveling/{chapter}/{episode}.jpg"
	fields = {
		"title": "Solo-Leveling",
		"chapter": (1, 179),
		"episode": (1, 100)
	}

	with IteratorDownloader(url, fields) as i:
		pass