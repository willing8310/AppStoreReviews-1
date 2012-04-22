# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import pymongo
from bson.objectid import ObjectId
from pymongo import Connection

from models.Review import Review
from models.Application import Application
from models.Subscriber import Subscriber

class MongoStorage:
	connection = None
	db = None
	
	reviewsCollection = None
	applicationsCollection = None
	subscribersCollection = None
	
	def __init__(self, database, host = 'localhost', port = 27017):
		self.connection = Connection(host, port)
		self.db = self.connection[database]
		self.reviewsCollection = self.db['reviews']
		self.applicationsCollection = self.db['applications']
		self.subscribersCollection = self.db['subscribers']
		
	def replaceReview(self, review):
		if review is None:
			return
		
		data = {
			"identifier" : review.identifier,
			"appId" : review.appId, 
			"author" : review.author,
			"title" : review.title,
			"text" : review.text,
			"version" : review.version,
			"rating" : review.rating,
			"date" : review.date,
			"appStoreId" : review.appStoreId,
			"order" : review.order
		}
		
		conditions = {
			"identifier" : review.identifier
		}
		
		self.reviewsCollection.update(conditions, {"$set": data}, True)
	
		
	def replaceApplication(self, application):
		if application is None:
			return
		
		data = {
			"identifier" : application.identifier,
			"updated" : application.updated,
			"reviewsLastDate" : application.reviewsLastDate
		}
		
		conditions = {
			"identifier" : application.identifier
		}
				
		self.applicationsCollection.update(conditions, {"$set": data}, True)

	
	def getApplicationWithIdentifier(self, identifier):
		if identifier is None:
			return
			
		conditions = {
			"identifier" : identifier
		}
		
		result = self.applicationsCollection.find_one(conditions)
		
		application = None
		
		if result is not None:
			application = Application()
			application.identifier = result["identifier"]
			application.updated = result["updated"]
			application.reviewsLastDate = result["reviewsLastDate"]
				
		return application
	
	def insertSubscriber(self, subscriber):
		if subscriber is None:
			return
			
		data = {
			"email" : subscriber.email,
			"appId" : subscriber.appId,
			"lastReviewId" : subscriber.lastReviewId
		}
		
		self.subscribersCollection.insert(data)
		
	def deleteSubscriber(self, subscriber):
		if subscriber is None:
			return
			
		self.subscribersCollection.remove(subscriber.rowId)
	
	def _subscriberFromDict(self, data):
		if data is None:
			return None
			
		subscriber = Subscriber()
		subscriber.rowId = data["_id"]
		subscriber.email = data["email"]
		subscriber.appId = data["appId"]
		subscriber.lastReviewId = data["lastReviewId"]
		
		return subscriber
	
	def getSubscriber(self, email, appId):
		if email is None or appId is None:
			return
			
		conditions = {
			"email" : email,
			"appId" : appId
		}
		
		result = self.subscribersCollection.find_one(conditions)
		
		subscriber = self._subscriberFromDict(result)
						
		return subscriber
	
	def getSubscribers(self, appId = None):
		
		conditions = {}
		if appId is not None:
			conditions["appId"] = appId
		
		result = []
		
		cursor = self.subscribersCollection.find(spec = conditions).sort(u"email", pymongo.ASCENDING)
		for data in cursor:
			result.append(self._subscriberFromDict(data))
			
		return result
	
	def _getReviews(self, conditions = None, limit = 0):
		reviews = []
				
		cursor = self.reviewsCollection.find(spec = conditions, limit = limit).sort([(u"date", pymongo.DESCENDING), (u"order", pymongo.DESCENDING)])
		for rawReview in cursor:
			review = Review()
			review.rowId = rawReview["_id"]
			review.identifier = rawReview["identifier"]
			review.author = rawReview["author"]
			review.appId = rawReview["appId"]
			review.title = rawReview["title"]
			review.text = rawReview["text"]
			review.version = rawReview["version"]
			review.rating = rawReview["rating"]
			review.date = rawReview["date"]
			review.appStoreId = rawReview["appStoreId"]
			
			reviews.append(review)
			
		return reviews
		
	def getReviews(self, appId, limit = 0, appStoreId = None, date = None, minRowId = None):
		conditions = {
			"appId" : appId
		}
		if appStoreId is not None:
			conditions["appStoreId"] = appStoreId
		
		if date is not None:
			conditions["date"] = date
			
		if minRowId is not None:
			conditions["_id"] = {"$gt" : ObjectId(minRowId)}
		
		return self._getReviews(conditions, limit)
			
			