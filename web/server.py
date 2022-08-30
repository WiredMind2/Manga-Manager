#!/usr/bin/python3.7

import importlib
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from urllib.parse import parse_qs, urlparse, urlunparse
import webbrowser

# os.environ['REQUEST_URI'] = '/viewer/manga_viewer.py?action=manga_list'
# os.environ['REQUEST_METHOD'] = 'GET'

USE_CGI = 'REQUEST_URI' in os.environ

if USE_CGI:
	import cgi
	import cgitb
	cgitb.enable(logdir="./")
	# Disable pygame welcome message
	os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# else:
hostName = "localhost"
serverPort = 80

mapped_mimetypes = {
	'.html': 'text/html',
	'.js': 'text/javascript'
}

class BaseServer(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			parsed = urlparse(self.path)
			path = parsed.path
			params = parse_qs(parsed.query)

			filepath = self.get_filepath(path)
			
			if not os.path.exists(filepath):
				# Invalid request
				print('Not found:', path, filepath)
				return self.send_error(404, 'Not found!')

			if len(params) == 0:
				if os.path.isdir(filepath): # path[-1] == '/'
					# Folder root
					return self.send_file(self.get_filepath(path + 'index.html'))
				else:
					# Get file
					return self.send_file(self.get_filepath(path))
			else:
				return self.parse_command(params)

		except Exception as e:
			return self.send_error(500, str(e))

	def do_POST(self):
		try:
			parsed = urlparse(self.path)
			path = parsed.path
			params = parse_qs(parsed.query)
			filepath = self.get_filepath(path)

			if not os.path.exists(filepath):
				# Invalid request
				print('Not found:', path)
				return self.send_error(404, 'Not found!')

			params['POST_DATA'] = self.get_post_data
			
			if len(params) == 0:
				return self.do_GET()
			else:
				return self.parse_command(params)

		except Exception as e:
			self.send_error(500, str(e))

	def parse_command(self, params):
		action = params.get('action')
		if action:
			func = self.actions.get(action[0])
			if func:
				return func(self, **params)
			else:
				return self.send_error(400, f'{action[0]} is an invalid action')

	def send_file(self, path):
		if not os.path.exists(path):
			print('Not found:', path)
			self.send_error(404, 'Not found!')
		else:
			self.send_response(200)
	
			_, ext = os.path.splitext(urlparse(path).path)
			filetype = mapped_mimetypes.get(ext)
	
			if not filetype:
				filetype = mimetypes.guess_type(path)[0] or '*/*'
	
			self.send_header("Content-type", filetype)
			self.end_headers()

		with open(path, 'rb') as f:
			self.wfile.write(f.read())

	def send_json(self, data):
		self.send_response(200)
		self.send_header("Content-type", 'application/json')
		self.end_headers()

		data = json.dumps(data).encode('utf-8')
		self.wfile.write(data)

	def get_filepath(self, path):
		if path[0] != '/':
			path = '/' + path
		
		try:
			root = self.server_root
		except AttributeError:
			root = os.path.dirname(__file__)

		return os.path.normpath(root + path)

	def get_post_data(self, type_out='json'):
		# TODO - Might be too big to read all at once
		length = int(self.headers['Content-Length'])
		data = self.rfile.read(length)

		if type_out == 'bytes':
			return data
		elif type_out == 'json':
			data = json.loads(data)
			return data
		elif type_out == 'str':
			data = data.decode()
			return data

	# Map function for each action in the instance
	# This should be overriden in subclass
	actions = {}

class PluginServer(BaseServer):
	# Adds plugins support to BaseServer
	def do_GET(self):
		self.run_plugins('do_GET')

	def do_POST(self):
		self.run_plugins('do_POST')

	def import_from_path(self, path):
		head, tail = os.path.split(path)

		if os.path.isdir(path):
			module_name = tail
		else:
			if tail == '__init__.py':
				module_name = os.path.split(head)[1]
			else:
				module_name = tail.rsplit('.')[0]

		# Import spec from path
		spec = importlib.util.spec_from_file_location(module_name, path)
		# Import module from file
		module = importlib.util.module_from_spec(spec)
		# Add module to sys.modules
		sys.modules[spec.name] = module
		# Execute module
		spec.loader.exec_module(module)

		return module

	def load_plugins(self, root=None):
		# Search for plugins in subdirectories

		if root is None:
			# Avoid wrapping plugins in dict at root level
			root = os.path.dirname(__file__)
			module_root = os.path.split(root)[1]
			return self.load_plugins(root)[module_root]

		module_root = os.path.split(root)[1]
		plugin = None
		out = {}

		path = os.path.join(root, '__init__.py')
		if os.path.exists(path):
			module = self.import_from_path(path)
			if hasattr(module, 'plugin'):
				# out[module_root] = module.plugin
				plugin = module.plugin
				plugin.server_root = root

		for f in os.listdir(root):
			path = os.path.join(root, f)
			if os.path.isdir(path):
				plugins = self.load_plugins(path)
				if plugins:
					out |= plugins

		if not out and not plugin:
			# Nothing in this folder, ignore
			return {}

		return {module_root: (out, plugin)}

	def search_plugin(self, root, plugins=None):
		if root is None:
			return None, None

		if root.startswith('/'):
			root = root[1:]

		root_comp = root.split('/', 1)
		name = root_comp.pop(0)
		if root_comp:
			path = root_comp.pop(0)
		else:
			path = None

		if plugins is None:
			plugins = self.load_plugins()

		plugin = plugins[0].get(name)
		if plugin:
			sub, sub_path = self.search_plugin(path, plugin)
			if sub:
				# Found a plugin deeper
				return sub, '/' + name + sub_path
			elif plugin[1] is not None:
				# No plugin deeper, use the current one
				return plugin[1], '/' + name
			else:
				# No plugin found
				return None, None

		return None, None

	def run_plugins(self, command):
		parsed = urlparse(self.path)
		path = parsed.path
		params = parse_qs(parsed.query)

		plugin, plugin_path = self.search_plugin(path)
		if plugin:
			data = {key: val for key, val in self.__dict__.items() if key[0] != '_'}

			path = os.path.relpath(path, plugin_path)
			if path == '.':
				path = '/'
			
			
			plugin_parsed = parsed._replace(path=path)
			path = urlunparse(plugin_parsed)
			
			data['path'] = path

			# def init_override(self, request, client_address, server):
			# 	self.request = request
			# 	self.client_address = client_address
			# 	self.server = server
			# 	self.setup()

			# plugin.server.__init__ = init_override
			# instance = plugin.server(self.request, self.client_address, self.server)

			# force_keys = ('path',)

			# for key, value in data.items():
			# 	if key[0] != '_':
			# 		if key in force_keys or not hasattr(instance, key):
			# 			setattr(instance, key, value)

			if hasattr(plugin.server, command):
				func = getattr(plugin.server, command)
			else:
				print(f'Command not found on plugin, path {path}: {e}')
				return

			try:
				# out = func()
				func(self)
			except ConnectionAbortedError:
				print(f'ConnectionAbortedError: {path}')
				return
			except Exception as e:
				print(f'Error on plugin, path {path}: {e}')
			else:
				return
			# finally:
			# 	instance.finish()
		
		try:
			func = getattr(super(), command)
			func()
		except AttributeError:
			# Not defined
			pass

def cgi_wrapper(instance=None):
	instance = instance or PluginServer

	class CGIServerWrapper(PluginServer):
		def __init__(self):
			# data = cgi.parse()
			# form = cgi.FieldStorage()

			self.path = os.environ['REQUEST_URI']
			self.rfile = sys.stdin
			self.wfile = sys.stdout

			mname = 'do_' + os.environ['REQUEST_METHOD']

			method = getattr(self, mname)
			try:
				method()
			except Exception as e:
				print(f'Error on CGI wrapper - {mname}: {e}')
				raise

			self.wfile.flush()

		# def send_header(self, key, value):
		# 	self.wfile.write(f'{key}: {value}\n')

		# def end_headers(self):
		# 	self.wfile.write('\n')

	return CGIServerWrapper()

def start_server(address=None, instance=None, openInBrowser=False):
	if USE_CGI:
		return cgi_wrapper(instance=instance)
		
	if instance is not None:
		if not issubclass(instance, BaseHTTPRequestHandler):
			raise TypeError(f'{instance} is not a subclass of BaseHTTPRequestHandler!')
	else:
		instance = PluginServer

	if address is not None:
		if not isinstance(address, tuple, type(None)):
			raise TypeError('address must be a tuple')
	else:
		address = (hostName, serverPort)

	webServer = HTTPServer(address, instance)

	url = "http://%s:%s" % address
	print(f"Server started {url}")

	if openInBrowser:
		webbrowser.open(url)

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	print("Content-Type: text/plain")    # HTML is following
	print() 
	
	start_server()
