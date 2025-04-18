import json
import os

import requests
from crewai import Agent, Task
from unstructured.partition.html import partition_html
from langchain_community.llms import Ollama
from langchain_core.tools import tool

class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(url):
    """Useful to scrape and summarize a website content, just pass a string with
    only the full url, no need for a final slash `/`, eg: https://google.com or https://clearbit.com/about-us"""
    # Check if SCRAPINGANT_API_KEY is defined and has a non-empty value
    scrapingant_api_key = os.environ.get('SCRAPINGANT_API_KEY')
    if scrapingant_api_key:
      # Use the ScrapingAnt API if the key is available
      scraping_url = f"https://api.scrapingant.com/v2/general?x-api-key={scrapingant_api_key}&url={url}"
    else:
       # Otherwise, use the Browserless API
        browserless_api_key = os.environ['BROWSERLESS_API_KEY']
        scraping_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
    payload = json.dumps({"url": url})
    headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
    response = requests.request("POST", scraping_url, headers=headers, data=payload)
    elements = partition_html(text=response.text)
    content = "\n\n".join([str(el) for el in elements])
    content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
    summaries = []
    for chunk in content:
      agent = Agent(
          role='Principal Researcher',
          goal=
          'Do amazing researches and summaries based on the content you are working with',
          backstory=
          "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
          llm=Ollama(model=os.environ['MODEL']),
          allow_delegation=False)
      task = Task(
          expected_output="A long summary of the product features and description.",
          agent=agent,
          description=
          f'Analyze and make a LONG summary the content below, make sure to include the ALL relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
      )
      summary = task.execute()
      summaries.append(summary)
      content = "\n\n".join(summaries)
    return f'\nScrapped Content: {content}\n'
