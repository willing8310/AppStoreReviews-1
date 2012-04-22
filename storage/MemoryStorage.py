# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

class MemoryStorage:
	reviews = None
	dirty = False
		
	def __init__(self):
		self.reviews = []
		self.dirty = False
		
	def replaceReview(self, review):
		if review is None:
			return
		
		self.reviews.append(review);
		self.dirty = True
		
	
	def replaceApplication(self, application):
		pass
	
	def getApplicationWithIdentifier(self, identifier):
		return None
		
	def getReviews(self, appId, limit = 0, appStoreId = None, date = None):
		if self.dirty:
			self.reviews.sort(key=lambda review: review.date, reverse=True)
			self.dirty = False
		
		if limit == 0:
			limit = len(self.reviews)
		
		result = []
		for review in self.reviews:
			if limit <= 0:
				break
				
			if review.appId == appId:
				result.append(review)
				limit -= 1
				
		
		return result
			
			