# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from downloader import Downloader
import trans
import shutil
import os.path
import re
import sqlite3

class Getfromwiki(object):
	"""docstring for Getfromwiki"""

	def __init__(self, start_article, depth = 0):
		super(Getfromwiki, self).__init__()
		self.dl = Downloader()
		self.ruwiki = 'http://ru.wikipedia.org/wiki/'
		self.zhwiki = 'http://zh.wikipedia.org/zh-cn/'
		self.start_article = start_article #chinese wiki article
		self.output_file_name = 'new_words.html'
		self.parsed_urls = []
		self.parsed_articles = []
		self.conn = sqlite3.connect('bkrs.db')
		self.cursor = self.conn.cursor()
		self.start_log()
		self.new_words = []

		self.parse_url(self.zhwiki+start_article, depth)

	def parse_url(self, starturl, depth = 0):
		print 'Start parse url: '+starturl
		urls = self.get_article_urls(starturl)
		self.parsed_urls.append(starturl)
		parsed = 0
		for url in urls:
			if url in self.parsed_urls:
				continue
			filename = self.dl.download(url)
			self.parse_file(filename)
			parsed += 1
		print 'Parsed: '+str(parsed)+'  parsed urls: '+str(len(self.parsed_urls))+' All new words: '+str(len(self.new_words))
		if depth > 0:
			for url in urls:
				if url in self.parsed_urls:
					continue
				self.parse_url(starturl=url, depth=depth-1)

	def parse_file(self, filename):
		zh_name = self.get_zh_name(filename)
		ru_name = self.get_ru_name(filename)
		zh_article_len = self.get_article_len(filename)
		if ru_name and zh_name:
			if self.is_good_article(zh_name, ru_name):
				if not self.in_bkrs(zh_name):
					if zh_name not in self.new_words:
						self.new_words.append(zh_name)
						self.log_word(zh_name, ru_name, zh_article_len)

	def log_word(self, zh_name, ru_name, zh_article_len):
		str_index = str(len(self.new_words))
		str_odd = str(len(self.new_words)%2+1)
		rn = ru_name.encode('utf-8')
		zn = zh_name.encode('utf-8')
		log_file = open(self.output_file_name, 'a')
		log_file.write('<tr class="tr'+str_odd+'">')
		log_file.write('<td class="num">#'+str_index+'</td>')
		log_file.write('<td class="zh"><a target="_blank" href="http://bkrs.info/slovo.php?ch='+zn+'">'+zn+'</a></td>')
		log_file.write('<td class="ru">'+rn+'</td>')
		log_file.write('<td class="zh_wiki"><a target="_blank" href="'+self.zhwiki+zn+'">zh_wiki</a></td>')
		log_file.write('<td class="ru_wiki"><a target="_blank" href="'+self.ruwiki+rn.replace(' ','_')+'">ru_wiki</a></td>')
		log_file.write('<td class="zh_article_len">'+str(zh_article_len)+'</td>')
		log_file.write('<td class="zh_len">'+str(len(zh_name))+'</td>')
		log_file.write('<td class="ru_len">'+str(len(ru_name))+'</td>')
		log_file.write('</tr>')
		log_file.close()

	def get_article_urls(self, url):
		filename = self.dl.download(url)
		doc = pq(filename = filename)
		urls = []
		doc_urls = doc.find('#mw-content-text a')
		for doc_url in doc_urls:
			url = pq(doc_url).attr('href')
			if self.is_good_url(url):
				zh_url = self.zhwiki+url.replace('/wiki/','')
				urls.append(zh_url)
		return urls
	def get_article_len(self, filename):
		doc = pq(filename = filename)
		content = doc.find('#content').text()
		return len(content)


	def is_good_article(self, zh_name,  ru_name):
		ru_bad_words = [u'Списки', u'Список', u'История']
		status = False
		if re.match(ur'^[\u3300-\u33FF\u3400-\u4DBF\u4e00-\u9fff\uF900-\uFAFF\uFE30-\uFE4F]+$', zh_name):
			status = True

		for ru_bad_word in ru_bad_words:
			if ru_name.find(ru_bad_word) != -1:
				status = False

		if zh_name.find(u'·') != -1:
			status = False 

		return status

	def is_good_url(self, url):
		status = True
		if not re.match('^/wiki/(%[A-F0-9]{2})+$', url):
			status = False
		return status

	def get_zh_name(self, filename):
		try:
			zh_name = pq(filename = filename).find('h1').text()
		except:
			zh_name = ''
		return zh_name
	def get_ru_name(self, filename):
		try:
			ru_name = pq(filename = filename).find('#p-lang a[lang=ru]').attr('title').replace(u' – 俄文','')
		except:
			ru_name = ''
		return ru_name

	def in_bkrs(self, zh_word):
		t = (zh_word,)
		self.cursor.execute('SELECT * FROM dict WHERE simp=?', t)
		result = self.cursor.fetchone()
		return bool(result)

	def start_log(self):
		log_file = open(self.output_file_name, 'w')
		log_file.write('''<html>
		<head>
			<meta charset="utf-8">
			<style>
			td{padding: 0 10px;}
			a {text-decoration: none;}
			.tr1 {background-color: #EEE;}
			</style>
			<script src="sorttable.js"></script>
			<style src="styeles.css"></style>
		</head>
		<body>
			<table class="sortable" border="1" cellspacing="0">
			<tr>
				<th>Номер</th>
				<th>Китайский</th>
				<th>Русский</th>
				<th>Кит.вики</th>
				<th>Рус.вики</th>
				<th>Кол-во символов в кит. статье</th>
				<th>Длина кит. названия</th>
				<th>Длина рус. названия</th>
			</tr>
		''')
		log_file.close()

gfw = Getfromwiki('天文學', depth = 1)