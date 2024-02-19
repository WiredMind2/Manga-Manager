import logging
from urllib.parse import urljoin

import constants
from utils import ParseError

if constants.USE_PARSER == "lxml":
	import lxml.html
	from lxml import etree

elif constants.USE_PARSER == "bs4":
	from bs4 import BeautifulSoup

else:
	raise Exception(f'{constants.USE_PARSER} is an invalid value!')


class LxmlParser:
	def main_page(self, data, page):
		p_tree = etree.ElementTree(lxml.html.fromstring(page))
		main_list = p_tree.xpath(data['xpth']['main_list'])
		if len(main_list) == 0:
			print(f'ERROR - Main list not found! Url: {data["url"]}')
			raise ParseError
		main_list = main_list[0]

		links = {}
		for c in main_list:
			matchs = c.xpath(data['xpth']['main_list_item'])
			if len(matchs) == 0:
				continue

			child = matchs[0]
			if constants.USE_DDL == "requests":
				link = child.get('href')
			elif constants.USE_DDL == "selenium":
				link = p_tree.getpath(child)

			link = urljoin(data['url'], link)

			name = child.text_content().strip()
			links[name] = link

		title = p_tree.xpath(data['title'])[0].text.strip()
		if 'cover' in data:
			cover = p_tree.xpath(data['cover'])[0].get(data.get('cover_url', None) or data.get('img_url', None) or 'src')
			if cover is None:
				cover = p_tree.xpath(data['cover'])[0].get('src')
			if cover is not None:
				cover = cover.strip()
		else:
			cover = None

		if 'description' in data:
			desc = ''.join(p_tree.xpath(data['description'])).strip()
		else:
			desc = None

		return {'title': title, 'cover': cover, 'desc': desc, 'links': links}

	def chapter(self, page, path, data):
		l_tree = etree.ElementTree(lxml.html.fromstring(page))
		l_data = []
		root = l_tree.xpath(data['xpth']['img_list'])[0]
		for i, child in enumerate(root.xpath(data['xpth']['img_list_item'])):
			if child.tag == 'img':
				tmp = {
					'url': child.get(data['img_url']).strip(),
					'desc': str(i).zfill(5) + "-" + child.get(data['img_desc'], 'Unknown'),
					'path': path
				}

				l_data.append(tmp)

			else:
				txt = f'Error: child isn\'t an image - {path} {child} {child.tag}'
				logging.error(txt)

				raise Exception(txt)

		return l_data


class Bs4Parser:
	def main_page(self, data, page):
		# TODO - How to implement xPath??
		p_soup = BeautifulSoup(page, 'html.parser')
		main_list = p_soup.find(
			"li", {"id": "ceo_latest_comics_widget-3"}).ul.find_all("a")  # WTF hardcoded??

		links = {}
		for child in main_list:
			if constants.USE_DDL == "requests":
				link = child['href']
			elif constants.USE_DDL == "selenium":
				# TODO
				raise NotImplementedError(
					"bs4 parser not implemented with selenium!")
			
			name = child.getText()
			links[name] = link

		title = p_soup.title.text

		return title, links

	def chapter(self, page, path, data):
		# TODO - How to implement xPath??
		l_soup = BeautifulSoup(page, 'lxml')
		l_data = []
		for i, child in enumerate(l_soup.find("main").article.div.div.find_all("img")):
			tmp = {
				'url': child['src'],
				'desc': str(i).zfill(5) + "-" + child['alt'],
				'path': path
			}
			l_data.append(tmp)
