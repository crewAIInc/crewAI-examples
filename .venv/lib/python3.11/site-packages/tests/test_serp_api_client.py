import random
import unittest
import os
import pprint
from serpapi import SerpApiClient

# This test shows how to extends SerpApiClient
#  without using search engine wrapper.
# 
class TestSerpSearchApi(unittest.TestCase):

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_json(self):
				search = SerpApiClient({
					"q": "Coffee", 
					"location": "Austin,Texas", 
					"engine": "google_scholar",
					"api_key": os.getenv("API_KEY", "demo")
					})
				data = search.get_json()
				self.assertIsNotNone(data["organic_results"][0]["title"])
				pp = pprint.PrettyPrinter(indent=2)
				pp.pprint(data)

if __name__ == '__main__':
		unittest.main()
