from serpapi.serp_api_client import *

class BingSearch(SerpApiClient):
    """BingSearch enables to search bing and parse the result.
    ```python
    from serpapi import BingSearch
    query = BingSearch({"q": "coffee", "location": "Austin,Texas"})
    data = query.get_json()
    ```

    doc: https://serpapi.com/bing-search-api
    """

    def __init__(self, params_dict):
        super(BingSearch, self).__init__(params_dict, BING_ENGINE)
