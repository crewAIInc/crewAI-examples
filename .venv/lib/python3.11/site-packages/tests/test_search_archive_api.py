import random
import unittest
import os
from serpapi import GoogleSearch

class TestSearchArchiveApi(unittest.TestCase):

    def setUp(self):
        GoogleSearch.SERP_API_KEY = os.getenv("API_KEY","demo")

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_get_search_archive(self):
        search = GoogleSearch({"q": "Coffee", "location": "Austin,Texas"})
        search_result = search.get_dictionary()
        search_id = search_result.get("search_metadata").get("id")
        archived_search_result = GoogleSearch({}).get_search_archive(search_id, 'json')
        self.assertEqual(archived_search_result.get("search_metadata").get("id"), search_id)
        html_buffer = GoogleSearch({}).get_search_archive(search_id, 'html')
        self.assertGreater(len(html_buffer), 10000)

if __name__ == '__main__':
    unittest.main()
