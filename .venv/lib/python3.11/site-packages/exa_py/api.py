from __future__ import annotations
from dataclasses import dataclass
import dataclasses
import re
import requests
from typing import (
    List,
    Optional,
    Dict,
    Generic,
    TypeVar,
    overload,
    Union,
    Literal,
)
from typing_extensions import TypedDict


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase.

    Args:
        snake_str (str): The string in snake_case format.

    Returns:
        str: The string converted to camelCase format.
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_camel_case(data: dict) -> dict:
    """Convert keys in a dictionary from snake_case to camelCase.

    Args:
        data (dict): The dictionary with keys in snake_case format.

    Returns:
        dict: The dictionary with keys converted to camelCase format.
    """
    return {snake_to_camel(k): v for k, v in data.items() if v is not None}


def camel_to_snake(camel_str: str) -> str:
    """Convert camelCase string to snake_case.

    Args:
        camel_str (str): The string in camelCase format.

    Returns:
        str: The string converted to snake_case format.
    """
    snake_str = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake_str).lower()


def to_snake_case(data: dict) -> dict:
    """Convert keys in a dictionary from camelCase to snake_case.

    Args:
        data (dict): The dictionary with keys in camelCase format.

    Returns:
        dict: The dictionary with keys converted to snake_case format.
    """
    return {camel_to_snake(k): v for k, v in data.items()}


SEARCH_OPTIONS_TYPES = {
    "query": [str],  # The query string.
    "num_results": [int],  # Number of results (Default: 10, Max for basic: 10).
    "include_domains": [
        list
    ],  # Domains to search from; exclusive with 'exclude_domains'.
    "exclude_domains": [list],  # Domains to omit; exclusive with 'include_domains'.
    "start_crawl_date": [str],  # Results after this crawl date. ISO 8601 format.
    "end_crawl_date": [str],  # Results before this crawl date. ISO 8601 format.
    "start_published_date": [
        str
    ],  # Results after this publish date; excludes links with no date. ISO 8601 format.
    "end_published_date": [
        str
    ],  # Results before this publish date; excludes links with no date. ISO 8601 format.
    "use_autoprompt": [bool],  # Convert query to Exa (Higher latency, Default: false).
    "type": [
        str
    ],  # 'keyword' or 'neural' (Default: neural). Choose 'neural' for high-quality, semantically relevant content in popular domains. 'Keyword' is for specific, local, or obscure queries.
    "category": [
        str
    ],  # A data category to focus on, with higher comprehensivity and data cleanliness. Currently, the only category is company.
}

FIND_SIMILAR_OPTIONS_TYPES = {
    "url": [str],
    "num_results": [int],
    "include_domains": [list],
    "exclude_domains": [list],
    "start_crawl_date": [str],
    "end_crawl_date": [str],
    "start_published_date": [str],
    "end_published_date": [str],
    "exclude_source_domain": [bool],
    "category": [str],
}

CONTENTS_OPTIONS_TYPES = {
    "ids": [list],
    "text": [dict, bool],
    "highlights": [dict, bool],
}


def validate_search_options(
    options: Dict[str, Optional[object]], expected: dict
) -> None:
    """Validate an options dict against expected types and constraints.

    Args:
        options (Dict[str, Optional[object]]): The options to validate.
        expected (dict): The expected types for each option.

    Raises:
        ValueError: If an invalid option or option type is provided.
    """
    for key, value in options.items():
        if key not in expected:
            raise ValueError(f"Invalid option: '{key}'")
        if not any(isinstance(value, t) for t in expected[key]):
            raise ValueError(
                f"Invalid type for option '{key}': Expected one of {expected[key]}, got {type(value)}"
            )


class TextContentsOptions(TypedDict, total=False):
    """A class representing the options that you can specify when requesting text

    Attributes:
        max_characters (int): The maximum number of characters to return. Default: None (no limit).
        include_html_tags (bool): If true, include HTML tags in the returned text. Default false.
    """

    max_characters: int
    include_html_tags: bool


