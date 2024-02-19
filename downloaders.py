import constants

if constants.USE_DDL == "requests":
	import requests

elif constants.USE_DDL == "selenium":
	from selenium import webdriver
	from selenium.webdriver.common.by import By

else:
	raise Exception(f'{constants.USE_DDL} is an invalid value!')


class RequestsDownloader:
	def __init__(self):
		self.session = requests.Session()

	def get(self, url, headers={}, cookies={}, decode=True, **_):
		r = self.session.get(url, headers=headers, cookies=cookies, timeout=constants.TIMEOUT)
		r.raise_for_status()

		out = r.content
		if decode:
			out = out.decode(encoding='UTF-8', errors='replace')

		return out

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.session.close()


class SeleniumDownloader:
	def __init__(self, *_):
		executable_path = r'C:\Program Files\geckodriver\geckodriver.exe'
		opts = webdriver.FirefoxOptions()
		# opts.headless = True
		self.driver = webdriver.Firefox(
			executable_path=executable_path, options=opts)
		self.driver.implicitly_wait(15)

	def __enter__(self):
		return self

	def get(self, url, *_, force_url=False):
		if force_url:
			self.driver.get(url)
		else:
			self.driver.back()
			self.driver.find_element(By.XPATH, url).click()

		return self.driver.page_source

	def __exit__(self, *args):
		self.driver.quit()
