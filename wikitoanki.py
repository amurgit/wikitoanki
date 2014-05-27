# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from downloader import Downloader

ruwiki = 'http://ru.wikipedia.org/wiki/'
zhwiki = 'http://zh.wikipedia.org/zh-cn/'
start_article = 'Список_стран_по_населению' 
output_file_name = 'anki_countries.txt'
contries = []

def get_start_urls(url, urlpath):
	dl = Downloader()
	pagedata_filename = dl.download(url)
	doc = pq(filename = pagedata_filename)
	urls = []
	durls = doc(urlpath)
	for durl in durls:
		url = pq(durl).attr('href')
		urls.append(url)
	return urls

def parse_ru_country(filename):	
	dl = Downloader()																						
	name = pq(filename = filename).find('h1').text()
	cap = pq(filename = filename).find(u'table.infobox a[title="Столица"]').parents('tr').find('td').eq(1).text()
	imgurl = pq(filename = filename).find('table.infobox img[width="300"]').attr('src').replace('//','http://')
	if imgurl:
		img = dl.download(imgurl)
	else:
		img = ''
	return (name, cap, img)

def parse_zh_country(filename):
	ths = pq(filename = filename).find('table.infobox th')
	name = ''
	cap = pq(filename = filename).find(u'table.infobox a[title="首都"]').parents('tr').find('td').eq(0).text()
	for th in ths:
		th_text = pq(th).text()
		if th_text.find(u'通称：') == 0:
			name = pq(th).text().replace(u'通称：','')
	if not name:
		name = pq(filename = filename).find('h1').text().replace(u'国','')
	print name.encode('utf-8')
	print cap.encode('utf-8')
	return (name, cap)

output_file = open(output_file_name, 'w')
urls = get_start_urls(ruwiki+start_article, 'table.wide span.flagicon a')
dl = Downloader()
i = 0
for href in urls:
	i+=1
	ru_country_page = dl.download(ruwiki+href.replace('/wiki/',''))
	ru_country = parse_ru_country(ru_country_page)
	zh_href = pq(filename=ru_country_page).find('#p-lang a[lang=zh]').attr('href')
	zh_country_page = dl.download(zhwiki+zh_href.replace('//zh.wikipedia.org/wiki/',''))
	ru_name = pq(filename = ru_country_page).find('h1').text()

	if zh_country_page:
		zh_country = parse_zh_country(zh_country_page)
		zh_name = pq(filename = zh_country_page).find('h1').text()
		print '#'+str(i)+' '+ru_name.encode('utf-8')+' '+zh_name.encode('utf-8')
	else:
		zh_country = ('','')

	if ru_country[2]:
		
		