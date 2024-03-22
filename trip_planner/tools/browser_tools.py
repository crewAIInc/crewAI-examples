import os
import json
import requests

from crewai import Agent, Task
from langchain.tools import tool
from unstructured.partition.html import partition_html

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY") #pulled from .env file


class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website):
    """Useful to scrape and summarize a website content"""
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
          'Perform thorough research and generate insightful summaries based on the content at hand.',
          backstory=
          "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
          allow_delegation=False,
          llm = ChatOpenAI(api_key = api_key, temperature = 0))
      task = Task(
          agent=agent,
          expected_output="Detailed summary of the content information",
          description= f'Analyze and summarize the content below, making sure to include the most relevant 
                        information in the summary. Return only the summary, nothing else.\n\nCONTENT\n----
                        ------\n{chunk}'
      )
      summary = task.execute()
      summaries.append(summary)
    return "\n\n".join(summaries)
