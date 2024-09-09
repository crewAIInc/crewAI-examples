from serpapi.serp_api_client import *

class HomeDepotSearch(SerpApiClient):
    """GoogleScholarSearch enables to search google scholar and parse the result.
    ```python
    from serpapi import HomeDepotSearch
    query = HomeDepotSearch({"q": "chair"})
    data = query.get_json()
    ```

    doc: https://serpapi.com/home-depot-search-api
    """

    def __init__(self, params_dict):
        super(HomeDepotSearch, self).__init__(params_dict, HOME_DEPOT_ENGINE)

    def get_location(self, q, limit = 5):
        raise "location is not supported by Home Depot search engine"
