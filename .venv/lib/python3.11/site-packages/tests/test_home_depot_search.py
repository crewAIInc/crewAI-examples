import random
import unittest
import os
import pprint
from serpapi import HomeDepotSearch

class TestHomeDepotSearchApi(unittest.TestCase):

		def setUp(self):
				HomeDepotSearch.SERP_API_KEY = os.getenv("API_KEY", "demo")

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_json(self):
				search = HomeDepotSearch({"q": "chair"})
				data = search.get_dict()
				self.assertEqual(data["search_metadata"]["status"], "Success")
				self.assertIsNotNone(data["search_metadata"]["home_depot_url"])
				self.assertIsNotNone(data["search_metadata"]["id"])
				self.assertTrue(len(data["products"]) > 5)
				self.assertIsNotNone(data["products"][0]["title"])

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_object(self):
				search = HomeDepotSearch({"q": "chair"})
				r = search.get_object()
				pp = pprint.PrettyPrinter(indent=2)
				pp.pprint(r)
				self.assertEqual(r.search_metadata.status, "Success")
				self.assertEqual(type(r.products), list)
				self.assertIsNotNone(r.products[0].title)
				self.assertIsNotNone(r.search_metadata.id)
				self.assertIsNotNone(r.search_metadata.home_depot_url)
				self.assertEqual(r.search_parameters.q, "chair")
				self.assertEqual(r.search_parameters.engine, "home_depot")
				self.assertGreater(r.search_information.total_results, 10)

if __name__ == '__main__':
		unittest.main()
