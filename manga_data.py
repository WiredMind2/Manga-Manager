
data_list = []

# Webtoons.com

if False:
	headers = {
		'Cookie': 'pagGDPR=true;',
		'Referer': 'https://www.webtoons.com'
	}

	urls = [
		# ('https://www.webtoons.com/en/fantasy/1hp-club/list?title_no=2960', 2),
		# ('https://www.webtoons.com/en/action/the-gamer/list?title_no=88', 10),
	]

	data_global = {
		'title': './/title',
		'xpth': {
			'main_list': '//*[@id="_listUl"]',
			'main_list_item': 'a',
			'img_list': '//*[@id="_imageList"]',
			'img_list_item': 'img',
		},
		'img_url': 'data-url',
		'img_desc': 'alt',
		'headers': headers
	}

	data_list.extend([({'url': url + f'&page={i}'} | data_global) for url, page in urls for i in range(1, page+1)])

# Manhwaz.com // parse directly img link? -> range // Parser blocked

if False:
	urls = [
		"https://manhwaz.com/webtoon/the-magic-in-this-other-world-is-too-far-behind"
	]

	headers = {
		'Referer': 'https://manhwaz.com/webtoon/the-magic-in-this-other-world-is-too-far-behind'
	}

	data_global = {
		'title': './/title',
		'xpth': {
			'main_list': '/html/body/div[1]/div[2]/div/div/div[1]/div[3]/ul',
			'main_list_item': 'a',
			'img_list': '//*[@id="chapter_content"]',
			'img_list_item': '*/img'
		},
		'img_url': 'src',
		'img_desc': 'alt',
		'headers': headers
	}

	data_list.extend([({'url': url} | data_global) for url in urls])

# Sololeveling.fr

if False:
	headers = {
		'Referer': 'https://www.sololeveling.fr/'
	}

	urls = [
		"https://www.sololeveling.fr/"
	]

	data_global = {
		'title': '/html/body/div/div/div/div/div/main/article/div/header/h1',
		'xpth': {
			'main_list': '/html/body/div/div/div/div/div/main/article/div/div/div[2]/ul/li/ul',
			'main_list_item': 'a',
			'img_list': '/html/body/div/div/div/div/div/main/article/div/div',
			'img_list_item': '*/img'
		},
		'img_url': 'src',
		'img_desc': 'title',
		'headers': headers
	}

	data_list.extend([({'url': url} | data_global) for url in urls])

# Readmanganato.com

if True:
	headers = {
		'Referer': 'https://readmanganato.com/',
		# 'Cookie': 'content_server=server2'
	}

	urls = [
		"https://readmanganato.com/manga-mh989642", # Chr-47
		"https://readmanganato.com/manga-ax951880", # Tales Of Demons And Gods
		"https://readmanganato.com/manga-je987087", # The Max Level Hero Has Returned!
		"https://readmanganato.com/manga-ci980191", # A Returner's Magic Should Be Special
		"https://readmanganato.com/manga-bf979214", # Versatile Mage
		"https://readmanganato.com/manga-ej981992", # I Am The Sorcerer King
		"https://readmanganato.com/manga-eu982203", # Tomb Raider King
		"https://readmanganato.com/manga-to970571", # Kimetsu no Yaiba
		"https://readmanganato.com/manga-cb980036", # The World Of Otome Games Is Tough For Mobs
		"https://readmanganato.com/manga-ec981811", # Ranker Who Lives A Second Time
		"https://readmanganato.com/manga-em981495", # Spy X Family
		"https://readmanganato.com/manga-ie985687", # Legend Of The Northern Blade
		"https://readmanganato.com/manga-va953509", # Komi-San Wa Komyushou Desu
		"https://readmanganato.com/manga-ko987549", # Sss-Class Suicide Hunter
		"https://readmanganato.com/manga-hu985229", # The Great Mage Returns After 4000 Years
		"https://readmanganato.com/manga-ex982080", # Jitsu Wa Ore, Saikyou Deshita?
		"https://readmanganato.com/manga-gt984176", # Survival Story Of A Sword King In A Fantasy World
		"https://readmanganato.com/manga-gi983617", # Fff-Class Trashero
		"https://readmanganato.com/manga-jz987182", # Mercenary Enrollment
		"https://readmanganato.com/manga-dg980989", # The Beginning After The End
		"https://readmanganato.com/manga-bt978676", # Apotheosis
		"https://readmanganato.com/manga-fr982926", # Rebirth Of The Urban Immortal Cultivator
		"https://readmanganato.com/manga-dk980967", # My Wife Is A Demon Queen
		"https://readmanganato.com/manga-nk991345", # Trapped In The Academy's Eroge
		"https://readmanganato.com/manga-nk990919", # Swordmaster’S Youngest Son
		"https://manganato.com/manga-dt981302", # Hagure Seirei Ino Shinsatsu Kiroku ~ Seijo Kishi-Dan To Iyashi No Kamiwaza ~
		"https://readmanganato.com/manga-hu985229", # The Great Mage Returns After 4000 Years
		"https://readmanganato.com/manga-ha984983", # Shijou Saikyou Orc-San No Tanoshii Tanetsuke Harem Zukuri
		"https://readmanganato.com/manga-nd990912", # Sleeping Ranker
		"https://readmanganato.com/manga-dg980989", # The Beginning After The End
		"https://readmanganato.com/manga-gr983826", # Magic Emperor
		"https://readmanganato.com/manga-nv990430", # The Weakest Occupation "blacksmith," But It's Actually The Strongest
		"https://readmanganato.com/manga-ni990665", # The Hero Returns
		"https://readmanganato.com/manga-ik985693", # Nano Machine
	]

	data_global = {
		'title': '/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/h1',
		'xpth': {
			'main_list': '/html/body/div[1]/div[3]/div[1]/div[3]/ul',
			'main_list_item': 'a',
			'img_list': '/html/body/div[1]/div[3]',
			'img_list_item': 'img'
		},
		'img_url': 'src',
		'img_desc': 'alt',
		'headers': headers,
		# 'cookies': cookies
	}

	data_list.extend([({'url': url} | data_global) for url in urls])

# magakakalot.tv

if True:
	urls = [
		"https://ww3.mangakakalot.tv/manga/manga-bs978875", # Sono Bisque Doll Wa Koi Wo Suru
	]

	data_global = {
		'title': '/html/body/div[1]/div[2]/div[1]/div[3]/ul/li[1]/h1',
		'xpth': {
			'main_list': '/html/body/div[1]/div[2]/div[1]/div[9]/div/div[2]',
			'main_list_item': 'span[1]/a',
			'img_list': '//*[@id="vungdoc"]',
			'img_list_item': 'img[@class="img-loading"]'
		},
		'img_url': 'data-src',
		'img_desc': 'alt',
		'headers': {}
	}

	data_list.extend([({'url': url} | data_global) for url in urls])
