#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import argparse
from storage.MongoStorage import MongoStorage
from models.Subscriber import Subscriber
from models.Application import Application

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
	
	args = parser.parse_args()
	args.func(args)
	