import random
import unittest
import os
from serpapi import GoogleSearch

class TestAccountApi(unittest.TestCase):

    def setUp(self):
        GoogleSearch.SERP_API_KEY = os.getenv("API_KEY","demo")

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_get_account(self):
        search = GoogleSearch({})
        account = search.get_account()
        self.assertIsNotNone(account.get("account_id"))
        self.assertEqual(account.get("api_key"), GoogleSearch.SERP_API_KEY)

if __name__ == '__main__':
    unittest.main()
