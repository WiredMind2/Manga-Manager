data_list = []

# Webtoons.com

if False:
	headers = {"Cookie": "pagGDPR=true;", "Referer": "https://www.webtoons.com"}

	urls = [
		# ('https://www.webtoons.com/en/fantasy/1hp-club/list?title_no=2960', 2),
		# ('https://www.webtoons.com/en/action/the-gamer/list?title_no=88', 10),
	]

	data_global = {
		"title": ".//title",
		"xpth": {
			"main_list": '//*[@id="_listUl"]',
			"main_list_item": "a",
			"img_list": '//*[@id="_imageList"]',
			"img_list_item": "img",
		},
		"img_url": "data-url",
		"img_desc": "alt",
		"headers": headers,
	}

	data_list.extend(
		[
			({"url": url + f"&page={i}"} | data_global)
			for url, page in urls
			for i in range(1, page + 1)
		]
	)

# Manhwaz.com // parse directly img link? -> range // Parser blocked

if False:
	urls = [
		"https://manhwaz.com/webtoon/the-magic-in-this-other-world-is-too-far-behind"
	]

	headers = {
		"Referer": "https://manhwaz.com/webtoon/the-magic-in-this-other-world-is-too-far-behind"
	}

	data_global = {
		"title": ".//title",
		"xpth": {
			"main_list": "/html/body/div[1]/div[2]/div/div/div[1]/div[3]/ul",
			"main_list_item": "a",
			"img_list": '//*[@id="chapter_content"]',
			"img_list_item": "*/img",
		},
		"img_url": "src",
		"img_desc": "alt",
		"headers": headers,
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# Sololeveling.fr

if False:
	headers = {"Referer": "https://www.sololeveling.fr/"}

	urls = ["https://www.sololeveling.fr/"]

	data_global = {
		"title": "/html/body/div/div/div/div/div/main/article/div/header/h1",
		"xpth": {
			"main_list": "/html/body/div/div/div/div/div/main/article/div/div/div[2]/ul/li/ul",
			"main_list_item": "a",
			"img_list": "/html/body/div/div/div/div/div/main/article/div/div",
			"img_list_item": "*/img",
		},
		"img_url": "src",
		"img_desc": "title",
		"headers": headers,
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# manganato.com

if True:
	headers = {
		"Referer": "https://chapmanganato.com/",
		# 'Cookie': 'content_server=server2'
	}

	urls = [
		# "https://chapmanganato.com/manga-mh989642", # Chr-47
		# "https://chapmanganato.com/manga-ax951880", # Tales Of Demons And Gods
		"https://chapmanganato.com/manga-je987087",  # The Max Level Hero Has Returned!
		# "https://chapmanganato.com/manga-ci980191",  # A Returner's Magic Should Be Special
		# "https://chapmanganato.com/manga-bf979214",  # Versatile Mage
		# "https://chapmanganato.com/manga-ej981992",  # I Am The Sorcerer King
		# "https://chapmanganato.com/manga-eu982203",  # Tomb Raider King
		# "https://chapmanganato.com/manga-cb980036",  # The World Of Otome Games Is Tough For Mobs
		"https://chapmanganato.com/manga-ec981811",  # Ranker Who Lives A Second Time
		# "https://chapmanganato.com/manga-ie985687",  # Legend Of The Northern Blade
		"https://chapmanganato.com/manga-ko987549",  # Sss-Class Suicide Hunter
		"https://chapmanganato.com/manga-hu985229",  # The Great Mage Returns After 4000 Years
		"https://chapmanganato.com/manga-ex982080",  # Jitsu Wa Ore, Saikyou Deshita?
		"https://chapmanganato.com/manga-gt984176",  # Survival Story Of A Sword King In A Fantasy World
		# "https://chapmanganato.com/manga-gi983617",  # Fff-Class Trashero
		# "https://chapmanganato.com/manga-jz987182",  # Mercenary Enrollment
		"https://chapmanganato.com/manga-dg980989",  # The Beginning After The End
		# "https://chapmanganato.com/manga-bt978676",  # Apotheosis
		# "https://chapmanganato.com/manga-fr982926",  # Rebirth Of The Urban Immortal Cultivator
		# "https://chapmanganato.com/manga-dk980967",  # My Wife Is A Demon Queen
		# "https://chapmanganato.com/manga-nk991345", # Trapped In The Academy's Eroge
		"https://chapmanganato.com/manga-nk990919",  # Swordmaster’S Youngest Son
		"https://manganato.com/manga-dt981302",  # Hagure Seirei Ino Shinsatsu Kiroku ~ Seijo Kishi-Dan To Iyashi No Kamiwaza ~
		# "https://chapmanganato.com/manga-ha984983",  # Shijou Saikyou Orc-San No Tanoshii Tanetsuke Harem Zukuri
		# "https://chapmanganato.com/manga-nd990912",  # Sleeping Ranker
		"https://chapmanganato.com/manga-gr983826",  # Magic Emperor / The Devil Butler
		"https://chapmanganato.com/manga-nv990430",  # The Weakest Occupation "blacksmith," But It's Actually The Strongest
		"https://chapmanganato.com/manga-ni990665",  # The Hero Returns
		# "https://chapmanganato.com/manga-ik985693",  # Nano Machine
		"https://chapmanganato.com/manga-td996812",  # Catastrophic Necromancer
		"https://manganato.com/manga-on992096",  # Souzou Renkinjutsushi Wa Jiyuu Wo Ouka Suru: Kokyou Wo Tsuihou Saretara, Maou No Ohizamoto De Chouzetsu Kouka No Magic Item Tsukuri-Houdai Ni Narimashita
		"https://manganato.com/manga-gm984221",  # Isekai De Cheat Skill Wo Te Ni Shita Ore Wa, Genjitsu Sekai Wo Mo Musou Suru ~Level Up Wa Jinsei Wo Kaeta~
		#"https://manganato.com/manga-qz993682",  # Magic Level 99990000 All-Attribute Great Sage -> Not found
		"https://manganato.com/manga-oq991399",  # Kiwameta Renkinjutsu Ni, Fukanou Wa Nai.
		"https://manganato.com/manga-eq981551",  # The Reincarnation Magician Of The Inferior Eyes
		#"https://manganato.com/manga-om991369",  # A Hero Trained By The Most Evil Demon King Is Unrivaled In The Academy Of Returnees From Another World -> Not found
		"https://chapmanganato.com/manga-jy987133",  # Max Level Returner
		"https://chapmanganato.com/manga-lt989154",  # I Grow Stronger By Eating!
		"https://chapmanganato.com/manga-fz982434",  # Isekai Meikyuu No Saishinbu O Mezasou
		"https://chapmanganato.com/manga-fo982397",  # 100-Nin No Eiyuu O Sodateta Saikyou Yogensha Wa, Boukensha Ni Natte Mo Sekaijuu No Deshi Kara Shitawarete Masu
		"https://chapmanganato.com/manga-cs979527",  # My Status As An Assassin Obviously Exceeds The Brave's
		"https://chapmanganato.com/manga-kt987876",  # The Tutorial Is Too Hard
		"https://chapmanganato.com/manga-ih985916",  # Kikanshita Yuusha No Gojitsudan
		"https://chapmanganato.com/manga-ht984802",  # Crimson Karma
		"https://chapmanganato.com/manga-nt991076",  # Is This Hero For Real?
		"https://chapmanganato.com/manga-nd991160",  # Monster Streamer For Gods
		"https://chapmanganato.com/manga-nh990916",  # The Exiled Reincarnated Heavy Knight Is Unrivaled In Game Knowledge
		"https://chapmanganato.com/manga-om991521",  # The Novel’S Extra
		# "https://chapmanganato.com/manga-dr980474",  # Solo Leveling
		# "https://chapmanganato.com/manga-aa951883",  # Tower Of God
		"https://chapmanganato.com/manga-bu979277",  # Skeleton Soldier Couldn’T Protect The Dungeon
		"https://chapmanganato.com/manga-mu989777",  # Talent Copycat
		"https://chapmanganato.com/manga-lc988811",  # Rise From The Rubble
		"https://chapmanganato.com/manga-mp989824",  # I'm Really Not The Evil God's Lackey
		"https://chapmanganato.com/manga-mt989602",  # I Can Snatch 999 Types Of Abilities
		"https://chapmanganato.com/manga-jn986422",  # Return To Player
		"https://chapmanganato.to/manga-xk1001093",  # I Killed An Academy Player
	]

	mangas = False
	if mangas:
		urls += [  # Mangas / scans -> black and white
			"https://chapmanganato.com/manga-um971369",  # Youjo Senki
			"https://chapmanganato.com/manga-to951549",  # Tenkuu Shinpan
			"https://chapmanganato.com/manga-us971827",  # Goblin Slayer
			"https://chapmanganato.com/manga-oa952283",  # Attack On Titan
			"https://chapmanganato.com/manga-de980539",  # The Eminence In Shadow
			"https://chapmanganato.com/manga-ai977917",  # Kaifuku Jutsushi No Yarinaoshi
			"https://chapmanganato.com/manga-dr980852",  # Fukushuu O Koinegau Saikyou Yuusha Wa, Yami No Chikara De Senmetsu Musou Suru
			"https://chapmanganato.com/manga-dn980422",  # Chainsaw Man
			"https://chapmanganato.com/manga-kx951980",  # Ansatsu Kyoushitsu
			"https://chapmanganato.com/manga-bc978911",  # Darling In The Franxx
			"https://chapmanganato.com/manga-em981495",  # Spy X Family
			"https://chapmanganato.com/manga-va953509",  # Komi-San Wa Komyushou Desu
			"https://chapmanganato.com/manga-to970571",  # Kimetsu no Yaiba
			"https://chapmanganato.com/manga-in985422",  # Boys abyss
			"https://manganato.com/manga-kg988163", # Gannibal
			"https://chapmanganato.to/manga-ln988396", # Manchuria Opium Squad
			"https://manganato.com/manga-ou952777", # Rikudou
			"https://chapmanganato.to/manga-qj952992", # Ajin
		]

	data_global = {
		
		"title": '//div[contains(@class, "story-info-right")]/h1',
		"cover": '//span[contains(@class, "info-image")]/img',
		"description": '//*[@id="panel-story-info-description"]/text()',
		"xpth": {
			"main_list": '//ul[contains(@class, "row-content-chapter")]',
			"main_list_item": "a",
			"img_list": '//div[contains(@class, "container-chapter-reader")]',
			"img_list_item": "img",
		},
		"img_url": "src",
		"img_desc": "alt",
		"headers": headers,
		# 'cookies': cookies
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# magakakalot.tv

if False:
	urls = [
		"https://ww3.mangakakalot.tv/manga/manga-bs978875",  # Sono Bisque Doll Wa Koi Wo Suru
	]

	data_global = {
		"title": "/html/body/div[1]/div[2]/div[1]/div[3]/ul/li[1]/h1",
		"cover": "/html/body/div[1]/div[2]/div[1]/div[3]/div/img",
		"description": '//*[@id="noidungm"]/text()',
		"xpth": {
			"main_list": "/html/body/div[1]/div[2]/div[1]/div[9]/div/div[2]",
			"main_list_item": "span[1]/a",
			"img_list": '//*[@id="vungdoc"]',
			"img_list_item": 'img[@class="img-loading"]',
		},
		"img_url": "data-src",
		"img_desc": "alt",
		"headers": {},
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# sololevelingscan.com

if False:
	urls = ["https://ww4.sololevelingscan.com/"]

	data_global = {
		"title": "/html/body/div/div/div/div/div/main/article/div/header/h1",
		"xpth": {
			"main_list": "/html/body/div/div/div/div/div/main/article/div/div/div[9]/ul/li/ul",
			"main_list_item": "a",
			"img_list": "/html/body/div/div/div/div/div/main/article/div",
			"img_list_item": '//img[not(contains(@class, "aligncenter"))]',
		},
		"img_url": "src",
		"img_desc": "alt",
		"headers": {},
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# Mangatx.com

if False: # Website doesn't exists anymore?
	urls = [
		"https://mangatx.com/manga/i-became-the-tyrant-of-a-defence-game",
		"https://mangatx.com/manga/swordmasters-youngest-son/",
		# "https://mangatx.com/manga/the-hero-returns/",
		"https://mangatx.com/manga/boundless-necromancer/",
		"https://mangatx.com/manga/my-girlfriend-is-a-zombie/",
	]

	data_global = {
		"title": "//h1",
		"cover": '//div[contains(@class, "summary_image")]/a/img',
		"description": '//div[contains(@class, "summary__content")]//*/text()',
		"xpth": {
			"main_list": '//ul[contains(@class, "main ")]',
			"main_list_item": "a",
			"img_list": '//div[contains(@class, "read-container")]/div[contains(@class, "reading-content")]',
			"img_list_item": "div/img",
		},
		"img_url": "data-src",
		"cover_url": "data-src",
		"img_desc": "id",
		"headers": {},
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

# Readgrandblue
if False: # Site seems down?
	urls = ["https://w12.readgrandblue.com/"]

	data_global = {
		"title": "//header/h1",
		"description": "//main/article/div/div/p[1]/strong/text()",
		"xpth": {
			"main_list": '//*[@id="ceo_thumbnail_widget-2"]',
			"main_list_item": "div[1]/a",
			"img_list": "//main/article/div/div",
			"img_list_item": "p/img",
		},
		"img_url": "src",
		"img_desc": "alt",
		"headers": {},
	}

	data_list.extend([({"url": url} | data_global) for url in urls])

if __name__ == "__main__":
	# Export datalist
	import json

	path = "datalist.json"
	with open(path, "w") as f:
		json.dump(data_list, f, indent=4)
