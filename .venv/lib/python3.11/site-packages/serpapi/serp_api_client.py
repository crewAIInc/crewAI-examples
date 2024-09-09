import requests
import json

GOOGLE_ENGINE = 'google'
BING_ENGINE = 'bing'
BAIDU_ENGINE = 'baidu'
GOOGLE_SCHOLAR_ENGINE = 'google_scholar'
YANDEX_ENGINE = 'yandex'
EBAY_ENGINE = 'ebay'
YAHOO_ENGINE = 'yahoo'
HOME_DEPOT_ENGINE = 'home_depot'

class SerpApiClient(object):
    """SerpApiClient enables to query any any search engines supported by SerpApi and parse the result.
    ```python
    from serpapi import GoogleSearch
    search = SerpApiClient({
        "q": "Coffee", 
        "location": "Austin,Texas", 
        "engine": "google",
        "api_key": "<your private key>"
        })
	data = search.get_json()
    ```

    https://serpapi.com/search-api
    """

    BACKEND = "https://serpapi.com"
    SERP_API_KEY = None

    def __init__(self, params_dict, engine = None):
        self.params_dict = params_dict
        self.engine = engine

    def construct_url(self, path = "/search"):
        self.params_dict['source'] = 'python'
        if self.SERP_API_KEY:
            self.params_dict['serp_api_key'] = self.SERP_API_KEY
        if self.engine:
            if not 'engine' in self.params_dict:
                self.params_dict['engine'] = self.engine
        if not 'engine' in self.params_dict:
            raise "engine must be defined in params_dict or engine"

        return self.BACKEND + path, self.params_dict

    def get_results(self, path = '/search'):
        url = None
        try:
            url, parameter = self.construct_url(path)
            response = requests.get(url, parameter, timeout=60000)
            return response.text
        except requests.HTTPError as e:
            print("fail: " + url)
            print(e, e.response.status_code)
            raise e

    def get_html(self):
        """Returns:
            Raw HTML search result from Gooogle
        """
        return self.get_results()

    def get_json(self):
        """Returns:
            Formatted JSON search results using json package
        """
        self.params_dict["output"] = "json"
        return json.loads(self.get_results())

    def get_raw_json(self):
        """Returns:
            Formatted JSON search result as string
        """
        self.params_dict["output"] = "json"
        return self.get_results()

    def get_dictionary(self):
        """Returns:
            Dict with the formatted response content
        """
        return dict(self.get_json())

    def get_dict(self):
        """Returns:
            Dict with the formatted response content
            (alias for get_dictionary)
        """
        return self.get_dictionary()

    def get_object(self):
        """Returns a dynamically created python object wrapping the data structure
        """
        # iterative over response hash
        node = self.get_dictionary()
        # create dynamic python object
        return self.make_pyobj("response", node)

    def make_pyobj(self, name, node):
        pytype = type(name, (object, ), {})
        pyobj = pytype()

        if isinstance(node, list):
            setattr(pyobj, name, [])
            for el in node:
                getattr(pyobj, name).append(self.make_pyobj(name, el))
            return pyobj
        elif isinstance(node, dict):
            for name, child in node.items():
                if isinstance(child, list):
                    setattr(pyobj, name, [])
                    for el in child:
                        getattr(pyobj, name).append(self.make_pyobj(name, el))
                elif isinstance(child, dict):
                    setattr(pyobj, name, self.make_pyobj(name, child))
                else:
                    setattr(pyobj, name, child)
        else:
            setattr(pyobj, name, node)

        return pyobj

    def get_search_archive(self, search_id, format = 'json'):
        """Retrieve search result from the Search Archive API
        Parameters:
            search_id (int): unique identifier for the search provided by metadata.id 
            format (string): search format: json or html [optional]
        Returns:
            dict|string: search result from the archive
        """
        result = self.get_results("/searches/{0}.{1}".format(search_id, format))
        if format == 'json':
            result = json.loads(result)
        return result

    def get_account(self):
        """Get account information using Account API
        Returns:
            dict: account information
        """
        return json.loads(self.get_results("/account"))

    def get_location(self, q, limit = 5):
        """Get location using Location API
        Parameters:
            q (string): location (like: city name..)
            limit (int): number of matches returned
        Returns:
            dict: Location matching q
        """
        self.params_dict = {}
        self.params_dict["output"] = "json"
        self.params_dict["q"] = q
        self.params_dict["limit"] = limit
        return json.loads(self.get_results('/locations.json'))

