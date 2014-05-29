# -*- coding: utf-8 -*-
import urllib2
import hashlib
import os
from socket import error as SocketError
import errno
import random
import time
import urllib

class Downloader(object):
	"""docstring for Downloader"""
	def __init__(self):
		super(Downloader, self).__init__()
		self.cachedir = '/home/dongxing/Downloads/wiki_cache/'
		self.userAgent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
		self.max_retries = 5
		self.slowurls = []
		
	def download(self, url, retry = 0):
		if retry>0:
			print 'try #'+str(retry)+' to download url: '+urllib.unquote(url)
			time.sleep(random.random()+0.5)
		if retry>self.max_retries:
			self.slowurls.append(url)
			return False
		timeout = 1+retry
		urlhash = hashlib.md5(url).hexdigest()
		filepath = self.cachedir+urlhash+'.'+self.get_extension(url)
		filepath_old = self.cachedir+urlhash #without extention
		if os.path.isfile(filepath):
			return filepath
		if os.path.isfile(filepath_old) and filepath != filepath_old:
			os.rename(filepath_old, filepath)
			return filepath
		try:
			pagedata = urllib2.urlopen(url=url, timeout=timeout).read()
		except (urllib2.URLError, SocketError) as e:
			if e.errno == errno.ECONNRESET:
				print 'reset connection'
			return self.download(url, retry = retry+1)

		cachefile = open(filepath, 'w')
		cachefile.write(pagedata)
		cachefile.close()
		return filepath

	def get_extension(self, url):
		ext = url.split('.')[-1]
		if len(ext)>4:
			ext = 'noext'
		return ext
