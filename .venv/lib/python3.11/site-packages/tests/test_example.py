# Unit testing
import unittest

# Operating system
import os

# regular expression library
import re

# safe queue 
import sys
if (sys.version_info > (3, 0)):
  from queue import Queue
else:
  from Queue import Queue
  
# Time utility
import time

# Serp API search
from serpapi import GoogleSearch

# download file with wget
#import wget

class TestExample(unittest.TestCase):

    def setUp(self):
        GoogleSearch.SERP_API_KEY = os.getenv("API_KEY","demo")

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_google_images(self):
        search = GoogleSearch({"q": "coffe", "tbm": "isch"})
        for image_result in search.get_json()['images_results']:
            try:
                link = image_result["original"]
                print("link is found: " + link)
                # uncomment the line below to down the original image
                # wget.download(link, '.')
            except:
                print("link is not found.")
                pass
            # https://github.com/serpapi/showcase-serpapi-tensorflow-keras-image-training/blob/master/fetch.py

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_async(self):
        # store searches
        search_queue = Queue()
        
        # Serp API search
        search = GoogleSearch({
            "location": "Austin,Texas",
            "async": True
        })
        
        # loop through companies
        for company in ['amd','nvidia','intel']:
          print("execute async search: q = " + company)
          search.params_dict["q"] = company
          data = search.get_dict()
          print("add search to the queue where id: " + data['search_metadata']['id'])
          # add search to the search_queue
          search_queue.put(data)
        
        print("wait until all search statuses are cached or success")
        
        # Create regular search
        search = GoogleSearch({"async": True})
        while not search_queue.empty():
          data = search_queue.get()
          search_id = data['search_metadata']['id']

          # retrieve search from the archive - blocker
          print(search_id + ": get search from archive")
          search_archived =  search.get_search_archive(search_id)
          print(search_id + ": status = " + search_archived['search_metadata']['status'])
          
          # check status
          if re.search('Cached|Success', search_archived['search_metadata']['status']):
            print(search_id + ": search done with q = " + search_archived['search_parameters']['q'])
          else:
            # requeue search_queue
            print(search_id + ": requeue search")
            search_queue.put(search)
            # wait 1s
            time.sleep(1)
        # search is over.
        print('all searches completed')
        
    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_google_news(self):
        search = GoogleSearch({
            "q": "coffe",   # search search
            "tbm": "nws",   # news
            "tbs": "qdr:d", # last 24h
            "num": 10
        })
        for offset in [0,1,2]:
            search.params_dict["start"] = offset * 10
            data = search.get_json()
            for news_result in data['news_results']:
                print(str(news_result['position'] + offset * 10) + " - " + news_result['title'])

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_google_shopping(self):
        search = GoogleSearch({
            "q": "coffe",   # search search
            "tbm": "shop",  # news
            "tbs": "p_ord:rv", # last 24h
            "num": 100
        })
        data = search.get_json()
        for shopping_result in data['shopping_results']:
            print(str(shopping_result['position']) + " - " + shopping_result['title'])

    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_by_location(self):
        for city in ["new york", "paris", "berlin"]:
            location = GoogleSearch({}).get_location(city, 1)[0]["canonical_name"]
            search = GoogleSearch({
                "q": "best coffee shop",   # search search
                "location": location,
                "num": 10,
                "start": 0
            })
            data = search.get_json()
            top_result = data['organic_results'][0]["title"]
            print("top coffee result for " + location + " is: " + top_result)


if __name__ == '__main__':
    unittest.main()
