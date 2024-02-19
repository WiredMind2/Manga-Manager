import base64
import hashlib
import multiprocessing
import queue
import threading


class Status():
	DOWNLOAD = 1  # (Status.DOWNLOAD, url, title)
	PARSE = 2  # (Status.PARSE, url, level)
	CHAPTER = 3  # (Status.CHAPTER, url, level)
	IMAGES = 4  # (Status.IMAGES, mainpage url, image url)


class EmptyQueue:
	# A dummy class simulating a queue,
	# useful if logging isn't necessary
	# (avoid storing endless amounts of logs forever)
	def __init__(self, empty=None):
		self.empty = empty

	def get(self, *args, **kwargs):
		return self.empty

	def put(self, *args, **kwargs):
		pass

	def empty(self):
		return True

	def join(self):
		pass


class Counter:
	# Thread-safe counter, used
	# for tracking alive threads
	def __init__(self, count=0, manager=None):
		if manager is None:
			manager = multiprocessing.Manager()
		self.lock = manager.Lock()
		self.counter = manager.Value('I', int(count))
		self.update_event = manager.Event()

	def __enter__(self):
		self.add()
		return self

	def __exit__(self):
		self.remove()

	def add(self, amount=1):
		# Add amount from the counter
		# amount can also be negative
		with self.lock:
			self.counter.value += amount
			self.update_event.set()

	def remove(self, amount=1):
		# Remove amount from the counter
		return self.add(-amount)

	def set(self, amount):
		# Set the counter to a specific amount
		with self.lock:
			self.counter.value = amount
			self.update_event

	def reset(self):
		# Reset counter to 0
		return self.set(0)

	def wait(self, amount=0):
		# Wait until the counter is greater than amount
		while self.counter.value <= amount:
			self.update_event.wait()

	def join(self):
		# Wait until the counter is zero
		while self.counter.value > 0:
			self.update_event.wait()

	def is_empty(self):
		with self.lock:
			return self.counter.value == 0


class dummyManager:
	# Dummy multiprocessing.Manager
	def __init__(self) -> None:
		pass

	def Queue(self,*args, **kwargs):
		return queue.Queue(*args, **kwargs)

	def Lock(self, *args, **kwargs):
		return threading.Lock(*args, **kwargs)

	def Value(self, *args, **kwargs):
		return DummyValue(*args, **kwargs)

	def Event(self, *args, **kwargs):
		return threading.Event(*args, **kwargs)

class DummyValue:
	# Dummy multiprocessing.Manager.Value
	def __init__(self, typecode, value) -> None:
		self.value = value


def returnProcess(que, func, args=[], kwargs={}):
	# Wrapper function to get a process with output
	p = multiprocessing.Process(
		target=queueFunction,
		args=(que, func, args, kwargs),
	)
	return p

def returnThread(que, func, args=[], kwargs={}):
	# Wrapper function to get a thread with output
	p = threading.Thread(
		target=queueFunction,
		args=(que, func, args, kwargs),
		name=f'returnThread-{func.__name__}'
	)
	return p

def queueFunction(que, func, args=[], kwargs={}):
	# Put function output in que, useful when used 
	# with threads or processes
	
	out = False
	try:
		out = func(*args, **kwargs)
	finally:
		que.put(out)

def queue_waiter(que, func, method='thread'):
	if method == 'func':
		pass
	else:
		if method == 'thread':
			p = threading.Thread(
				target=queue_waiter,
				args=(que, func, 'func'),
				name=f'Thread-{func.__name__}'
			)
		elif method == 'process':
			p = multiprocessing.Process(
				target=queue_waiter,
				args=(que, func, 'func'),
				name=f'Process-{func.__name__}'
			)
		else:
			raise Exception(f'Unknown method: {method}')
		p.start()
		return p

	while True:
		data = que.get()
		try:
			if data == "STOP":
				break
			else:
				stop = func(**data)
				
				if stop is False:
					break
		finally:
			que.task_done()


def b64_hash(url):
	return base64.b64encode(url.encode("utf-8")).decode().replace('/', '_')


def sha1_hash(url):
	return hashlib.sha1(url.encode("utf-8")).hexdigest()
