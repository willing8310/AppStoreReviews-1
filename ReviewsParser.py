# -*- coding: utf-8 -*-

''' AppStore Reviews
	Evgeniy Shurakov <github@shurakov.name>
'''

import re
import urlparse

from elementtree import ElementTree

from datetime import datetime
from datetime import date
from datetime import time

from models.Review import Review

months = {
	u"janv" : 1,
	u"févr" : 2,
	u"mars" : 3,
	u"avr" : 4,
	u"mai" : 5,
	u"juin" : 6,
	u"juil" : 7,
	u"août" : 8,
	u"sept" : 9,
	u"oct" : 10,
	u"nov" : 11,
	u"déc" : 12,
	
	u"jan" : 1,
	u"feb" : 2,
	u"mar" : 3,
	u"apr" : 4,
	u"may" : 5,
	u"jun" : 6,
	u"jul" : 7,
	u"aug" : 8,
	u"sep" : 9,
	u"oct" : 10,
	u"nov" : 11,
	u"dec" : 12,
	
	u"gen" : 1,
	u"mag" : 5,
	u"giu" : 6,
	u"lug" : 7,
	u"ago" : 8,
	u"set" : 9,
	u"ott" : 10,
	u"dic" : 12
}

class ReviewsParser:
	
	source = None
	reviews = None
	
	lastDate = None
	
	@staticmethod
	def parser(source):
		return ReviewsParser(source);
	
	def __init__(self, source):
		self.source = source
		self.reviews = []
		self.lastDate = datetime.combine(date.today(), time(0, 0))

	def parse(self):
		
		root = ElementTree.parse(self.source).getroot()
		
		for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/'):
			
			review = self._parseItem(node)				
			self.reviews.append(review)
		
		return self.reviews


		
	def _parseItem(self, item):
		review = Review()
		
		textNode = item.find("{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle")
		if textNode is not None:
			review.text = textNode.text
		
		authorNode = item.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL/{http://www.apple.com/itms/}b")
		if authorNode is not None:
			review.author = authorNode.text.strip()
		else:
			review.author = u"Anonymous"
		
		ratingNode = item.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView")
		try:
			review.rating = int(ratingNode.attrib['alt'].strip(' stars'))
		except KeyError:
			review.rating = 0
		
		reportConcernNode = item.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}GotoURL")
		
		if reportConcernNode is not None and reportConcernNode.attrib is not None and "url" in reportConcernNode.attrib:
			parseResult = urlparse.urlparse(reportConcernNode.attrib["url"])
			queryResult = urlparse.parse_qs(parseResult.query)
			if queryResult is not None and "userReviewId" in queryResult:
				review.identifier = queryResult["userReviewId"][0]
		
								
		titleNode = item.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b")
		if titleNode is not None:
			review.title = titleNode.text
		
		versionAndDateNode = item.find("{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL")
		if versionAndDateNode is not None:
			regexpResult = re.search("Version ([^\n^\ ]+)", versionAndDateNode.tail)
			if regexpResult:
				review.version = regexpResult.group(1)
										
																						
			regexpResult = re.search("(((?P<day1>\d{1,2})\.(?P<month1>\d{1,2})\.)|((?P<month2>\w+) (?P<day2>\d{1,2})[ ,]+)|((?P<day3>\d{1,2})[ \-](?P<month3>.+?)\.?[ \-]))(?P<year>\d{4})", versionAndDateNode.tail)
						
			if regexpResult:
				dateObject = None
				
				dict = regexpResult.groupdict()
				
				if dict["day1"] is not None:
					dateObject = datetime(int(dict["year"]), int(dict["month1"]), int(dict["day1"]), 0, 0, 0)
				elif dict["day2"] is not None:
					k = dict["month2"].lower()
					if k in months:
						dateObject = datetime(int(dict["year"]), int(months[k]), int(dict["day2"]), 0, 0, 0)
					else:
						regexpResult = re.search(".*?Version\s.*?[\s\-]+?([^\s\-].+)", versionAndDateNode.tail)
						if regexpResult:
							print regexpResult.group(1)
				else:
					k = dict["month3"].lower()
					if k in months:
						dateObject = datetime(int(dict["year"]), int(months[k]), int(dict["day3"]), 0, 0, 0)
					else:
						regexpResult = re.search(".*?Version\s.*?[\s\-]+?([^\s\-].+)", versionAndDateNode.tail)
						if regexpResult:
							print regexpResult.group(1)
									
				review.date = dateObject
			else:
				regexpResult = re.search(".*?Version\s.*?[\s\-]+?([^\s\-].+)", versionAndDateNode.tail)
				if regexpResult:
					print regexpResult.group(1)
		
		if review.date is None:
			review.date = self.lastDate
		else:
			self.lastDate = review.date
			
		return review
