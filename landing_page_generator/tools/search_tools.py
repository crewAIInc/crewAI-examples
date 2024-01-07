import os
import json
import requests
from langchain.tools import tool


class SearchTools():

  @tool("Search the internet")
  def search_internet(query):
    """Useful to search the internet 
    about a a given topic and return relevant results"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    results = response.json()['organic']
    string = []
    for result in results:
      string.append('\n'.join([
          f"Title: {result['title']}", f"Link: {result['link']}",
          f"Snippet: {result['snippet']}", "\n-----------------"
      ]))

    return '\n'.join(string)
