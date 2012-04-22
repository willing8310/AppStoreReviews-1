
import unittest

import os
import json

from ReviewsParser import ReviewsParser


class TestReviewsParser(unittest.TestCase):
	
#	def setUp(self):	
#	def tearDown(self):
	
	def test_reviews(self):
		parser = ReviewsParser(os.path.join(os.path.dirname(__file__), "data", "reviews_1.xml"))
		reviews = parser.parse()
		self.assertIs(type(reviews), list);
		
		fo = open(os.path.join(os.path.dirname(__file__), "data", "reviews_1.json"))
		reviewsJson = json.load(fo)
		
		self.assertEquals(len(reviewsJson), len(reviews));
		
		i = 0
		for review in reviews:
			self.assertEquals(review.author, reviewsJson[i]["author"])
			self.assertEquals(review.title, reviewsJson[i]["title"])
			self.assertEquals(review.rating, reviewsJson[i]["rating"])
			self.assertEquals(review.version, reviewsJson[i]["version"])
			self.assertEquals(review.date.strftime("%d.%m.%Y"), reviewsJson[i]["date"])
			
			i += 1


if __name__ == '__main__':
	unittest.main()