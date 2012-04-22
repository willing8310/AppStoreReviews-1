# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import urllib2

baseURL = "http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software"

userAgent = 'iTunes/9.2 (Macintosh; U; Mac OS X 10.6)'

class ReviewsFetcher:
	appId = None
	appStoreId = None
	page = 0
		
	@staticmethod
	def fetcher(appId, appStoreId):
		return ReviewsFetcher(appId, appStoreId);
	
	def __init__(self, appId, appStoreId):
		self.appId = appId
		self.appStoreId = appStoreId
		self.page = 0

	def fetchPage(self, pageNumber):
		front = "%d-1" % self.appStoreId
		url = baseURL % (self.appId, pageNumber)
		
		req = urllib2.Request(url, headers={"X-Apple-Store-Front": front, "User-Agent": userAgent})
		
		try:
			u = urllib2.urlopen(req, timeout=30)
			if u.code >= 300:
				return None

		except urllib2.HTTPError:
			print "Can't connect to the AppStore, please try again later."
			raise SystemExit
			
		return u

	def fetchNextPage(self):
		result = self.fetchPage(self.page)
		self.page += 1;
		return result

	