class HighlightsContentsOptions(TypedDict, total=False):
    """A class representing the options that you can specify when requesting highlights

    Attributes:
        query (str): The query string for the highlights. if not specified, defaults to a generic summarization query.
        num_sentences (int): Size of highlights to return, in sentences. Default: 5
        highlights_per_url (int): The number of highlights to return per URL. Default: 1
    """

    query: str
    num_sentences: int
    highlights_per_url: int


@dataclass
class _Result:
    """A class representing the base fields of a search result.

    Attributes:
        title (str): The title of the search result.
        url (str): The URL of the search result.
        id (str): The temporary ID for the document.
        score (float, optional): A number from 0 to 1 representing similarity between the query/url and the result.
        published_date (str, optional): An estimate of the creation date, from parsing HTML content.
        author (str, optional): If available, the author of the content.
    """

    url: str
    id: str
    title: Optional[str] = None
    score: Optional[float] = None
    published_date: Optional[str] = None
    author: Optional[str] = None

    def __str__(self):
        return (
            f"Title: {self.title}\n"
            f"URL: {self.url}\n"
            f"ID: {self.id}\n"
            f"Score: {self.score}\n"
            f"Published Date: {self.published_date}\n"
            f"Author: {self.author}\n"
        )


@dataclass
class Result(_Result):
    """
    A class representing a search result with optional text and highlights.

    Attributes:
        text (str, optional): The text of the search result page.
        highlights (List[str], optional): The highlights of the search result.
        highlight_scores (List[float], optional): The scores of the highlights of the search result.
    """

    text: Optional[str] = None
    highlights: Optional[List[str]] = None
    highlight_scores: Optional[List[float]] = None

    def __str__(self):
        base_str = super().__str__()
        return base_str + (
            f"Text: {self.text}\n"
            f"Highlights: {self.highlights}\n"
            f"Highlight Scores: {self.highlight_scores}\n"
        )


@dataclass
class ResultWithText(_Result):
    """
    A class representing a search result with text present.

    Attributes:
        text (str): The text of the search result page.
    """

    text: str = dataclasses.field(default_factory=str)

    def __str__(self):
        base_str = super().__str__()
        return base_str + f"Text: {self.text}\n"


@dataclass
class ResultWithHighlights(_Result):
    """
    A class representing a search result with highlights present.

    Attributes:
        highlights (List[str]): The highlights of the search result.
        highlight_scores (List[float]): The scores of the highlights of the search result.
    """

    highlights: List[str] = dataclasses.field(default_factory=list)
    highlight_scores: List[float] = dataclasses.field(default_factory=list)

    def __str__(self):
        base_str = super().__str__()
        return base_str + (
            f"Highlights: {self.highlights}\n"
            f"Highlight Scores: {self.highlight_scores}\n"
        )


@dataclass
class ResultWithTextAndHighlights(_Result):
    """
    A class representing a search result with text and highlights present.

    Attributes:
        text (str): The text of the search result page.
        highlights (List[str): The highlights of the search result.
        highlight_scores (List[float]): The scores of the highlights of the search result.
    """

    text: str = dataclasses.field(default_factory=str)
    highlights: List[str] = dataclasses.field(default_factory=list)
    highlight_scores: List[float] = dataclasses.field(default_factory=list)

    def __str__(self):
        base_str = super().__str__()
        return base_str + (
            f"Text: {self.text}\n"
            f"Highlights: {self.highlights}\n"
            f"Highlight Scores: {self.highlight_scores}\n"
        )


T = TypeVar("T")


@dataclass
class SearchResponse(Generic[T]):
    """A class representing the response for a search operation.

    Attributes:
        results (List[Result]): A list of search results.
        autoprompt_string (str, optional): The Exa query created by the autoprompt functionality.
    """

    results: List[T]
    autoprompt_string: Optional[str]

    def __str__(self):
        output = "\n\n".join(str(result) for result in self.results)
        if self.autoprompt_string:
            output += f"\n\nAutoprompt String: {self.autoprompt_string}"
        return output


