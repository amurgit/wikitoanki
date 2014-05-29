# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from downloader import Downloader
import trans
import shutil
import os.path

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
	try:
		cap = pq(filename = filename).find(u'table.infobox a[title="Столица"]').parents('tr').find('td').eq(1).text()
	except:
		cap = 'CAPITAL'
	try:
		imgurl = pq(filename = filename).find('table.infobox img[width="300"]').attr('src').replace('//','http://')
	except:
		imgurl = ''
	if imgurl:
		img = dl.download(imgurl)
	else:
		img = ''
	return (name, cap, img)

def parse_zh_country(filename):
	ths = pq(filename = filename).find('table.infobox th')
	name = ''
	try:
		cap = pq(filename = filename).find(u'table.infobox a[title="首都"]').parents('tr').find('td').eq(0).text()
	except:
		cap = 'CAPITAL'
	for th in ths:
		th_text = pq(th).text()
		if th_text.find(u'通称：') == 0:
			name = pq(th).text().replace(u'通称：','')
	if not name:
		name = pq(filename = filename).find('h1').text().replace(u'国','')
	return (name, cap)

output_file = open(output_file_name, 'w')
urls = get_start_urls(ruwiki+start_article, 'table.wide span.flagicon a')
dl = Downloader()
i = 0
no_zh = 0
no_pic = 0
for href in urls:
	i+=1
	ru_country_page = dl.download(ruwiki+href.replace('/wiki/',''))
	ru_country = parse_ru_country(ru_country_page)
	zh_href = pq(filename=ru_country_page).find('#p-lang a[lang=zh]').attr('href')
	if zh_href:
		zh_country_page = dl.download(zhwiki+zh_href.replace('//zh.wikipedia.org/wiki/',''))
	else:
		zh_country_page = False
	ru_name = pq(filename = ru_country_page).find('h1').text()

	if zh_country_page:
		zh_country = parse_zh_country(zh_country_page)
		zh_name = pq(filename = zh_country_page).find('h1').text()
		print '#'+str(i)+' '+ru_name.encode('utf-8')+' '+zh_name.encode('utf-8')
	else:
		zh_country = ('ZH_NAME','ZH_CAPITAL')
		print 'No Chinese: '+ruwiki+href.replace('/wiki/','')
		no_zh +=1


	pic_address = 'picture/'+str(i)+'_'+ru_name.encode('trans/slug')
	if ru_country[2]:
		pic_address = pic_address+'.'+ru_country[2].split('.')[-1]
		if not os.path.isfile(pic_address):
			shutil.copyfile(ru_country[2], pic_address)
	else:
		
		if os.path.isfile(pic_address+'.png'):
			pic_address = pic_address+'.png'
		elif os.path.isfile(pic_address+'.jpeg'):
			pic_address = pic_address+'.jpeg'
		elif os.path.isfile(pic_address+'.gif'):
			pic_address = pic_address+'.gif'
		elif os.path.isfile(pic_address+'.jpg'):
			pic_address = pic_address+'.jpg'
		else:
			no_pic +=1
			print 'No Pic: '+pic_address+'  '+ruwiki+href.replace('/wiki/','')
			pic_address = 'PICTURE'

	ru_name, ru_cap, tmp = ru_country
	zh_name, zh_cap = zh_country

	output_file.write(pic_address.encode('utf-8')+'\t'+ru_name.encode('utf-8')+'\t'+zh_name.encode('utf-8')+'\t'+ru_cap.encode('utf-8')+'\t'+zh_cap.encode('utf-8')+'\n')

output_file.close()
print 'All: '+str(i)
print 'No chinese: '+str(no_zh)
print 'No picture: '+str(no_pic)