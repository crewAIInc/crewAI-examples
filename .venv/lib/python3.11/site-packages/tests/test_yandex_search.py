import random
import unittest
import os
import pprint
from serpapi import YandexSearch

class TestYandexSearchApi(unittest.TestCase):

		def setUp(self):
				YandexSearch.SERP_API_KEY = os.getenv("API_KEY", "demo")

		@unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
		def test_get_json(self):
				search = YandexSearch({"text": "Coffee"})
				data = search.get_json()
				self.assertEqual(data["search_metadata"]["status"], "Success")
				self.assertIsNotNone(data["search_metadata"]["yandex_url"])
				self.assertIsNotNone(data["search_metadata"]["id"])
				self.assertIsNotNone(data["organic_results"][0]["title"])
				pp = pprint.PrettyPrinter(indent=2)
				pp.pprint(data)

if __name__ == '__main__':
		unittest.main()
