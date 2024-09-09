import random
import unittest
import os
import pprint
from serpapi import GoogleSearch

class TestSearchApi(unittest.TestCase):

		def setUp(self):
				GoogleSearch.SERP_API_KEY = os.getenv("API_KEY", "demo")

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_json(self):
				search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
				data = search.get_json()
				self.assertEqual(data["search_metadata"]["status"], "Success")
				self.assertIsNotNone(data["search_metadata"]["google_url"])
				self.assertIsNotNone(data["search_metadata"]["id"])
				# pp = pprint.PrettyPrinter(indent=2)
				# pp.pprint(data['local_results'])
				self.assertIsNotNone(data['local_results']['places'][0])

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_json(self):
				search = GoogleSearch({"q": "Coffee", "engine": "google_scholar"})
				data = search.get_json()
				self.assertIsNotNone(data["organic_results"][0]["title"])

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_dict(self):
				search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
				data = search.get_dict()
				self.assertIsNotNone(data.get('local_results'))

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_dictionary(self):
				search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
				data = search.get_dictionary()
				self.assertIsNotNone(data.get('local_results'))

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_html(self):
				search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
				data = search.get_html()
				self.assertGreater(len(data), 10)

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_object(self):
				search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
				r = search.get_object()
				self.assertEqual(type(r.organic_results), list)
				self.assertIsNotNone(r.organic_results[0].title)
				self.assertIsNotNone(r.search_metadata.id)
				self.assertIsNotNone(r.search_metadata.google_url)
				self.assertEqual(r.search_parameters.q, "Coffee")
				self.assertEqual(r.search_parameters.engine, "google")
				self.assertGreater(r.search_information.total_results, 10)

if __name__ == '__main__':
		unittest.main()
