# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

class Review:
	
	identifier = 0
	
	author = None
	
	title = None
	text = None
	version = None
	
	rating = 0
	date = None
	
	appId = None
	appStoreId = None
	
	usn = 0
	order = 0
	
	def isAnonymous(self):
		return (self.author is None or self.author == u"Anonymous")
	
	def isEqual(self, otherReview):
		if otherReview is None:
			return False
			
		if self.title == otherReview.title and self.text == otherReview.text and self.version == otherReview.version and self.rating == otherReview.rating and self.author == otherReview.author:
			return True
			
		return False
		