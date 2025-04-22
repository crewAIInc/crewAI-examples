from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from serpapi import GoogleSearch
import os


class AccommodationSearchToolInput(BaseModel):
    """Input schema for AccommodationSearchTool."""
    location: str = Field(..., description="Location to search for accommodations.")
    checkin_date: str = Field(..., description="Date of the check-in in YYYY-MM-DD format.")
    checkout_date: str = Field(..., description="Date of the check-out in YYYY-MM-DD format.")


class AccommodationSearchTool(BaseTool):
    name: str = "Accommodation Search Tool"
    description: str = (
        "A tool to search for accommodations using the SerpAPI Google Accommodation API. Input should be a detailed description of the desired accommodation, including location, and dates."
    )
    args_schema: Type[BaseModel] = AccommodationSearchToolInput

    def _run(self, location: str, checkin_date: str, checkout_date: str) -> str:
        params = {
            "engine": "google_hotels",
            "q": f"{location} Hotels & Resorts",
            "check_in_date": checkin_date,
            "check_out_date": checkout_date,
            "adults": "1",
            "currency": "USD",
            "gl": "us",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        search = GoogleSearch(params)
        return search.get_dict()
