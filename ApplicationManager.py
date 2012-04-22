# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import datetime
import sys
from models.Application import Application

appStores = {
	'Argentina':		143505,
	'Australia':		143460,
	'Belgium':			143446,
	'Brazil':			143503,
	'Canada':			143455,
	'Chile':			143483,
	'China':			143465,
	'Colombia':			143501,
	'Costa Rica':		143495,
	'Croatia':			143494,
	'Czech Republic':	143489,
	'Denmark':			143458,
	'Deutschland':		143443,
	'El Salvador':		143506,
	'Espana':			143454,
	'Finland':			143447,
	'France':			143442,
	'Greece':			143448,
	'Guatemala':		143504,
	'Hong Kong':		143463,
	'Hungary':			143482,
	'India':			143467,
	'Indonesia':		143476,
	'Ireland':			143449,
	'Israel':			143491,
	'Italia':			143450,
	'Korea':			143466,
	'Kuwait':			143493,
	'Lebanon':			143497,
	'Luxembourg':		143451,
	'Malaysia':			143473,
	'Mexico':			143468,
	'Nederland':		143452,
	'New Zealand':		143461,
	'Norway':			143457,
	'Osterreich':		143445,
	'Pakistan':			143477,
	'Panama':			143485,
	'Peru':				143507,
	'Phillipines':		143474,
	'Poland':			143478,
	'Portugal':			143453,
	'Qatar':			143498,
	'Romania':			143487,
	'Russia':			143469,
	'Saudi Arabia':		143479,
	'Schweiz/Suisse':	143459, 
	'Singapore':		143464,
	'Slovakia':			143496,
	'Slovenia':			143499,
	'South Africa':		143472,
	'Sri Lanka':		143486,
	'Sweden':			143456,
	'Taiwan':			143470,
	'Thailand':			143475,
	'Turkey':			143480,
	'United Arab Emirates':143481,
	'United Kingdom':	143444,
	'United States':	143441,
	'Venezuela':		143502,
	'Vietnam':			143471,
	'Japan':			143462,
	'Dominican Republic': 143508,
	'Ecuador':			143509,
	'Egypt':			143516,
	'Estonia':			143518,
	'Honduras':			143510,
	'Jamaica':			143511,
	'Kazakhstan':		143517,
	'Latvia':			143519,
	'Lithuania':		143520,
	'Macau':			143515, 
	'Malta':			143521,
	'Moldova':			143523,  
	'Nicaragua':		143512,
	'Paraguay':			143513,
	'Uruguay':			143514
}

class ApplicationManager:
	storage = None
	
	fetcherFactory = None
	parserFactory = None
	
	application = None
	
	reviewsLastDate = None
	
	def __init__(self, appId, storage):
		self.storage = storage
		application = self.storage.getApplicationWithIdentifier(appId)
		if application is None:
			application = Application()
			application.identifier = appId
			
		self.application = application
	
	def loadAndUpdateReviews(self, country = None, limit = 50):
		if self.application is None:
			return
		
		if self.fetcherFactory is None or self.parserFactory is None:
			return
		
		if country is None:
			self.reviewsLastDate = None
			
			# i = 0
			# total = len(appStores)
			# progress = int((float(i) / float(total)) * 100.0)
			# print "\r[{0}] {1}%".format('#'*(progress/10), progress)
			
			for country in appStores:
				self.loadAndUpdateReviews(country, limit)
				# i += 1
				# progress = int((float(i) / float(total)) * 100)	
				# print "\r[{0}] {1}%".format('#'*(progress/10), progress)
			
			if self.application.reviewsLastDate is None:
				self.application.reviewsLastDate = self.reviewsLastDate
			elif self.reviewsLastDate is not None and self.application.reviewsLastDate < self.reviewsLastDate:
				self.application.reviewsLastDate = self.reviewsLastDate
			
			self.application.updated = datetime.datetime.now()			
			self.storage.replaceApplication(self.application)
			
		else:
			#print country
			if country not in appStores:
				print "Country not found"
				return
			
			appStoreId = appStores[country]
			reviewsCount = 0
			reviewsOrder = sys.maxint
			lastDayReviews = None
					
			fetcher = self.fetcherFactory.fetcher(self.application.identifier, appStoreId)
					
			while reviewsCount < limit:
				reviews = None
								
				try:					
					parser = self.parserFactory.parser(fetcher.fetchNextPage())
					reviews = parser.parse()
				except Exception as ex:
					print ex
					break
				
				if len(reviews) == 0:
					break
				
				reviewsCount += len(reviews)
																				
				for review in reviews:
					if self.reviewsLastDate is None or self.reviewsLastDate < review.date:
						self.reviewsLastDate = review.date
										
					if self.application.reviewsLastDate is not None and self.application.reviewsLastDate > review.date:
						reviewsCount = limit
						break
					
					if lastDayReviews is None:
						lastDayReviews = self.storage.getReviews(appId = self.application.identifier, appStoreId = appStoreId, date = self.application.reviewsLastDate)
										
					review.appId = self.application.identifier
					review.appStoreId = appStoreId
					
					oldReview = None
					
					for _review in lastDayReviews:
						if _review.identifier == review.identifier:
							oldReview = _review
							break
					
					if oldReview is not None:
						reviewsCount = limit
						break							
										
					review.order = reviewsOrder					
					reviewsOrder -= 1
						
					self.storage.replaceReview(review)
				
					
				
	def getLatestReviews(self, country = None, limit = 10):
		if self.application is None:
			return
		return self.storage.getReviews(appId = self.application.identifier, limit = limit)

	