def nest_fields(original_dict: Dict, fields_to_nest: List[str], new_key: str):
    # Create a new dictionary to store the nested fields
    nested_dict = {}

    # Iterate over the fields to be nested
    for field in fields_to_nest:
        # Check if the field exists in the original dictionary
        if field in original_dict:
            # Move the field to the nested dictionary
            nested_dict[field] = original_dict.pop(field)

    # Add the nested dictionary to the original dictionary under the new key
    original_dict[new_key] = nested_dict

    return original_dict


class Exa:
    """A client for interacting with Exa API."""

    def __init__(
        self,
        api_key: Optional[str],
        base_url: str = "https://api.exa.ai",
        user_agent: str = "metaphor-python 1.0.2",
    ):
        """Initialize the Exa client with the provided API key and optional base URL and user agent.

        Args:
            api_key (str): The API key for authenticating with the Exa API.
            base_url (str, optional): The base URL for the Exa API. Defaults to "https://api.exa.ai".
        """
        if api_key is None:
            import os

            api_key = os.environ.get("EXA_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided as argument or in EXA_API_KEY environment variable"
                )
        self.base_url = base_url
        self.headers = {"x-api-key": api_key, "User-Agent": user_agent}

    def request(self, endpoint: str, data):
        res = requests.post(self.base_url + endpoint, json=data, headers=self.headers)
        if res.status_code != 200:
            raise ValueError(
                f"Request failed with status code {res.status_code}: {res.text}"
            )
        return res.json()

    def search(
        self,
        query: str,
        *,
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: Optional[bool] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[_Result]:
        """Perform a search with a Exa prompt-engineered query and retrieve a list of relevant results.

        Args:
            query (str): The query string.
            num_results (int, optional): Number of search results to return. Defaults to 10.
            include_domains (List[str], optional): List of domains to include in the search.
            exclude_domains (List[str], optional): List of domains to exclude in the search.
            start_crawl_date (str, optional): Results will only include links crawled after this date.
            end_crawl_date (str, optional): Results will only include links crawled before this date.
            start_published_date (str, optional): Results will only include links with a published date after this date.
            end_published_date (str, optional): Results will only include links with a published date before this date.
            use_autoprompt (bool, optional): If true, convert query to a Exa query. Defaults to False.
            type (str, optional): The type of search, 'keyword' or 'neural'. Defaults to "neural".
            category (str, optional): A data category to focus on, with higher comprehensivity and data cleanliness. Currently, the only category is company.
        Returns:
            SearchResponse: The response containing search results and optional autoprompt string.
        """
        options = {k: v for k, v in locals().items() if k != "self" and v is not None}
        validate_search_options(options, SEARCH_OPTIONS_TYPES)
        options = to_camel_case(options)
        data = self.request("/search", options)
        return SearchResponse(
            [Result(**to_snake_case(result)) for result in data["results"]],
            data["autopromptString"] if "autopromptString" in data else None,
        )

    @overload
    def search_and_contents(
        self,
        query: str,
        *,
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: Optional[bool] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def search_and_contents(
        self,
        query: str,
        *,
        text: Union[TextContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: Optional[bool] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def search_and_contents(
        self,
        query: str,
        *,
        highlights: Union[HighlightsContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: Optional[bool] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithHighlights]:
        ...

    @overload
    def search_and_contents(
        self,
        query: str,
        *,
        text: Union[TextContentsOptions, Literal[True]],
        highlights: Union[HighlightsContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: Optional[bool] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithTextAndHighlights]:
        ...

    def search_and_contents(self, query: str, **kwargs):
        options = {
            k: v
            for k, v in {"query": query, **kwargs}.items()
            if k != "self" and v is not None
        }
        if "text" not in options and "highlights" not in options:
            options["text"] = True
        validate_search_options(
            options, {**SEARCH_OPTIONS_TYPES, **CONTENTS_OPTIONS_TYPES}
        )
        options = nest_fields(options, ["text", "highlights"], "contents")
        options = to_camel_case(options)
        data = self.request("/search", options)
        return SearchResponse(
            [Result(**to_snake_case(result)) for result in data["results"]],
            data["autopromptString"] if "autopromptString" in data else None,
        )

    @overload
    def get_contents(
        self,
        ids: Union[str, List[str], List[_Result]],
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def get_contents(
        self,
        ids: Union[str, List[str], List[_Result]],
        *,
        text: Union[TextContentsOptions, Literal[True]],
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def get_contents(
        self,
        ids: Union[str, List[str], List[_Result]],
        *,
        highlights: Union[HighlightsContentsOptions, Literal[True]],
    ) -> SearchResponse[ResultWithHighlights]:
        ...

    @overload
    def get_contents(
        self,
        ids: Union[str, List[str], List[_Result]],
        *,
        text: Union[TextContentsOptions, Literal[True]],
        highlights: Union[HighlightsContentsOptions, Literal[True]],
    ) -> SearchResponse[ResultWithTextAndHighlights]:
        ...

    def get_contents(self, ids: Union[str, List[str], List[_Result]], **kwargs):
        options = {
            k: v
            for k, v in {"ids": ids, **kwargs}.items()
            if k != "self" and v is not None
        }
        if "text" not in options and "highlights" not in options:
            options["text"] = True
        validate_search_options(options, {**CONTENTS_OPTIONS_TYPES})
        options = to_camel_case(options)
        data = self.request("/contents", options)
        return SearchResponse(
            [Result(**to_snake_case(result)) for result in data["results"]],
            data["autopromptString"] if "autopromptString" in data else None,
        )

    def find_similar(
        self,
        url: str,
        *,
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        exclude_source_domain: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[_Result]:
        options = {k: v for k, v in locals().items() if k != "self" and v is not None}
        validate_search_options(options, FIND_SIMILAR_OPTIONS_TYPES)
        options = to_camel_case(options)
        data = self.request("/findSimilar", options)
        return SearchResponse(
            [Result(**to_snake_case(result)) for result in data["results"]],
            data["autopromptString"] if "autopromptString" in data else None,
        )

    @overload
    def find_similar_and_contents(
        self,
        url: str,
        *,
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        exclude_source_domain: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def find_similar_and_contents(
        self,
        url: str,
        *,
        text: Union[TextContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        exclude_source_domain: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithText]:
        ...

    @overload
    def find_similar_and_contents(
        self,
        url: str,
        *,
        highlights: Union[HighlightsContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        exclude_source_domain: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithHighlights]:
        ...

    @overload
    def find_similar_and_contents(
        self,
        url: str,
        *,
        text: Union[TextContentsOptions, Literal[True]],
        highlights: Union[HighlightsContentsOptions, Literal[True]],
        num_results: Optional[int] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_crawl_date: Optional[str] = None,
        end_crawl_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        exclude_source_domain: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> SearchResponse[ResultWithTextAndHighlights]:
        ...

    def find_similar_and_contents(self, url: str, **kwargs):
        options = {
            k: v
            for k, v in {"url": url, **kwargs}.items()
            if k != "self" and v is not None
        }
        if "text" not in options and "highlights" not in options:
            options["text"] = True
        validate_search_options(
            options, {**FIND_SIMILAR_OPTIONS_TYPES, **CONTENTS_OPTIONS_TYPES}
        )
        options = to_camel_case(options)
        options = nest_fields(options, ["text", "highlights"], "contents")
        data = self.request("/findSimilar", options)
        return SearchResponse(
            [Result(**to_snake_case(result)) for result in data["results"]],
            data["autopromptString"] if "autopromptString" in data else None,
        )
