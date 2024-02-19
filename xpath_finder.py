import random
import socket

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class XpathFinder():
	def __init__(self):
		
		options = Options()
		options.add_argument("start-maximized")
		options.add_argument("--log-level=2")
		# options.add_experimental_option("excludeSwitches", ["enable-logging"])
		
		self.driver = webdriver.Chrome(service=Service(
			ChromeDriverManager().install()), options=options)
		self.driver.implicitly_wait(15)

		# executable_path = r'C:\Program Files\geckodriver\geckodriver.exe'
		# opts = webdriver.FirefoxOptions()
		# self.driver = webdriver.Firefox(executable_path=executable_path,options=opts)
		# self.driver.implicitly_wait(15)
	
	def find_element(self, url, elements):
		self.driver.get(url)
		xpaths = {}

		for elt in elements:
			kwargs = {'title': elt}

			with open('header.html', 'r') as f:
				header = f.read()
				header = header.format(**kwargs)

			with open('header.js', 'r') as f:
				js = f.read()

			port = random.randint(2000, 5000) # Random port
			self.driver.execute_script(js, header, port)
			value = self.socket_server(port)

			xpaths[elt] = value

		self.driver.close()
		return xpaths

	def socket_server(self, port):
		host = ''
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((host, port))
			s.listen(1)
			conn, addr = s.accept()
			with conn:
				data = conn.recv(1024)
				conn.sendall(b'Closing')

		data = data.decode().split('\r\n')
		data = data[0].split(' ')[1]

		return data

if __name__ == "__main__":
	c = XpathFinder()
	o = c.find_element('https://google.com', elements=['loool', 'hehe'])
	print(o)
