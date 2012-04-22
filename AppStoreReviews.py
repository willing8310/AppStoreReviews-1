#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import argparse

from ReviewsFetcher import ReviewsFetcher
from ReviewsParser import ReviewsParser
from storage.MemoryStorage import MemoryStorage
from storage.MongoStorage import MongoStorage

from ApplicationManager import ApplicationManager

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='AppStoreReviewsScrapper command line.', epilog='To get your application Id look into the AppStore link to you app, for example http://itunes.apple.com/pl/app/autobuser-warszawa/id335042980?mt=8 - app Id is the number between "id" and "?mt=0"')
	parser.add_argument('-i', '--id', default=0, metavar='AppId', type=int, help='Application Id (see below)')
	parser.add_argument('-c', '--country', metavar='"Name"', type=str, default=None, help='AppStore country name')
	parser.add_argument('-l', '--limit', default=15, type=int, help='Limit results')
	parser.add_argument('-s', '--storage', default='memory', type=str, help='Storage type (mongo or memory)')
	args = parser.parse_args()
	if args.id == 0:
		parser.print_help()
		raise SystemExit
	
	storage = None
	try:
		if args.storage == "mongo":
			storage = MongoStorage("AppStoreReviews")
		else:
			storage = MemoryStorage()	
	except Exception as ex:
		print ex
		raise SystemExit
	
	
	application = ApplicationManager(args.id, storage)
	application.fetcherFactory = ReviewsFetcher
	application.parserFactory = ReviewsParser
	
	application.loadAndUpdateReviews(country = args.country, limit = args.limit)
	
	reviews = application.getLatestReviews(country = args.country, limit = args.limit)
	
	for review in reviews:			
		print "[%d stars] %s by %s on %s" % (review.rating, review.version, review.author, review.date)
		print " (%s) %s" % (review.title, review.text)
		print "-------------------------------------------------------------------------------------------"
		
	