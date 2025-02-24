from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from serpapi import GoogleSearch
import os


class FlightSearchToolInput(BaseModel):
    """Input schema for FlightSearchTool."""
    departure_id: str = Field(..., description="3 letter airport code of the departure location.")
    arrival_id: str = Field(..., description="3 letter airport code of the arrival location.")
    outbound_date: str = Field(..., description="Date of the outbound travel in YYYY-MM-DD format.")
    return_date: str = Field(..., description="Date of the return travel in YYYY-MM-DD format.")

class FlightSearchTool(BaseTool):
    name: str = "Flight Search Tool"
    description: str = (
        "A tool to search for flights using the SerpAPI Google Flights API. Input should be a detailed description of the desired flight, including origin, destination, dates, and any preferences."
    )
    args_schema: Type[BaseModel] = FlightSearchToolInput

    def _run(self, departure_id: str, arrival_id: str, outbound_date: str, return_date: str) -> str:
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "currency": "USD",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY"),
        }

        search = GoogleSearch(params)
        return search.get_dict()
