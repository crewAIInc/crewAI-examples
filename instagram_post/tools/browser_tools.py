import json
import os

import requests
from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html

from langchain.llms import Ollama

class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content, just pass a string with
    only the full url, no need for a final slash `/`, eg: https://google.com or https://clearbit.com/about-us"""
    url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"
    payload = json.dumps({"url": website})
    headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
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
          agent=agent,
          description=
          f'Analyze and make a LONG summary the content bellow, make sure to include the ALL relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
      )
      summary = task.execute()
      summaries.append(summary)
      content = "\n\n".join(summaries)
    return f'\nScrapped Content: {content}\n'
