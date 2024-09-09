from serpapi.serp_api_client import *

class BaiduSearch(SerpApiClient):
    """BaiduSearch enables to search baidu and parse the result.
    ```python
    from serpapi import BaiduSearch
    query = BaiduSearch({"q": "coffee"})
    data = query.get_json()
    ```

    doc: https://serpapi.com/baidu-search-api
    """

    def __init__(self, params_dict):
        super(BaiduSearch, self).__init__(params_dict, BAIDU_ENGINE)

    def get_location(self, q, limit = 5):
        raise "location is not supported by Baidu search engine at this time"
