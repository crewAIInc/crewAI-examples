import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests

class NewsSearchInput(BaseModel):
    """Input schema for Real Time News Search Tool."""
    query: str = Field(..., description="Search query for news articles")

class RealTimeNewsSearchTool(BaseTool):
    name: str = "Real Time News Search"
    description: str = "A tool that searches for real-time news articles based on various filters like query, time published, country, and language."

    args_schema: Type[BaseModel] = NewsSearchInput

    def _run(self, query: str) -> str:
        """Execute the real-time news search tool."""
        try:
            url = "https://real-time-news-data.p.rapidapi.com/search"

            querystring = {
                "query": query,
                "limit": str(10),
                "time_published": "1d",
                "country": "US",
                "lang": "en"
            }

            headers = {
                "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
                "x-rapidapi-host": "real-time-news-data.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                return str(response.json())
            else:
                return f"Error fetching news: HTTP {response.status_code} - {response.text}"

        except Exception as e:
            return f"An error occurred while fetching news: {str(e)}"
