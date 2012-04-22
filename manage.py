#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import argparse

from storage.MongoStorage import MongoStorage
from storage.MemoryStorage import MemoryStorage

from models.Subscriber import Subscriber
from models.Application import Application

from ReviewsFetcher import ReviewsFetcher
from ReviewsParser import ReviewsParser

from ApplicationManager import ApplicationManager

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

storage = None

def getStorage():
	global storage
	if storage is not None:
		return storage
		
	try:
		storage = MongoStorage("AppStoreReviews")
	except Exception as ex:
		print ex
		raise SystemExit
		
	return storage


def addSubscriber(args):
	storage = getStorage()
	
	subscriber = storage.getSubscriber(email = args.email, appId = args.appId)
	if subscriber is not None:
		return
	
	application = storage.getApplicationWithIdentifier(args.appId)
	if application is None:
		application = Application()
		application.identifier = args.appId
		storage.replaceApplication(application)
	
	subscriber = Subscriber()
	subscriber.email = args.email
	subscriber.appId = args.appId
	
	storage.insertSubscriber(subscriber)

def deleteSubscriber(args):
	storage = getStorage()
	
	subscriber = storage.getSubscriber(email = args.email, appId = args.appId)
	if subscriber is None:
		return
		
	storage.deleteSubscriber(subscriber)

def listSubscribers(args):
	storage = getStorage()
	
	subscribers = storage.getSubscribers(appId = args.appId)
	for subscriber in subscribers:
		print "%s / %s" % (subscriber.email, subscriber.appId)

def listReviews(args):
	storage = getStorage()
	
	reviews = storage.getReviews(appId = args.appId, limit = args.limit)
	
	for review in reviews:			
		print "[%d stars] %s by %s on %s" % (review.rating, review.version, review.author, review.date)
		print " (%s) %s" % (review.title, review.text)
		print "-------------------------------------------------------------------------------------------"
	
	
def updateReviews(args):
	application = ApplicationManager(args.appId, getStorage())
	application.fetcherFactory = ReviewsFetcher
	application.parserFactory = ReviewsParser
	
	application.loadAndUpdateReviews(country = args.country, limit = args.limit)
	
def sendReviews(args):
	storage = getStorage()
	subscribers = storage.getSubscribers(appId = args.appId)
	for subscriber in subscribers:	
		reviews = storage.getReviews(appId = args.appId, minRowId = subscriber.lastReviewId, limit = 50)
		
		if reviews is None or len(reviews) == 0:
			continue
		
		fromAddr = "appstorereviews@shurakov.name"
		toAddr = subscriber.email
		
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Test Subject"
		msg['From'] = fromAddr
		msg['To'] = toAddr
		
		text = ''
		
		for review in reviews:
			text += u"[%d stars] %s by %s on %s\n%s\n%s\n\n-------\n" % (review.rating, review.version, review.author, review.date, review.title, review.text)
				
		part1 = MIMEText(text, 'plain', 'utf-8')
		msg.attach(part1)
		s = smtplib.SMTP('localhost')
		s.sendmail(fromAddr, toAddr, msg.as_string())
		s.quit()
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	subparsers = parser.add_subparsers()
	
	parser_subscribers = subparsers.add_parser('subscribers')
	parser_subscribers_sub = parser_subscribers.add_subparsers()
	
	parser_subscribers_add = parser_subscribers_sub.add_parser('list')
	parser_subscribers_add.add_argument('appId', type=int, help='application identifier', default = None, nargs='?')
	parser_subscribers_add.set_defaults(func=listSubscribers)
	
	parser_subscribers_add = parser_subscribers_sub.add_parser('add')
	parser_subscribers_add.add_argument('email', type=str, help='email')
	parser_subscribers_add.add_argument('appId', type=int, help='application identifier')
	parser_subscribers_add.set_defaults(func=addSubscriber)
	
	parser_subscribers_delete = parser_subscribers_sub.add_parser('delete')
	parser_subscribers_delete.add_argument('email', type=str, help='email')
	parser_subscribers_delete.add_argument('appId', type=int, help='application identifier')
	parser_subscribers_delete.set_defaults(func=deleteSubscriber)
	
	
	parser_reviews = subparsers.add_parser('reviews')
	parser_reviews_sub = parser_reviews.add_subparsers()
	
	parser_reviews_list = parser_reviews_sub.add_parser('list')
	parser_reviews_list.add_argument('appId', type=int, help='application identifier')
	parser_reviews_list.add_argument('-c', '--country', type=str, help='country', default=None)
	parser_reviews_list.add_argument('-l', '--limit', type=int, help='limit', default=10)
	parser_reviews_list.set_defaults(func=listReviews)
	
	parser_reviews_update = parser_reviews_sub.add_parser('update')
	parser_reviews_update.add_argument('appId', type=int, help='application identifier')
	parser_reviews_update.add_argument('-c', '--country', type=str, help='country', default=None)
	parser_reviews_update.add_argument('-l', '--limit', type=int, help='limit', default=50)
	parser_reviews_update.set_defaults(func=updateReviews)
	
	parser_reviews_send = parser_reviews_sub.add_parser('send')
	#parser_reviews_send.add_argument('appId', type=int, help='application identifier', default = None, nargs='?')
	parser_reviews_send.add_argument('appId', type=int, help='application identifier')
	parser_reviews_send.set_defaults(func=sendReviews)
	
	args = parser.parse_args()
	args.func(args)
	