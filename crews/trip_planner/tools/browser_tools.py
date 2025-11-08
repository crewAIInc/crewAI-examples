import json
import os

import requests
from crewai import Agent, Task
from crewai.tools import tool
from unstructured.partition.html import partition_html


class BrowserTools():

  @tool("Scrape website content")
  def scrape_and_summarize_website(website: str) -> str:
    """Useful to scrape and summarize a website content.
    
    Args:
        website: The URL of the website to scrape and summarize
    
    Returns:
        Summarized content from the website
    """
    token = os.getenv('BROWSERLESS_API_KEY')
    try:
      if token:
        url = f"https://chrome.browserless.io/content?token={token}"
        payload = json.dumps({"url": website})
        headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload, timeout=60)
        html_text = response.text
      else:
        # Fallback: fetch directly if no Browserless token is set
        response = requests.get(website, timeout=60)
        response.raise_for_status()
        html_text = response.text
    except Exception as e:
      return f"Error fetching website content: {str(e)}"

    elements = partition_html(text=html_text)
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
          allow_delegation=False)
      task = Task(
          agent=agent,
          description=
          f'Analyze and summarize the content bellow, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}',
          expected_output="A concise markdown summary capturing key facts, figures, entities, and links (if present)."
      )
      try:
        summary = task.execute()
      except Exception:
        # Fallback summarization if LLM execution fails
        sample = (chunk[:1000] + '...') if len(chunk) > 1000 else chunk
        summary = f"Fallback summary (no LLM available):\n\n{sample}"
      summaries.append(summary)
    return "\n\n".join(summaries)
