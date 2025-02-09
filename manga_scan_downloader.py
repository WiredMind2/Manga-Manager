from datetime import datetime
import glob
import logging
import os
import re
import shutil
import sys
import threading
import time
from urllib.parse import urljoin, urlparse
import zipfile

import requests
import urllib3.exceptions

import constants
import downloaders
import parsers
import utils

USE_LOCAL_SERVER = sys.platform == 'win32'

if USE_LOCAL_SERVER:
	DATA_URL = "http://localhost:8080"
else:
	DATA_URL = "https://manga.tetrazero.com/viewer/datalist.json"


class MangaDownloader:
	def __init__(self, data_list=[], log_queue=None):
		if not os.path.exists(constants.OUTPUT):
			os.mkdir(constants.OUTPUT)

		self.image_threads, self.chapter_threads = [], []
		self.archive_thread, self.downloader_thread = None, None

		# File downloaded / Create archive event

		# self.manager = multiprocessing.Manager()
		self.manager = utils.dummyManager()
		self.image_queue = self.manager.Queue()
		self.chapter_queue = self.manager.Queue()
		self.archive_queue = self.manager.Queue()
		self.downloader_queue = self.manager.Queue()
		self.status_queue = log_queue or utils.EmptyQueue()

		self.LOG_DDL_last = time.time()
		self.LOG_DDL_count = 0

		self.hashes_path = os.path.abspath("website_hashes")
		if not os.path.exists(self.hashes_path):
			os.makedirs(self.hashes_path)

		if constants.USE_PARSER == "lxml":
			self.parser = parsers.LxmlParser()
		elif constants.USE_PARSER == "bs4":
			self.parser = parsers.Bs4Parser()

		# Start download threads
		self.init_threads()

		if data_list:
			self.download(data_list)

	def log(self, *args):
		self.status_queue.put(args)

	def fetch_datalist(self):
		r = requests.get(DATA_URL)
		data_list = r.json()
		self.download(data_list)

	def download(self, data_list, no_thread=False):
		if not data_list:
			return

		folders = []

		for data in data_list:
			try:
				folder = self.handle_data(data)
			except utils.ParseError:
				pass
			except Exception as e:
				# Should never reach here, but just in case, log the error
				logging.error(f'Unhandled error on url {data["url"]}: {e}')
				raise
			else:
				if folder:
					folders.append(folder)

		if constants.DELETE_UNKNOWN:
			logging.info("Deleting unknown folders")
			folders = set(folders)
			for sub in os.listdir(constants.OUTPUT):
				if sub not in folders:
					logging.warning(f'Unknown folder: {sub}')
					try:
						shutil.rmtree(os.path.join(constants.OUTPUT, sub))
					except Exception as e:
						logging.error(f'Couldn\'t delete folder: {sub}')

		self.stop_threads()

		logging.info("Done!")

	def __call__(self, data):
		return self.handle_data(data)

	def handle_data(self, manga):
		try:
			data = self.parse_main_page(manga)
		except utils.ParseError:
			raise

		title = data["title"]
		chapter_links = data["links"]

		if title is None:
			return

		# Prepare folder
		self.prepare_files(title)

		# Download started
		chapters_count = len(chapter_links)
		
		logging.info(
			f"{chapters_count} chapters found for manga: {title}, downloading..."
		)
		self.log(utils.Status.DOWNLOAD, manga["url"], title)

		#region Metadata
		# Handle metadata
		folder = os.path.normpath(
			os.path.join(constants.OUTPUT, title, "metadata")
		)  # This folder should already exists, it is created by .prepare_files()

		# Save source url
		source = manga["url"]
		if source is not None: # Yeah it's never None
			path = os.path.join(folder, "source.txt")

			if not os.path.exists(path):
				with open(path, "w", encoding='utf-8') as f:
					f.write(source)

		# Save description
		desc = data["desc"]
		if desc is not None:
			path = os.path.join(folder, "description.txt")

			if not os.path.exists(path):
				with open(path, "w", encoding='utf-8') as f:
					f.write(desc)

		# Download cover image
		cover_url = data["cover"]
		if cover_url is not None:
			path = os.path.join(folder, "cover.jpg")  # Use mimetype?

			if not os.path.exists(path):
				# Download image
				kwargs = {
					"url": cover_url,
					"path": path,
					"headers": manga.get("headers", {}),
					"cookies": manga.get("cookies", {}),
				}
				if constants.USE_THREADS:
					self.image_queue.put(kwargs)
				else:
					self.dll(**kwargs)

		#endregion

		# Parse chapter pages
		self.log(utils.Status.PARSE, manga["url"], 3, chapters_count)

		def natural_sort_key(s):
			# Sort filename without zero-padded numbers
			return [
				int(text) if text.isdigit() else text.lower()
				for text in re.split("([0-9]+)", s)
			]

		chapter_links = sorted(
			chapter_links.items(), key=lambda e: natural_sort_key(e[0])
		)

		threads = []
		self.last_log = time.time()
		for i, (idx, link) in enumerate(chapter_links):
			kwargs = {
				"title": title,
				"data": manga,
				"i": i,
				"idx": self.format_text(idx),
				"link": link,
				"chapters_count": chapters_count,
			}
			self.chapter_queue.put(kwargs)


		for t in threads:
			t.join()

		# Done parsing main page and all chapters pages
		self.log(utils.Status.PARSE, manga["url"], -1)

		return title # To keep track of known folders

	def handle_chapter(self, title, data, i, idx, link, chapters_count):
		# Parse one chapter
		chapter_data = self.parse_chapter(data, idx, link)

		if len(chapter_data) == 0:
			logging.warning(f"No data for chapter {i+1} - {title}")
			return

		if constants.LOG_PARSE and (time.time() - self.last_log > 5):
			# Log time in console
			logging.info(f"Parsed - {title}: {i+1} / {chapters_count}")
			self.last_log = time.time()

		# Initialize thread counter for archive thread
		counter = utils.Counter(manager=self.manager)

		folder = self.get_path(title, i, chapter_data[0]["path"])
		
		root, leaf = os.path.split(folder)
		paths = glob.glob(os.path.join(root, leaf[:7] + '*'))
		for path in paths:
			if path != folder:
				shutil.rmtree(path)
				pass

		# Download images
		for img_data in chapter_data:
			if img_data['url'] is None or img_data['url'] == '':
				continue

			self.log(utils.Status.IMAGES, link, img_data["url"], 0)

			# Get image path
			file = (
				self.format_text(img_data["desc"]) + ".jpg"
			)  # Maybe use mimetype instead?
			path = os.path.join(folder, file)

			# Create folder
			if not os.path.exists(folder):
				try:
					os.mkdir(folder)
				except Exception as e:
					# Can happen if two threads are trying to create the same folder
					print(f"Can't create folder {folder}: {e}")
					if not os.path.exists(folder):
						continue

			# Download image
			kwargs = {
				"url": img_data["url"],
				"path": path,
				"headers": data.get("headers", {}),
				"cookies": data.get("cookies", {}),
				"counter": counter,
			}
			counter.add()
			if constants.USE_THREADS:
				self.image_queue.put(kwargs)
			else:
				self.dll(**kwargs)

		if constants.CREATE_ARCHIVES:
			# Create archive
			kwargs = {
				"title": title,
				"images_path": folder,
				"chapter_idx": idx,
				"chapter_data": chapter_data,
				"chapters_count": chapters_count,
				"counter": counter,
			}
			if constants.USE_THREADS:
				self.archive_queue.put(kwargs)
			else:
				self.create_archives(**kwargs)

	def stop_threads(self):
		self.downloader_queue.join()

		self.chapter_queue.join()
		self.image_queue.join()
		if constants.CREATE_ARCHIVES:
			self.archive_queue.join()

		self.downloader_queue.put("STOP")
		self.downloader_thread.join()

		for i in range(constants.MAX_IMAGE_THREADS * 2):
			self.image_queue.put("STOP")

		def thread_filter(thread_list):
			return next(filter(lambda t: t.is_alive(), thread_list), None)

		thread = thread_filter(self.image_threads)
		while thread is not None:
			thread.join()
			thread = thread_filter(self.image_threads)

		for i in range(constants.MAX_CHAPTER_THREADS * 2):
			self.chapter_queue.put("STOP")

		thread = thread_filter(self.chapter_threads)
		while thread is not None:
			thread.join()
			thread = thread_filter(self.chapter_threads)

		if constants.CREATE_ARCHIVES:
			self.archive_queue.put("STOP")
			self.archive_thread.join()

		logging.info("Done downloading")

	def init_threads(self):
		# Start chapter parser threads
		for i in range(
			max(0, constants.MAX_CHAPTER_THREADS - len(self.chapter_threads))
		):
			t = threading.Thread(
				target=utils.queue_waiter,
				kwargs={
					"que": self.chapter_queue,
					"func": self.handle_chapter,
					"method": "func",
				},
				name=f"Thread-chapter_queue",
			)
			t.start()
			self.chapter_threads.append(t)

		# Start image downloader threads
		for i in range(max(0, constants.MAX_IMAGE_THREADS - len(self.image_threads))):
			t = threading.Thread(
				target=utils.queue_waiter,
				kwargs={"que": self.image_queue, "func": self.dll, "method": "func"},
				name=f"Thread-image_queue",
			)
			t.start()
			self.image_threads.append(t)

		if constants.CREATE_ARCHIVES and self.archive_thread is None:
			# Start archive creator threads
			t = threading.Thread(
				target=utils.queue_waiter,
				kwargs={
					"que": self.archive_queue,
					"func": self.create_archives,
					"method": "func",
				},
				name=f"Thread-archive_queue",
			)
			t.start()
			self.archive_thread = t

		if self.downloader_thread is None:
			# Start main downloader thread (for self.get())
			t = threading.Thread(
				target=utils.queue_waiter,
				kwargs={
					"que": self.downloader_queue,
					"func": self.get,
					"method": "func",
				},
				name=f"Thread-downloader_queue",
			)

			t.start()
			self.downloader_thread = t

	def prepare_files(self, title):
		root = os.path.join(constants.OUTPUT, title)
		if not os.path.exists(root):
			os.mkdir(root)

		folders = ["metadata", "images"]
		if constants.CREATE_ARCHIVES:
			folders.append("archives")

		for sub in folders:
			path = os.path.join(root, sub)
			if not os.path.exists(path):
				os.mkdir(path)

	def parse_main_page(self, data):
		if constants.LOG_PARSE:
			logging.info(f"Parsing url: {data['url']}")

		# Get main page
		self.log(utils.Status.PARSE, data["url"], 0)

		page = self.get(
			data["url"],
			h=data["headers"],
			force_url=True,
			no_cache=constants.RELOAD_MAIN,
		)
		if page is None:
			self.log(utils.Status.PARSE, data["url"], -1)
			return {}, None

		# Parse main page
		self.log(utils.Status.PARSE, data["url"], 1)

		try:
			out = self.parser.main_page(data, page)
		except utils.ParseError:
			raise

		out["title"] = self.format_text(out["title"])

		if not bool(urlparse(out['cover']).netloc):
			# Turn relative path into absolute path
			out['cover'] = urljoin(data['url'], out['cover'])

		# Done parsing main page
		self.log(utils.Status.PARSE, data["url"], 2)

		return out

	def parse_chapter(self, data, chapter_idx, chapter_link, no_cache=None):
		# Get chapter page
		self.log(utils.Status.CHAPTER, chapter_link, 0)

		chapter_page = None
		try:
			chapter_page = self.get(
				chapter_link,
				h=data["headers"],
				no_cache=no_cache or constants.RELOAD_MAIN,
			)
		except Exception as e:
			logging.error(f"{e} on chapter {chapter_link}")

		if chapter_page is None:
			# No page found, abort
			self.log(utils.Status.CHAPTER, chapter_link, -1)

			return []

		elif chapter_page == "":
			return self.parse_chapter(data, chapter_idx, chapter_link, True)

		# Parse chapter page
		self.log(utils.Status.CHAPTER, chapter_link, 1)

		# path = f'Chapter {str(chapter_idx).zfill(5)}'
		try:
			chapter_data = self.parser.chapter(chapter_page, chapter_idx, data)
		except Exception as e:
			logging.error(f"Error while parsing chapter, url: {chapter_link}: {e}")
			return []

		# Done parsing chapter page
		self.log(utils.Status.CHAPTER, chapter_link, -1)
		return chapter_data

	def get(self, url, h={}, force_url=False, no_cache=False, output=None):
		kwargs = {
			"url": url,
			"h": h,
			"force_url": force_url,
			"no_cache": no_cache,
		}

		thread = threading.current_thread()
		if thread.name != self.downloader_thread.name:
			# Send download to main download thread
			output = self.manager.Queue()
			kwargs["output"] = output

			self.downloader_queue.put(kwargs)
			out = output.get()
			return out

		if output is not None:
			# Create a waiter for response
			# Put data in output
			utils.queueFunction(output, self.get, kwargs=kwargs)
			return

		if constants.USE_CACHE and not no_cache:
			# Try to use cached data
			if constants.HASH_FUNCTION == "b64":
				url_hash = utils.b64_hash(url)
			elif constants.HASH_FUNCTION == "sha1":
				url_hash = utils.sha1_hash(url)

			# Compute path from hashed url
			path = os.path.join(self.hashes_path, url_hash)

			if os.path.exists(path):

				modif_time = os.path.getmtime(path)
				if time.time()-modif_time > constants.CACHE_AGE:
					os.remove(path)
				else:
					with open(path, "r", encoding="utf-8") as f:
						p = f.read()
					return p

		# Request data
		try:
			p = self.get_downloader().get(url, h, force_url=force_url)

		except Exception as e:
			logging.warning(f"Error while downloading (get) url: {url}: {e}")
			return None

		else:
			if constants.USE_CACHE:
				# Write new data to cache
				with open(path, "w", encoding="utf-8") as f:
					f.write(p)
			return p

	@classmethod
	def get_downloader(self):
		if hasattr(self, "downloader"):
			return self.downloader

		if constants.USE_DDL == "selenium":
			self.downloader = downloaders.SeleniumDownloader()
		elif constants.USE_DDL == "requests":
			self.downloader = downloaders.RequestsDownloader()
		return self.downloader

	@classmethod
	def dll(self, url, path, headers={}, cookies={}, counter=None, tentative=0):
		try:
			if not os.path.exists(path):
				if constants.LOG_DDL:
					if not hasattr(self, "LOG_DDL_count"):
						self.LOG_DDL_count = 0
						self.LOG_DDL_last = time.time()
					self.LOG_DDL_count += 1
					if time.time() - self.LOG_DDL_last > 5:
						timestamp = datetime.now().strftime("%H:%M:%S")
						logging.info(
							f"[{timestamp}] - Downloaded: {self.LOG_DDL_count} images - last img: '{path}'"
						)
						self.LOG_DDL_last = time.time()
						self.LOG_DDL_count = 0

				try:
					r = self.get_downloader().get(
						url, headers=headers, cookies=cookies, decode=False
					)
				except requests.exceptions.SSLError as e:
					logging.warning(
						f"SSL Error on url: {url} - {e} / Tentative {tentative}/{constants.MAX_TIMEOUT_RETRY}"
					)
					if tentative < constants.MAX_TIMEOUT_RETRY:
						return self.dll(
							url, path, headers, cookies, counter, tentative + 1
						)
				except urllib3.exceptions.SSLError as e:
					logging.warning(
						f"SSL Error on url: {url} - {e} / Tentative {tentative}/{constants.MAX_TIMEOUT_RETRY}"
					)
					if tentative < constants.MAX_TIMEOUT_RETRY:
						return self.dll(
							url, path, headers, cookies, counter, tentative + 1
						)
				except requests.exceptions.Timeout as e:
					logging.warning(
						f"Timeout Error on url: {url} - {e} / Tentative {tentative}/{constants.MAX_TIMEOUT_RETRY}"
					)
					if tentative < constants.MAX_TIMEOUT_RETRY:
						return self.dll(
							url, path, headers, cookies, counter, tentative + 1
						)
				except requests.exceptions.HTTPError as e:
					logging.warning(f"Http Error on url: {url} - {e}")
				except requests.exceptions.ConnectionError as e:
					if e.args and isinstance(
						e.args[0], urllib3.exceptions.ReadTimeoutError
					):
						logging.warning(
							f"Timeout Error on url: {url} - {e} / Tentative {tentative}/{constants.MAX_TIMEOUT_RETRY}"
						)
						if tentative < constants.MAX_TIMEOUT_RETRY:
							return self.dll(
								url, path, headers, cookies, counter, tentative + 1
							)
					else:
						logging.warning(f"Error Connecting on url: {url} - {e}")
				except requests.exceptions.RequestException as e:
					logging.warning(f"Error while downloading (ddl) url: {url} - {e}")
				except Exception as e:
					if url in str(e):
						logging.warning(f"Unknown error while downloading: {e}")
					else:
						logging.warning(f"Unknown error while downloading url: {url} - {e}")
				else:
					if constants.LOG_DDL_FULL:
						logging.info(f"Downloaded: {url}")

					with open(path, "wb") as f:
						f.write(r)
		finally:
			if counter is not None:
				counter.remove()

	@classmethod
	def get_path(self, title=None, index=None, chapter_path=None):
		out = [constants.OUTPUT]
		if title is not None:
			out.append(title)
			if index is not None:
				out.append('images')
				out.append(str(index).zfill(5) + " - " + self.format_text(chapter_path)) # chapter_data[0]["path"]
		
		return os.path.normpath(
			os.path.join(*out)
		)

	@classmethod
	def create_archives(
		self,
		title,
		images_path,
		chapter_idx,
		chapter_data,
		chapters_count,
		counter=None,
	):
		if not constants.CREATE_ARCHIVES:
			# In case archive creation is disabled
			return

		if len(chapter_data) == 0:
			# Ignore if no images found
			return

		if counter is not None:
			# counter.wait()  # Wait for at least one thread to start
			counter.join()  # Wait until all threads are done

		# Get archive path
		# archive_name = f'{title}-{chapter_idx.zfill(len(str(chapters_count)))}.cbz'
		archive_name = f"{title}-{chapter_idx}.cbz"
		archive_path = os.path.join(constants.OUTPUT, title, "archives", archive_name)

		# Create chapter folder and get existing files
		if not os.path.exists(images_path):
			try:
				os.mkdir(images_path)
			except FileExistsError:
				# Another thread has already created the folder
				pass
			files = set()
		else:
			files = set(os.listdir(images_path))

		# Check if all images exists
		complete = True
		for img_data in chapter_data:
			file = self.format_text(img_data["desc"]) + ".jpg"
			if file not in files:
				complete = False
				break

		# Check if all images have been downloaded
		if complete:
			# Create archive if not exists
			if os.path.exists(archive_path):
				validated = self.validate_archive(
					images_path, archive_path, chapter_data
				)
			else:
				validated = False

			if not validated:
				if constants.LOG_ARCHIVE:
					logging.info(
						f"Writing archive {chapter_idx}/{chapters_count}: {archive_path}"
					)

				with zipfile.ZipFile(
					file=archive_path,
					mode="w",
					compression=zipfile.ZIP_DEFLATED,
					allowZip64=True,
					compresslevel=9,
				) as z:
					padding = len(str(len(chapter_data)))
					for i, img_data in enumerate(chapter_data):
						file = self.format_text(img_data["desc"]) + ".jpg"
						path = os.path.join(images_path, file)
						arcname = str(i).zfill(padding) + ".jpg"
						z.write(path, arcname=arcname)

						# os.remove(path) - TODO - Image is redownloaded

		validated = self.validate_archive(images_path, archive_path, chapter_data)
		if not validated:
			logging.warning(f"Archive {archive_path} is invalid / corrupted!")

	@classmethod
	def validate_archive(self, images_path, archive_path, chapter_data):
		if len(chapter_data) == 0:
			# Ignore if no images found
			return False

		# Check if chapter folder exists
		if not os.path.exists(images_path):
			return False

		image_files = set(os.listdir(images_path))

		# Check if all images exists
		for img_data in chapter_data:
			file = self.format_text(img_data["desc"]) + ".jpg"
			if file not in image_files:
				return False

		# Check if archive exists
		if not os.path.exists(archive_path):
			return False

		try:
			with zipfile.ZipFile(file=archive_path, mode="r") as z:
				if len(chapter_data) != len(z.namelist()):
					return False
		except zipfile.BadZipFile:
			return False

		return True

	@classmethod
	def format_text(self, text):
		return (
			"".join(l for l in text if l.isalnum() or l in " _-.").rstrip(".").strip()
		)


if __name__ == "__main__":
	# for f in os.listdir(constants.OUTPUT):
	# 	path = os.path.join(constants.OUTPUT, f, 'archives')
	# 	for a in os.listdir(path):
	# 		os.remove(os.path.join(path, a))
	# 	os.rmdir(path)

	# pass

	if USE_LOCAL_SERVER:
		import data_server

		server = data_server.start_server(thread=True)

	try:
		dll = MangaDownloader()

		dll.fetch_datalist()
		# dll.download(data_list)
	finally:
		if USE_LOCAL_SERVER:
			data_server.stop_server()
			server.join()
