import os
from typing import Any, Optional, Type
from pydantic.v1 import BaseModel, Field
from crewai_tools import RagTool
from sec_api import QueryApi  # Make sure to have sec_api installed
from embedchain.models.data_type import DataType
import requests
import html2text
import re

class FixedSEC10KToolSchema(BaseModel):
    """Input for SEC10KTool."""
    search_query: str = Field(
        ...,
        description="Mandatory query you would like to search from the 10-K report",
    )

class SEC10KToolSchema(FixedSEC10KToolSchema):
    """Input for SEC10KTool."""
    stock_name: str = Field(
        ..., description="Mandatory valid stock name you would like to search"
    )

class SEC10KTool(RagTool):
    name: str = "Search in the specified 10-K form"
    description: str = "A tool that can be used to semantic search a query from a 10-K form for a specified company."
    args_schema: Type[BaseModel] = SEC10KToolSchema

    def __init__(self, stock_name: Optional[str] = None, **kwargs):
        print("enter init")
        # exit()
        super().__init__(**kwargs)
        if stock_name is not None:
            content = self.get_10k_url_content(stock_name)
            if content:
                self.add(content)
                # print("exit init")
                # exit()
                self.description = f"A tool that can be used to semantic search a query from {stock_name}'s latest 10-K SEC form's content as a txt file."
                self.args_schema = FixedSEC10KToolSchema
                self._generate_description()

    def get_10k_url_content(self, stock_name: str) -> Optional[str]:
        """Fetches the URL content as txt of the latest 10-K form for the given stock name."""
        try:
            queryApi = QueryApi(api_key=os.environ['SEC_API_API_KEY'])
            query = {
                "query": {
                    "query_string": {
                        "query": f"ticker:{stock_name} AND formType:\"10-K\""
                    }
                },
                "from": "0",
                "size": "1",
                "sort": [{ "filedAt": { "order": "desc" }}]
            }
            filings = queryApi.get_filings(query)['filings']
            if len(filings) == 0:
                print("No filings found for this stock.")
                return None

            url = filings[0]['linkToFilingDetails']
            
            headers = {
                "User-Agent": "crewai.com bisan@crewai.com",
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  
            h = html2text.HTML2Text()
            h.ignore_links = False
            text = h.handle(response.content.decode("utf-8"))

            text = re.sub(r"[^a-zA-Z$0-9\s\n]", "", text)
            return text
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error fetching 10-K URL: {e}")
            return None

    def add(self, *args: Any, **kwargs: Any) -> None:
        kwargs["data_type"] = DataType.TEXT
        super().add(*args, **kwargs)

    def _run(self, search_query: str, **kwargs: Any) -> Any:
        return super()._run(query=search_query, **kwargs)


class FixedSEC10QToolSchema(BaseModel):
    """Input for SEC10QTool."""
    search_query: str = Field(
        ...,
        description="Mandatory query you would like to search from the 10-Q report",
    )

class SEC10QToolSchema(FixedSEC10QToolSchema):
    """Input for SEC10QTool."""
    stock_name: str = Field(
        ..., description="Mandatory valid stock name you would like to search"
    )

class SEC10QTool(RagTool):
    name: str = "Search in the specified 10-Q form"
    description: str = "A tool that can be used to semantic search a query from a 10-Q form for a specified company."
    args_schema: Type[BaseModel] = SEC10QToolSchema

    def __init__(self, stock_name: Optional[str] = None, **kwargs):
        print("enter init")
        # exit()
        super().__init__(**kwargs)
        if stock_name is not None:
            content = self.get_10q_url_content(stock_name)
            if content:
                self.add(content)
                self.description = f"A tool that can be used to semantic search a query from {stock_name}'s latest 10-Q SEC form's content as a txt file."
                self.args_schema = FixedSEC10QToolSchema
                self._generate_description()

    def get_10q_url_content(self, stock_name: str) -> Optional[str]:
        """Fetches the URL content as txt of the latest 10-Q form for the given stock name."""
        try:
            queryApi = QueryApi(api_key=os.environ['SEC_API_API_KEY'])
            query = {
                "query": {
                    "query_string": {
                        "query": f"ticker:{stock_name} AND formType:\"10-Q\""
                    }
                },
                "from": "0",
                "size": "1",
                "sort": [{ "filedAt": { "order": "desc" }}]
            }
            filings = queryApi.get_filings(query)['filings']
            if len(filings) == 0:
                print("No filings found for this stock.")
                return None

            url = filings[0]['linkToFilingDetails']
            
            headers = {
                "User-Agent": "crewai.com bisan@crewai.com",
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            h = html2text.HTML2Text()
            h.ignore_links = False
            text = h.handle(response.content.decode("utf-8"))

            # Removing all non-English words, dollar signs, numbers, and newlines from text
            text = re.sub(r"[^a-zA-Z$0-9\s\n]", "", text)
            return text
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error fetching 10-Q URL: {e}")
            return None

    def add(self, *args: Any, **kwargs: Any) -> None:
        kwargs["data_type"] = DataType.TEXT
        super().add(*args, **kwargs)

    def _run(self, search_query: str, **kwargs: Any) -> Any:
        return super()._run(query=search_query, **kwargs)

