"""The LangSmith Client."""

from __future__ import annotations

import collections
import dataclasses
import datetime
import functools
import importlib
import io
import json
import logging
import os
import random
import socket
import sys
import threading
import time
import uuid
import weakref
from dataclasses import dataclass, field
from queue import Empty, PriorityQueue, Queue
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
)
from urllib import parse as urllib_parse

import requests
from requests import adapters as requests_adapters
from urllib3.util import Retry

import langsmith
from langsmith import env as ls_env
from langsmith import schemas as ls_schemas
from langsmith import utils as ls_utils
from langsmith.evaluation import evaluator as ls_evaluator

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)
# Filter the Connection pool is full warnings from urllib3
logging.getLogger("urllib3.connectionpool").addFilter(ls_utils.FilterPoolFullWarning())


def _is_localhost(url: str) -> bool:
    """Check if the URL is localhost.

    Parameters
    ----------
    url : str
        The URL to check.

    Returns
    -------
    bool
        True if the URL is localhost, False otherwise.
    """
    try:
        netloc = urllib_parse.urlsplit(url).netloc.split(":")[0]
        ip = socket.gethostbyname(netloc)
        return ip == "127.0.0.1" or ip.startswith("0.0.0.0") or ip.startswith("::")
    except socket.gaierror:
        return False


def _parse_token_or_url(url_or_token: str, api_url: str) -> Tuple[str, str]:
    """Parse a public dataset URL or share token."""
    try:
        uuid.UUID(url_or_token)
        return api_url, url_or_token
    except ValueError:
        pass

    # Then it's a URL
    parsed_url = urllib_parse.urlparse(url_or_token)
    # Extract the UUID from the path
    path_parts = parsed_url.path.split("/")
    if len(path_parts) >= 2:
        token_uuid = path_parts[-2]
    else:
        raise ls_utils.LangSmithUserError(f"Invalid public dataset URL: {url_or_token}")
    return api_url, token_uuid


def _is_langchain_hosted(url: str) -> bool:
    """Check if the URL is langchain hosted.

    Parameters
    ----------
    url : str
        The URL to check.

    Returns
    -------
    bool
        True if the URL is langchain hosted, False otherwise.
    """
    try:
        netloc = urllib_parse.urlsplit(url).netloc.split(":")[0]
        return netloc.endswith("langchain.com")
    except Exception:
        return False


ID_TYPE = Union[uuid.UUID, str]


def _default_retry_config() -> Retry:
    """Get the default retry configuration.

    If urllib3 version is 1.26 or greater, retry on all methods.

    Returns
    -------
    Retry
        The default retry configuration.
    """
    retry_params = dict(
        total=3,
        status_forcelist=[502, 503, 504, 408, 425, 429],
        backoff_factor=0.5,
        # Sadly urllib3 1.x doesn't support backoff_jitter
        raise_on_redirect=False,
        raise_on_status=False,
    )

    # the `allowed_methods` keyword is not available in urllib3 < 1.26

    # check to see if urllib3 version is 1.26 or greater
    urllib3_version = importlib.metadata.version("urllib3")
    use_allowed_methods = tuple(map(int, urllib3_version.split("."))) >= (1, 26)

    if use_allowed_methods:
        # Retry on all methods
        retry_params["allowed_methods"] = None

    return Retry(**retry_params)  # type: ignore


_PRIMITIVE_TYPES = (str, int, float, bool)
_MAX_DEPTH = 2


def _serialize_json(obj: Any, depth: int = 0) -> Any:
    try:
        if depth >= _MAX_DEPTH:
            try:
                return json.loads(json.dumps(obj))
            except BaseException:
                return repr(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if obj is None or isinstance(obj, _PRIMITIVE_TYPES):
            return obj
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        if isinstance(obj, (set, list, tuple)):
            return [_serialize_json(x, depth + 1) for x in list(obj)]
        if isinstance(obj, dict):
            return {k: _serialize_json(v, depth + 1) for k, v in obj.items()}

        serialization_methods = [
            ("model_dump_json", True),  # Pydantic V2
            ("json", True),  # Pydantic V1
            ("to_json", False),  # dataclass_json
        ]

        for attr, exclude_none in serialization_methods:
            if hasattr(obj, attr) and callable(getattr(obj, attr)):
                try:
                    method = getattr(obj, attr)
                    json_str = (
                        method(exclude_none=exclude_none) if exclude_none else method()
                    )
                    return json.loads(json_str)
                except Exception as e:
                    logger.debug(f"Failed to serialize {type(obj)} to JSON: {e}")
                    return repr(obj)

        if dataclasses.is_dataclass(obj):
            # Regular dataclass
            return dataclasses.asdict(obj)
        if hasattr(obj, "__slots__"):
            all_attrs = {slot: getattr(obj, slot, None) for slot in obj.__slots__}
        elif hasattr(obj, "__dict__"):
            all_attrs = vars(obj)
        else:
            return repr(obj)
        return {
            k: _serialize_json(v, depth=depth + 1) if v is not obj else repr(v)
            for k, v in all_attrs.items()
        }
    except BaseException as e:
        logger.debug(f"Failed to serialize {type(obj)} to JSON: {e}")
        return repr(obj)


def close_session(session: requests.Session) -> None:
    """Close the session.

    Parameters
    ----------
    session : Session
        The session to close.
    """
    logger.debug("Closing Client.session")
    session.close()


def _validate_api_key_if_hosted(api_url: str, api_key: Optional[str]) -> None:
    """Verify API key is provided if url not localhost.

    Parameters
    ----------
    api_url : str
        The API URL.
    api_key : str or None
        The API key.

    Raises
    ------
    LangSmithUserError
        If the API key is not provided when using the hosted service.
    """
    # If the domain is langchain.com, raise error if no api_key
    if not api_key:
        if _is_langchain_hosted(api_url):
            raise ls_utils.LangSmithUserError(
                "API key must be provided when using hosted LangSmith API"
            )


def _get_tracing_sampling_rate() -> float | None:
    """Get the tracing sampling rate.

    Returns
    -------
    float
        The tracing sampling rate.
    """
    sampling_rate_str = os.getenv("LANGCHAIN_TRACING_SAMPLING_RATE")
    if sampling_rate_str is None:
        return None
    sampling_rate = float(sampling_rate_str)
    if sampling_rate < 0 or sampling_rate > 1:
        raise ls_utils.LangSmithUserError(
            "LANGCHAIN_TRACING_SAMPLING_RATE must be between 0 and 1 if set."
            f" Got: {sampling_rate}"
        )
    return sampling_rate


def _get_api_key(api_key: Optional[str]) -> Optional[str]:
    api_key = api_key if api_key is not None else os.getenv("LANGCHAIN_API_KEY")
    if api_key is None or not api_key.strip():
        return None
    return api_key.strip().strip('"').strip("'")


def _get_api_url(api_url: Optional[str], api_key: Optional[str]) -> str:
    _api_url = (
        api_url
        if api_url is not None
        else os.getenv(
            "LANGCHAIN_ENDPOINT",
            "https://api.smith.langchain.com",
        )
    )
    if not _api_url.strip():
        raise ls_utils.LangSmithUserError("LangSmith API URL cannot be empty")
    return _api_url.strip().strip('"').strip("'").rstrip("/")


def _hide_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    if os.environ.get("LANGCHAIN_HIDE_INPUTS") == "true":
        return {}
    return inputs


def _hide_outputs(outputs: Dict[str, Any]) -> Dict[str, Any]:
    if os.environ.get("LANGCHAIN_HIDE_OUTPUTS") == "true":
        return {}
    return outputs


def _as_uuid(value: ID_TYPE, var: str) -> uuid.UUID:
    try:
        return uuid.UUID(value) if not isinstance(value, uuid.UUID) else value
    except ValueError as e:
        raise ls_utils.LangSmithUserError(
            f"{var} must be a valid UUID or UUID string. Got {value}"
        ) from e


@dataclass(order=True)
class TracingQueueItem:
    priority: str
    action: str
    item: Any = field(compare=False)


class Client:
    """Client for interacting with the LangSmith API."""

    __slots__ = [
        "__weakref__",
        "api_url",
        "api_key",
        "retry_config",
        "timeout_ms",
        "session",
        "_get_data_type_cached",
        "_web_url",
        "_tenant_id",
        "tracing_sample_rate",
        "_sampled_post_uuids",
        "tracing_queue",
    ]

    def __init__(
        self,
        api_url: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        retry_config: Optional[Retry] = None,
        timeout_ms: Optional[int] = None,
        web_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        auto_batch_tracing: bool = True,
    ) -> None:
        """Initialize a Client instance.

        Parameters
        ----------
        api_url : str or None, default=None
            URL for the LangSmith API. Defaults to the LANGCHAIN_ENDPOINT
            environment variable or https://api.smith.langchain.com if not set.
        api_key : str or None, default=None
            API key for the LangSmith API. Defaults to the LANGCHAIN_API_KEY
            environment variable.
        retry_config : Retry or None, default=None
            Retry configuration for the HTTPAdapter.
        timeout_ms : int or None, default=None
            Timeout in milliseconds for the HTTPAdapter.
        web_url : str or None, default=None
            URL for the LangSmith web app. Default is auto-inferred from
            the ENDPOINT.
        session: requests.Session or None, default=None
            The session to use for requests. If None, a new session will be
            created.

        Raises
        ------
        LangSmithUserError
            If the API key is not provided when using the hosted service.
        """
        self.tracing_sample_rate = _get_tracing_sampling_rate()
        self._sampled_post_uuids: set[uuid.UUID] = set()
        self.api_key = _get_api_key(api_key)
        self.api_url = _get_api_url(api_url, self.api_key)
        _validate_api_key_if_hosted(self.api_url, self.api_key)
        self.retry_config = retry_config or _default_retry_config()
        self.timeout_ms = timeout_ms or 10000
        self._web_url = web_url
        self._tenant_id: Optional[uuid.UUID] = None
        # Create a session and register a finalizer to close it
        self.session = session if session else requests.Session()
        weakref.finalize(self, close_session, self.session)
        # Initialize auto batching
        if auto_batch_tracing:
            self.tracing_queue: Optional[PriorityQueue] = PriorityQueue()

            threading.Thread(
                target=_tracing_control_thread_func,
                # arg must be a weakref to self to avoid the Thread object
                # preventing garbage collection of the Client object
                args=(weakref.ref(self),),
            ).start()
        else:
            self.tracing_queue = None

        # Mount the HTTPAdapter with the retry configuration
        adapter = requests_adapters.HTTPAdapter(max_retries=self.retry_config)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self._get_data_type_cached = functools.lru_cache(maxsize=10)(
            self._get_data_type
        )

    def _repr_html_(self) -> str:
        """Return an HTML representation of the instance with a link to the URL.

        Returns
        -------
        str
            The HTML representation of the instance.
        """
        link = self._host_url
        return f'<a href="{link}", target="_blank" rel="noopener">LangSmith Client</a>'

    def __repr__(self) -> str:
        """Return a string representation of the instance with a link to the URL.

        Returns
        -------
        str
            The string representation of the instance.
        """
        return f"Client (API URL: {self.api_url})"

    @property
    def _host_url(self) -> str:
        """The web host url."""
        if self._web_url:
            link = self._web_url
        else:
            parsed_url = urllib_parse.urlparse(self.api_url)
            if _is_localhost(self.api_url):
                link = "http://localhost"
            elif parsed_url.path.endswith("/api"):
                new_path = parsed_url.path.rsplit("/api", 1)[0]
                link = urllib_parse.urlunparse(parsed_url._replace(path=new_path))
            elif parsed_url.netloc.startswith("dev."):
                link = "https://dev.smith.langchain.com"
            else:
                link = "https://smith.langchain.com"
        return link

    @property
    def _headers(self) -> Dict[str, str]:
        """Get the headers for the API request.

        Returns
        -------
        Dict[str, str]
            The headers for the API request.
        """
        headers = {"User-Agent": f"langsmith-py/{langsmith.__version__}"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    @property
    def info(self) -> Optional[ls_schemas.LangSmithInfo]:
        """Get the information about the LangSmith API.

        Returns
        -------
        Optional[ls_schemas.LangSmithInfo]
            The information about the LangSmith API, or None if the API is
                not available.
        """
        info = Client._get_info(self.session, self.api_url, self.timeout_ms)
        if info is None and self.tracing_queue is not None:
            self.tracing_queue = None
        return cast(Optional[ls_schemas.LangSmithInfo], info)

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def _get_info(
        session: requests.Session, api_url: str, timeout_ms: int
    ) -> Optional[ls_schemas.LangSmithInfo]:
        try:
            response = session.get(
                api_url + "/info",
                headers={"Accept": "application/json"},
                timeout=timeout_ms / 1000,
            )
            ls_utils.raise_for_status_with_text(response)
            return ls_schemas.LangSmithInfo(**response.json())
        except requests.HTTPError:
            return None
        except BaseException as e:
            logger.warning(f"Failed to get info from {api_url}: {repr(e)}")
            return None

    def request_with_retries(
        self,
        request_method: str,
        url: str,
        request_kwargs: Mapping,
        stop_after_attempt: int = 1,
        retry_on: Optional[Sequence[Type[BaseException]]] = None,
        to_ignore: Optional[Sequence[Type[BaseException]]] = None,
    ) -> requests.Response:
        """Send a request with retries.

        Parameters
        ----------
        request_method : str
            The HTTP request method.
        url : str
            The URL to send the request to.
        request_kwargs : Mapping
            Additional request parameters.
        stop_after_attempt : int, default=1
            The number of attempts to make.
        retry_on : Sequence[Type[BaseException]] or None, default=None
            The exceptions to retry on. In addition to:
            [LangSmithConnectionError, LangSmithAPIError].
        to_ignore : Sequence[Type[BaseException]] or None, default=None
            The exceptions to ignore / pass on.

        Returns
        -------
        Response
            The response object.

        Raises
        ------
        LangSmithAPIError
            If a server error occurs.
        LangSmithUserError
            If the request fails.
        LangSmithConnectionError
            If a connection error occurs.
        LangSmithError
            If the request fails.
        """

        retry_on_: Tuple[Type[BaseException], ...] = (
            *(retry_on or []),
            *(ls_utils.LangSmithConnectionError, ls_utils.LangSmithAPIError),
        )
        to_ignore_: Tuple[Type[BaseException], ...] = (*(to_ignore or ()),)
        response = None
        for idx in range(stop_after_attempt):
            try:
                try:
                    response = self.session.request(
                        request_method, url, stream=False, **request_kwargs
                    )
                    ls_utils.raise_for_status_with_text(response)
                    return response
                except requests.HTTPError as e:
                    if response is not None:
                        if response.status_code == 500:
                            raise ls_utils.LangSmithAPIError(
                                f"Server error caused failure to {request_method}"
                                f" {url} in"
                                f" LangSmith API. {repr(e)}"
                            )
                        elif response.status_code == 429:
                            raise ls_utils.LangSmithRateLimitError(
                                f"Rate limit exceeded for {url}. {repr(e)}"
                            )
                        elif response.status_code == 401:
                            raise ls_utils.LangSmithAuthError(
                                f"Authentication failed for {url}. {repr(e)}"
                            )
                        elif response.status_code == 404:
                            raise ls_utils.LangSmithNotFoundError(
                                f"Resource not found for {url}. {repr(e)}"
                            )
                        elif response.status_code == 409:
                            raise ls_utils.LangSmithConflictError(
                                f"Conflict for {url}. {repr(e)}"
                            )
                        else:
                            raise ls_utils.LangSmithError(
                                f"Failed to {request_method} {url} in LangSmith"
                                f" API. {repr(e)}"
                            )

                    else:
                        raise ls_utils.LangSmithUserError(
                            f"Failed to {request_method} {url} in LangSmith API."
                            f" {repr(e)}"
                        )
                except requests.ConnectionError as e:
                    raise ls_utils.LangSmithConnectionError(
                        f"Connection error caused failure to {request_method} {url}"
                        "  in LangSmith API. Please confirm your LANGCHAIN_ENDPOINT."
                        f" {repr(e)}"
                    ) from e
                except Exception as e:
                    args = list(e.args)
                    msg = args[1] if len(args) > 1 else ""
                    msg = msg.replace("session", "session (project)")
                    emsg = "\n".join([args[0]] + [msg] + args[2:])
                    raise ls_utils.LangSmithError(
                        f"Failed to {request_method} {url} in LangSmith API. {emsg}"
                    ) from e
            except to_ignore_ as e:
                if response is not None:
                    logger.debug("Passing on exception %s", e)
                    return response
                # Else we still raise an error
            except retry_on_:
                if idx + 1 == stop_after_attempt:
                    raise
                sleep_time = 2**idx + (random.random() * 0.5)
                time.sleep(sleep_time)
                continue

        raise ls_utils.LangSmithError(
            f"Failed to {request_method} {url} in LangSmith API."
        )

    def _get_with_retries(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        return self.request_with_retries(
            "get",
            f"{self.api_url}{path}",
            request_kwargs={
                "params": params,
                "headers": self._headers,
                "timeout": self.timeout_ms / 1000,
            },
        )

    def _get_paginated_list(
        self, path: str, *, params: Optional[dict] = None
    ) -> Iterator[dict]:
        """Get a paginated list of items.

        Parameters
        ----------
        path : str
            The path of the request URL.
        params : dict or None, default=None
            The query parameters.

        Yields
        ------
        dict
            The items in the paginated list.
        """
        params_ = params.copy() if params else {}
        offset = params_.get("offset", 0)
        params_["limit"] = params_.get("limit", 100)
        while True:
            params_["offset"] = offset
            response = self._get_with_retries(path, params=params_)
            items = response.json()

            if not items:
                break
            yield from items
            if len(items) < params_["limit"]:
                # offset and limit isn't respected if we're
                # querying for specific values
                break
            offset += len(items)

    def _get_cursor_paginated_list(
        self,
        path: str,
        *,
        body: Optional[dict] = None,
        request_method: str = "post",
        data_key: str = "runs",
    ) -> Iterator[dict]:
        """Get a cursor paginated list of items.

        Parameters
        ----------
        path : str
            The path of the request URL.
        body : dict or None, default=None
            The query body.
        request_method : str, default="post"
            The HTTP request method.
        data_key : str, default="runs"

        Yields
        ------
        dict
            The items in the paginated list.
        """
        params_ = body.copy() if body else {}
        while True:
            response = self.request_with_retries(
                request_method,
                f"{self.api_url}{path}",
                request_kwargs={
                    "data": json.dumps(params_, default=_serialize_json),
                    "headers": self._headers,
                    "timeout": self.timeout_ms / 1000,
                },
            )
            response_body = response.json()
            if not response_body:
                break
            if not response_body.get(data_key):
                break
            yield from response_body[data_key]
            cursors = response_body.get("cursors")
            if not cursors:
                break
            if not cursors.get("next"):
                break
            params_["cursor"] = cursors["next"]

    def upload_dataframe(
        self,
        df: pd.DataFrame,
        name: str,
        input_keys: Sequence[str],
        output_keys: Sequence[str],
        *,
        description: Optional[str] = None,
        data_type: Optional[ls_schemas.DataType] = ls_schemas.DataType.kv,
    ) -> ls_schemas.Dataset:
        """Upload a dataframe as individual examples to the LangSmith API.

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to upload.
        name : str
            The name of the dataset.
        input_keys : Sequence[str]
            The input keys.
        output_keys : Sequence[str]
            The output keys.
        description : str or None, default=None
            The description of the dataset.
        data_type : DataType or None, default=DataType.kv
            The data type of the dataset.

        Returns
        -------
        Dataset
            The uploaded dataset.

        Raises
        ------
        ValueError
            If the csv_file is not a string or tuple.
        """
        csv_file = io.BytesIO()
        df.to_csv(csv_file, index=False)
        csv_file.seek(0)
        return self.upload_csv(
            ("data.csv", csv_file),
            input_keys=input_keys,
            output_keys=output_keys,
            description=description,
            name=name,
            data_type=data_type,
        )

    def upload_csv(
        self,
        csv_file: Union[str, Tuple[str, io.BytesIO]],
        input_keys: Sequence[str],
        output_keys: Sequence[str],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        data_type: Optional[ls_schemas.DataType] = ls_schemas.DataType.kv,
    ) -> ls_schemas.Dataset:
        """Upload a CSV file to the LangSmith API.

        Parameters
        ----------
        csv_file : str or Tuple[str, BytesIO]
            The CSV file to upload. If a string, it should be the path
            If a tuple, it should be a tuple containing the filename
            and a BytesIO object.
        input_keys : Sequence[str]
            The input keys.
        output_keys : Sequence[str]
            The output keys.
        name : str or None, default=None
            The name of the dataset.
        description : str or None, default=None
            The description of the dataset.
        data_type : DataType or None, default=DataType.kv
            The data type of the dataset.

        Returns
        -------
        Dataset
            The uploaded dataset.

        Raises
        ------
        ValueError
            If the csv_file is not a string or tuple.
        """
        data = {
            "input_keys": input_keys,
            "output_keys": output_keys,
        }
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if data_type:
            data["data_type"] = ls_utils.get_enum_value(data_type)
        if isinstance(csv_file, str):
            with open(csv_file, "rb") as f:
                file_ = {"file": f}
                response = self.session.post(
                    self.api_url + "/datasets/upload",
                    headers=self._headers,
                    data=data,
                    files=file_,
                )
        elif isinstance(csv_file, tuple):
            response = self.session.post(
                self.api_url + "/datasets/upload",
                headers=self._headers,
                data=data,
                files={"file": csv_file},
            )
        else:
            raise ValueError("csv_file must be a string or tuple")
        ls_utils.raise_for_status_with_text(response)
        result = response.json()
        # TODO: Make this more robust server-side
        if "detail" in result and "already exists" in result["detail"]:
            file_name = csv_file if isinstance(csv_file, str) else csv_file[0]
            file_name = file_name.split("/")[-1]
            raise ValueError(f"Dataset {file_name} already exists")
        return ls_schemas.Dataset(
            **result, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
        )

    @staticmethod
    def _run_transform(
        run: Union[ls_schemas.Run, dict, ls_schemas.RunLikeDict],
    ) -> dict:
        """
        Transforms the given run object into a dictionary representation.

        Args:
            run (Union[ls_schemas.Run, dict]): The run object to transform.

        Returns:
            dict: The transformed run object as a dictionary.
        """
        if hasattr(run, "dict") and callable(getattr(run, "dict")):
            run_create = run.dict()  # type: ignore
        else:
            run_create = cast(dict, run)
        if "id" not in run_create:
            run_create["id"] = uuid.uuid4()
        elif isinstance(run["id"], str):
            run["id"] = uuid.UUID(run["id"])
        if "inputs" in run_create:
            run_create["inputs"] = _hide_inputs(run_create["inputs"])
        if "outputs" in run_create:
            run_create["outputs"] = _hide_outputs(run_create["outputs"])
        if not run_create.get("start_time"):
            run_create["start_time"] = datetime.datetime.utcnow()
        return run_create

    @staticmethod
    def _insert_runtime_env(runs: Sequence[dict]) -> None:
        runtime_env = ls_env.get_runtime_and_metrics()
        for run_create in runs:
            run_extra = cast(dict, run_create.setdefault("extra", {}))
            # update runtime
            runtime: dict = run_extra.setdefault("runtime", {})
            run_extra["runtime"] = {**runtime_env, **runtime}
            # update metadata
            metadata: dict = run_extra.setdefault("metadata", {})
            langchain_metadata = ls_env.get_langchain_env_var_metadata()
            metadata.update(
                {k: v for k, v in langchain_metadata.items() if k not in metadata}
            )

    def _filter_for_sampling(
        self, runs: Iterable[dict], *, patch: bool = False
    ) -> list[dict]:
        if self.tracing_sample_rate is None:
            return list(runs)

        if patch:
            sampled = []
            for run in runs:
                if run["id"] in self._sampled_post_uuids:
                    sampled.append(run)
                    self._sampled_post_uuids.remove(run["id"])
            return sampled
        else:
            sampled = []
            for run in runs:
                if random.random() < self.tracing_sample_rate:
                    sampled.append(run)
                    self._sampled_post_uuids.add(run["id"])
            return sampled

    def create_run(
        self,
        name: str,
        inputs: Dict[str, Any],
        run_type: str,
        *,
        project_name: Optional[str] = None,
        revision_id: Optional[ID_TYPE] = None,
        **kwargs: Any,
    ) -> None:
        """Persist a run to the LangSmith API.

        Parameters
        ----------
        name : str
            The name of the run.
        inputs : Dict[str, Any]
            The input values for the run.
        run_type : str
            The type of the run, such as tool, chain, llm, retriever,
            embedding, prompt, or parser.
        revision_id : ID_TYPE or None, default=None
            The revision ID of the run.
        **kwargs : Any
            Additional keyword arguments.

        Raises
        ------
        LangSmithUserError
            If the API key is not provided when using the hosted service.
        """
        project_name = project_name or kwargs.pop(
            "session_name",
            # if the project is not provided, use the environment's project
            ls_utils.get_tracer_project(),
        )
        run_create = {
            **kwargs,
            "session_name": project_name,
            "name": name,
            "inputs": inputs,
            "run_type": run_type,
        }
        if not self._filter_for_sampling([run_create]):
            return

        run_create = self._run_transform(run_create)
        self._insert_runtime_env([run_create])

        if revision_id is not None:
            run_create["extra"]["metadata"]["revision_id"] = revision_id
        if (
            self.tracing_queue is not None
            # batch ingest requires trace_id and dotted_order to be set
            and run_create.get("trace_id") is not None
            and run_create.get("dotted_order") is not None
            # Checked last since it makes a (cached) API call
            and self.info is not None  # Older versions don't support batch ingest
        ):
            return self.tracing_queue.put(
                TracingQueueItem(run_create["dotted_order"], "create", run_create)
            )

        headers = {
            **self._headers,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        self.request_with_retries(
            "post",
            f"{self.api_url}/runs",
            request_kwargs={
                "data": json.dumps(run_create, default=_serialize_json),
                "headers": headers,
                "timeout": self.timeout_ms / 1000,
            },
            to_ignore=(ls_utils.LangSmithConflictError,),
        )

    def batch_ingest_runs(
        self,
        create: Optional[
            Sequence[Union[ls_schemas.Run, ls_schemas.RunLikeDict, Dict]]
        ] = None,
        update: Optional[
            Sequence[Union[ls_schemas.Run, ls_schemas.RunLikeDict, Dict]]
        ] = None,
        *,
        pre_sampled: bool = False,
    ):
        """
        Batch ingest/upsert multiple runs in the Langsmith system.

        Args:
            create (Optional[Sequence[Union[ls_schemas.Run, RunLikeDict]]]):
                A sequence of `Run` objects or equivalent dictionaries representing
                runs to be created / posted.
            update (Optional[Sequence[Union[ls_schemas.Run, RunLikeDict]]]):
                A sequence of `Run` objects or equivalent dictionaries representing
                runs that have already been created and should be updated / patched.
            pre_sampled (bool, optional): Whether the runs have already been subject
                to sampling, and therefore should not be sampled again.
                Defaults to False.

        Returns:
            None: If both `create` and `update` are None.

        Raises:
            LangsmithAPIError: If there is an error in the API request.

        Note:
            - The run objects MUST contain the dotted_order and trace_id fields
                to be accepted by the API.
        """

        if not create and not update:
            return
        # transform and convert to dicts
        create_dicts = [self._run_transform(run) for run in create or []]
        update_dicts = [self._run_transform(run) for run in update or []]
        # combine post and patch dicts where possible
        if update_dicts and create_dicts:
            create_by_id = {run["id"]: run for run in create_dicts}
            standalone_updates: list[dict] = []
            for run in update_dicts:
                if run["id"] in create_by_id:
                    create_by_id[run["id"]].update(
                        {k: v for k, v in run.items() if v is not None}
                    )
                else:
                    standalone_updates.append(run)
            update_dicts = standalone_updates
        for run in create_dicts:
            if not run.get("trace_id") or not run.get("dotted_order"):
                raise ls_utils.LangSmithUserError(
                    "Batch ingest requires trace_id and dotted_order to be set."
                )
        for run in update_dicts:
            if not run.get("trace_id") or not run.get("dotted_order"):
                raise ls_utils.LangSmithUserError(
                    "Batch ingest requires trace_id and dotted_order to be set."
                )
        # filter out runs that are not sampled
        if pre_sampled:
            body = {
                "post": create_dicts,
                "patch": update_dicts,
            }
        else:
            body = {
                "post": self._filter_for_sampling(create_dicts),
                "patch": self._filter_for_sampling(update_dicts, patch=True),
            }
        if not body["post"] and not body["patch"]:
            return

        self._insert_runtime_env(body["post"])

        self.request_with_retries(
            "post",
            f"{self.api_url}/runs/batch",
            request_kwargs={
                "data": json.dumps(body, default=_serialize_json),
                "timeout": self.timeout_ms / 1000,
                "headers": {
                    **self._headers,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            },
            to_ignore=(ls_utils.LangSmithConflictError,),
        )

    def update_run(
        self,
        run_id: ID_TYPE,
        *,
        end_time: Optional[datetime.datetime] = None,
        error: Optional[str] = None,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        events: Optional[Sequence[dict]] = None,
        **kwargs: Any,
    ) -> None:
        """Update a run in the LangSmith API.

        Parameters
        ----------
        run_id : str or UUID
            The ID of the run to update.
        end_time : datetime or None
            The end time of the run.
        error : str or None, default=None
            The error message of the run.
        inputs : Dict or None, default=None
            The input values for the run.
        outputs : Dict or None, default=None
            The output values for the run.
        events : Sequence[dict] or None, default=None
            The events for the run.
        **kwargs : Any
            Kwargs are ignored.
        """
        headers = {
            **self._headers,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data: Dict[str, Any] = {
            "id": _as_uuid(run_id, "run_id"),
            "trace_id": kwargs.pop("trace_id", None),
            "parent_run_id": kwargs.pop("parent_run_id", None),
            "dotted_order": kwargs.pop("dotted_order", None),
        }
        if not self._filter_for_sampling([data], patch=True):
            return
        if end_time is not None:
            data["end_time"] = end_time.isoformat()
        if error is not None:
            data["error"] = error
        if inputs is not None:
            data["inputs"] = _hide_inputs(inputs)
        if outputs is not None:
            data["outputs"] = _hide_outputs(outputs)
        if events is not None:
            data["events"] = events
        if (
            self.tracing_queue is not None
            # batch ingest requires trace_id and dotted_order to be set
            and data["trace_id"] is not None
            and data["dotted_order"] is not None
            # Checked last since it makes an API call
            and self.info is not None  # Older versions don't support batch ingest
        ):
            return self.tracing_queue.put(
                TracingQueueItem(data["dotted_order"], "update", data)
            )

        self.request_with_retries(
            "patch",
            f"{self.api_url}/runs/{data['id']}",
            request_kwargs={
                "data": json.dumps(data, default=_serialize_json),
                "headers": headers,
                "timeout": self.timeout_ms / 1000,
            },
        )

    def _load_child_runs(self, run: ls_schemas.Run) -> ls_schemas.Run:
        """Load child runs for a given run.

        Parameters
        ----------
        run : Run
            The run to load child runs for.

        Returns
        -------
        Run
            The run with loaded child runs.

        Raises
        ------
        LangSmithError
            If a child run has no parent.
        """
        child_runs = self.list_runs(id=run.child_run_ids)
        treemap: DefaultDict[uuid.UUID, List[ls_schemas.Run]] = collections.defaultdict(
            list
        )
        runs: Dict[uuid.UUID, ls_schemas.Run] = {}
        for child_run in sorted(
            child_runs,
            key=lambda r: r.dotted_order,
        ):
            if child_run.parent_run_id is None:
                raise ls_utils.LangSmithError(f"Child run {child_run.id} has no parent")
            treemap[child_run.parent_run_id].append(child_run)
            runs[child_run.id] = child_run
        run.child_runs = treemap.pop(run.id, [])
        for run_id, children in treemap.items():
            runs[run_id].child_runs = children
        return run

    def read_run(
        self, run_id: ID_TYPE, load_child_runs: bool = False
    ) -> ls_schemas.Run:
        """Read a run from the LangSmith API.

        Parameters
        ----------
        run_id : str or UUID
            The ID of the run to read.
        load_child_runs : bool, default=False
            Whether to load nested child runs.

        Returns
        -------
        Run
            The run.
        """
        response = self._get_with_retries(f"/runs/{_as_uuid(run_id, 'run_id')}")
        run = ls_schemas.Run(**response.json(), _host_url=self._host_url)
        if load_child_runs and run.child_run_ids:
            run = self._load_child_runs(run)
        return run

    def list_runs(
        self,
        *,
        project_id: Optional[ID_TYPE] = None,
        project_name: Optional[str] = None,
        run_type: Optional[str] = None,
        reference_example_id: Optional[ID_TYPE] = None,
        query: Optional[str] = None,
        filter: Optional[str] = None,
        execution_order: Optional[int] = None,
        parent_run_id: Optional[ID_TYPE] = None,
        start_time: Optional[datetime.datetime] = None,
        error: Optional[bool] = None,
        run_ids: Optional[List[ID_TYPE]] = None,
        **kwargs: Any,
    ) -> Iterator[ls_schemas.Run]:
        """List runs from the LangSmith API.

        Parameters
        ----------
        project_id : UUID or None, default=None
            The ID of the project to filter by.
        project_name : str or None, default=None
            The name of the project to filter by.
        run_type : str or None, default=None
            The type of the runs to filter by.
        reference_example_id : UUID or None, default=None
            The ID of the reference example to filter by.
        query : str or None, default=None
            The query string to filter by.
        filter : str or None, default=None
            The filter string to filter by.
        execution_order : int or None, default=None
            The execution order to filter by. Execution order is the position
            of the run in the full trace's execution sequence.
                All root run traces have execution_order 1.
        parent_run_id : UUID or None, default=None
            The ID of the parent run to filter by.
        start_time : datetime or None, default=None
            The start time to filter by.
        error : bool or None, default=None
            Whether to filter by error status.
        run_ids : List[str or UUID] or None, default=None
            The IDs of the runs to filter by.
        **kwargs : Any
            Additional keyword arguments.

        Yields
        ------
        Run
            The runs.
        """
        if project_name is not None:
            if project_id is not None:
                raise ValueError("Only one of project_id or project_name may be given")
            project_id = self.read_project(project_name=project_name).id
        body_query: Dict[str, Any] = {
            "session": [project_id] if project_id else None,
            "run_type": run_type,
            "reference_example": (
                [reference_example_id] if reference_example_id else None
            ),
            "query": query,
            "filter": filter,
            "execution_order": execution_order,
            "parent_run": parent_run_id,
            "start_time": start_time.isoformat() if start_time else None,
            "error": error,
            "id": run_ids,
            **kwargs,
        }
        body_query = {k: v for k, v in body_query.items() if v is not None}
        yield from (
            ls_schemas.Run(**run, _host_url=self._host_url)
            for run in self._get_cursor_paginated_list(
                "/runs/query", body=body_query, request_method="post"
            )
        )

    def get_run_url(
        self,
        *,
        run: ls_schemas.RunBase,
        project_name: Optional[str] = None,
        project_id: Optional[ID_TYPE] = None,
    ) -> str:
        """Get the URL for a run.

        Parameters
        ----------
        run : Run
            The run.
        project_name : str or None, default=None
            The name of the project.
        project_id : UUID or None, default=None
            The ID of the project.

        Returns
        -------
        str
            The URL for the run.
        """
        if hasattr(run, "session_id") and run.session_id is not None:
            session_id = run.session_id
        elif project_id is not None:
            session_id = project_id
        elif project_name is not None:
            session_id = self.read_project(project_name=project_name).id
        else:
            project_name = ls_utils.get_tracer_project()
            session_id = self.read_project(project_name=project_name).id
        session_id_ = _as_uuid(session_id, "session_id")
        return (
            f"{self._host_url}/o/{self._get_tenant_id()}/projects/p/{session_id_}/"
            f"r/{run.id}?poll=true"
        )

    def share_run(self, run_id: ID_TYPE, *, share_id: Optional[ID_TYPE] = None) -> str:
        """Get a share link for a run."""
        run_id_ = _as_uuid(run_id, "run_id")
        data = {
            "run_id": str(run_id_),
            "share_token": share_id or str(uuid.uuid4()),
        }
        response = self.session.put(
            f"{self.api_url}/runs/{run_id_}/share",
            headers=self._headers,
            json=data,
        )
        ls_utils.raise_for_status_with_text(response)
        share_token = response.json()["share_token"]
        return f"{self._host_url}/public/{share_token}/r"

    def unshare_run(self, run_id: ID_TYPE) -> None:
        """Delete share link for a run."""
        response = self.session.delete(
            f"{self.api_url}/runs/{_as_uuid(run_id, 'run_id')}/share",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def read_run_shared_link(self, run_id: ID_TYPE) -> Optional[str]:
        response = self.session.get(
            f"{self.api_url}/runs/{_as_uuid(run_id, 'run_id')}/share",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)
        result = response.json()
        if result is None or "share_token" not in result:
            return None
        return f"{self._host_url}/public/{result['share_token']}/r"

    def run_is_shared(self, run_id: ID_TYPE) -> bool:
        """Get share state for a run."""
        link = self.read_run_shared_link(_as_uuid(run_id, "run_id"))
        return link is not None

    def list_shared_runs(
        self, share_token: ID_TYPE, run_ids: Optional[List[str]] = None
    ) -> List[ls_schemas.Run]:
        """Get shared runs."""
        params = {"id": run_ids, "share_token": str(share_token)}
        response = self.session.get(
            f"{self.api_url}/public/{_as_uuid(share_token, 'share_token')}/runs",
            headers=self._headers,
            params=params,
        )
        ls_utils.raise_for_status_with_text(response)
        return [
            ls_schemas.Run(**run, _host_url=self._host_url) for run in response.json()
        ]

    def read_dataset_shared_schema(
        self,
        dataset_id: Optional[ID_TYPE] = None,
        *,
        dataset_name: Optional[str] = None,
    ) -> ls_schemas.DatasetShareSchema:
        if dataset_id is None and dataset_name is None:
            raise ValueError("Either dataset_id or dataset_name must be given")
        if dataset_id is None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
        response = self.session.get(
            f"{self.api_url}/datasets/{_as_uuid(dataset_id, 'dataset_id')}/share",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)
        d = response.json()
        return cast(
            ls_schemas.DatasetShareSchema,
            {
                **d,
                "url": f"{self._host_url}/public/"
                f"{_as_uuid(d['share_token'], 'response.share_token')}/d",
            },
        )

    def share_dataset(
        self,
        dataset_id: Optional[ID_TYPE] = None,
        *,
        dataset_name: Optional[str] = None,
    ) -> ls_schemas.DatasetShareSchema:
        """Get a share link for a dataset."""
        if dataset_id is None and dataset_name is None:
            raise ValueError("Either dataset_id or dataset_name must be given")
        if dataset_id is None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
        data = {
            "dataset_id": str(dataset_id),
        }
        response = self.session.put(
            f"{self.api_url}/datasets/{_as_uuid(dataset_id, 'dataset_id')}/share",
            headers=self._headers,
            json=data,
        )
        ls_utils.raise_for_status_with_text(response)
        d: dict = response.json()
        return cast(
            ls_schemas.DatasetShareSchema,
            {**d, "url": f"{self._host_url}/public/{d['share_token']}/d"},
        )

    def unshare_dataset(self, dataset_id: ID_TYPE) -> None:
        """Delete share link for a dataset."""
        response = self.session.delete(
            f"{self.api_url}/datasets/{_as_uuid(dataset_id, 'dataset_id')}/share",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def read_shared_dataset(
        self,
        share_token: str,
    ) -> ls_schemas.Dataset:
        """Get shared datasets."""
        response = self.session.get(
            f"{self.api_url}/public/{_as_uuid(share_token, 'share_token')}/datasets",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)
        return ls_schemas.Dataset(
            **response.json(),
            _host_url=self._host_url,
            _public_path=f"/public/{share_token}/d",
        )

    def list_shared_examples(
        self, share_token: str, *, example_ids: Optional[List[ID_TYPE]] = None
    ) -> List[ls_schemas.Example]:
        """Get shared examples."""
        params = {}
        if example_ids is not None:
            params["id"] = [str(id) for id in example_ids]
        response = self.session.get(
            f"{self.api_url}/public/{_as_uuid(share_token, 'share_token')}/examples",
            headers=self._headers,
            params=params,
        )
        ls_utils.raise_for_status_with_text(response)
        return [
            ls_schemas.Example(**dataset, _host_url=self._host_url)
            for dataset in response.json()
        ]

    def list_shared_projects(
        self,
        *,
        dataset_share_token: str,
        project_ids: Optional[List[ID_TYPE]] = None,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> Iterator[ls_schemas.TracerSessionResult]:
        params = {"id": project_ids, "name": name, "name_contains": name_contains}
        share_token = _as_uuid(dataset_share_token, "dataset_share_token")
        yield from [
            ls_schemas.TracerSessionResult(**project, _host_url=self._host_url)
            for project in self._get_paginated_list(
                f"/public/{share_token}/datasets/sessions",
                params=params,
            )
        ]

    def create_project(
        self,
        project_name: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        upsert: bool = False,
        project_extra: Optional[dict] = None,
        reference_dataset_id: Optional[ID_TYPE] = None,
    ) -> ls_schemas.TracerSession:
        """Create a project on the LangSmith API.

        Parameters
        ----------
        project_name : str
            The name of the project.
        project_extra : dict or None, default=None
            Additional project information.
        metadata: dict or None, default=None
            Additional metadata to associate with the project.
        description : str or None, default=None
            The description of the project.
        upsert : bool, default=False
            Whether to update the project if it already exists.
        reference_dataset_id: UUID or None, default=None
            The ID of the reference dataset to associate with the project.

        Returns
        -------
        TracerSession
            The created project.
        """
        endpoint = f"{self.api_url}/sessions"
        extra = project_extra
        if metadata:
            extra = {**(extra or {}), "metadata": metadata}
        body: Dict[str, Any] = {
            "name": project_name,
            "extra": extra,
            "description": description,
        }
        params = {}
        if upsert:
            params["upsert"] = True
        if reference_dataset_id is not None:
            body["reference_dataset_id"] = reference_dataset_id
        response = self.session.post(
            endpoint,
            headers={**self._headers, "Content-Type": "application/json"},
            data=json.dumps(body, default=_serialize_json),
        )
        ls_utils.raise_for_status_with_text(response)
        return ls_schemas.TracerSession(**response.json(), _host_url=self._host_url)

    def update_project(
        self,
        project_id: ID_TYPE,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
        project_extra: Optional[dict] = None,
        end_time: Optional[datetime.datetime] = None,
    ) -> ls_schemas.TracerSession:
        """Update a LangSmith project.

        Parameters
        ----------
        project_id : UUID
            The ID of the project to update.
        name : str or None, default=None
            The new name to give the project. This is only valid if the project
            has been assigned an end_time, meaning it has been completed/closed.
        description : str or None, default=None
            The new description to give the project.
        metadata: dict or None, default=None

        project_extra : dict or None, default=None
            Additional project information.

        Returns
        -------
        TracerSession
            The updated project.
        """
        endpoint = f"{self.api_url}/sessions/{_as_uuid(project_id, 'project_id')}"
        extra = project_extra
        if metadata:
            extra = {**(extra or {}), "metadata": metadata}
        body: Dict[str, Any] = {
            "name": name,
            "extra": extra,
            "description": description,
            "end_time": end_time.isoformat() if end_time else None,
        }
        response = self.session.patch(
            endpoint,
            headers={**self._headers, "Content-Type": "application/json"},
            data=json.dumps(body, default=_serialize_json),
        )
        ls_utils.raise_for_status_with_text(response)
        return ls_schemas.TracerSession(**response.json(), _host_url=self._host_url)

    def _get_tenant_id(self) -> uuid.UUID:
        if self._tenant_id is not None:
            return self._tenant_id
        response = self._get_with_retries("/sessions", params={"limit": 1})
        result = response.json()
        if isinstance(result, list):
            tracer_session = ls_schemas.TracerSessionResult(
                **result[0], _host_url=self._host_url
            )
            self._tenant_id = tracer_session.tenant_id
            return self._tenant_id
        raise ls_utils.LangSmithError("No projects found")

    @ls_utils.xor_args(("project_id", "project_name"))
    def read_project(
        self,
        *,
        project_id: Optional[str] = None,
        project_name: Optional[str] = None,
        include_stats: bool = False,
    ) -> ls_schemas.TracerSessionResult:
        """Read a project from the LangSmith API.

        Parameters
        ----------
        project_id : str or None, default=None
            The ID of the project to read.
        project_name : str or None, default=None
            The name of the project to read.
                Note: Only one of project_id or project_name may be given.
        include_stats : bool, default=False
            Whether to include a project's aggregate statistics in the response.

        Returns
        -------
        TracerSessionResult
            The project.
        """
        path = "/sessions"
        params: Dict[str, Any] = {"limit": 1}
        if project_id is not None:
            path += f"/{_as_uuid(project_id, 'project_id')}"
        elif project_name is not None:
            params["name"] = project_name
        else:
            raise ValueError("Must provide project_name or project_id")
        params["include_stats"] = include_stats
        response = self._get_with_retries(path, params=params)
        result = response.json()
        if isinstance(result, list):
            if len(result) == 0:
                raise ls_utils.LangSmithNotFoundError(
                    f"Project {project_name} not found"
                )
            return ls_schemas.TracerSessionResult(**result[0], _host_url=self._host_url)
        return ls_schemas.TracerSessionResult(
            **response.json(), _host_url=self._host_url
        )

    def has_project(
        self, project_name: str, *, project_id: Optional[str] = None
    ) -> bool:
        """Check if a project exists.

        Parameters
        ----------
        project_name : str
            The name of the project to check for.
        project_id : str or None, default=None
            The ID of the project to check for.

        Returns
        -------
        bool
            Whether the project exists.
        """
        try:
            self.read_project(project_name=project_name)
        except ls_utils.LangSmithNotFoundError:
            return False
        return True

    def get_test_results(
        self,
        *,
        project_id: Optional[ID_TYPE] = None,
        project_name: Optional[str] = None,
    ) -> "pd.DataFrame":
        """Read the record-level information from a test project into a Pandas DF.

        Note: this will fetch whatever data exists in the DB. Results are not
        immediately available in the DB upon evaluation run completion.

        Returns
        -------
        pd.DataFrame
            A dataframe containing the test results.
        """
        import pandas as pd  # type: ignore

        runs = self.list_runs(
            project_id=project_id, project_name=project_name, execution_order=1
        )
        results = []
        example_ids = []
        for r in runs:
            row = {
                "example_id": r.reference_example_id,
                **{f"input.{k}": v for k, v in r.inputs.items()},
                **{f"outputs.{k}": v for k, v in (r.outputs or {}).items()},
            }
            if r.feedback_stats:
                for k, v in r.feedback_stats.items():
                    row[f"feedback.{k}"] = v.get("avg")
            row.update(
                {
                    "execution_time": (
                        (r.end_time - r.start_time).total_seconds()
                        if r.end_time
                        else None
                    ),
                    "error": r.error,
                    "id": r.id,
                }
            )
            if r.reference_example_id:
                example_ids.append(r.reference_example_id)
            results.append(row)
        result = pd.DataFrame(results).set_index("example_id")
        batch_size = 100
        example_outputs = []
        for batch in [
            example_ids[i : i + batch_size]
            for i in range(0, len(example_ids), batch_size)
        ]:
            for example in self.list_examples(example_ids=batch):
                example_outputs.append(
                    {
                        "example_id": example.id,
                        **{
                            f"reference.{k}": v
                            for k, v in (example.outputs or {}).items()
                        },
                    }
                )
        if example_outputs:
            df = pd.DataFrame(example_outputs).set_index("example_id")
            result = df.merge(result, left_index=True, right_index=True)
        # Flatten dict columns into dot syntax for easier access
        return pd.json_normalize(result.to_dict(orient="records"))

    def list_projects(
        self,
        project_ids: Optional[List[ID_TYPE]] = None,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
        reference_dataset_id: Optional[ID_TYPE] = None,
        reference_dataset_name: Optional[str] = None,
        reference_free: Optional[bool] = None,
    ) -> Iterator[ls_schemas.TracerSession]:
        """
        List projects from the LangSmith API.

        Parameters
        ----------
        project_ids : Optional[List[ID_TYPE]], optional
            A list of project IDs to filter by, by default None
        name : Optional[str], optional
            The name of the project to filter by, by default None
        name_contains : Optional[str], optional
            A string to search for in the project name, by default None
        reference_dataset_id : Optional[List[ID_TYPE]], optional
            A dataset ID to filter by, by default None
        reference_dataset_name : Optional[str], optional
            The name of the reference dataset to filter by, by default None
        reference_free : Optional[bool], optional
            Whether to filter for only projects not associated with a dataset.

        Yields
        ------
        TracerSession
            The projects.
        """
        params: Dict[str, Any] = {}
        if project_ids is not None:
            params["id"] = project_ids
        if name is not None:
            params["name"] = name
        if name_contains is not None:
            params["name_contains"] = name_contains
        if reference_dataset_id is not None:
            if reference_dataset_name is not None:
                raise ValueError(
                    "Only one of reference_dataset_id or"
                    " reference_dataset_name may be given"
                )
            params["reference_dataset"] = reference_dataset_id
        elif reference_dataset_name is not None:
            reference_dataset_id = self.read_dataset(
                dataset_name=reference_dataset_name
            ).id
            params["reference_dataset"] = reference_dataset_id
        if reference_free is not None:
            params["reference_free"] = reference_free
        yield from (
            ls_schemas.TracerSessionResult(**project, _host_url=self._host_url)
            for project in self._get_paginated_list("/sessions", params=params)
        )

    @ls_utils.xor_args(("project_name", "project_id"))
    def delete_project(
        self, *, project_name: Optional[str] = None, project_id: Optional[str] = None
    ) -> None:
        """Delete a project from LangSmith.

        Parameters
        ----------
        project_name : str or None, default=None
            The name of the project to delete.
        project_id : str or None, default=None
            The ID of the project to delete.
        """
        if project_name is not None:
            project_id = str(self.read_project(project_name=project_name).id)
        elif project_id is None:
            raise ValueError("Must provide project_name or project_id")
        response = self.session.delete(
            self.api_url + f"/sessions/{_as_uuid(project_id, 'project_id')}",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def create_dataset(
        self,
        dataset_name: str,
        *,
        description: Optional[str] = None,
        data_type: ls_schemas.DataType = ls_schemas.DataType.kv,
    ) -> ls_schemas.Dataset:
        """Create a dataset in the LangSmith API.

        Parameters
        ----------
        dataset_name : str
            The name of the dataset.
        description : str or None, default=None
            The description of the dataset.
        data_type : DataType or None, default=DataType.kv
            The data type of the dataset.

        Returns
        -------
        Dataset
            The created dataset.
        """
        dataset = ls_schemas.DatasetCreate(
            name=dataset_name,
            description=description,
            data_type=data_type,
        )
        response = self.session.post(
            self.api_url + "/datasets",
            headers={**self._headers, "Content-Type": "application/json"},
            data=dataset.json(),
        )
        ls_utils.raise_for_status_with_text(response)
        return ls_schemas.Dataset(
            **response.json(),
            _host_url=self._host_url,
            _tenant_id=self._get_tenant_id(),
        )

    def has_dataset(
        self, *, dataset_name: Optional[str] = None, dataset_id: Optional[str] = None
    ) -> bool:
        """Check whether a dataset exists in your tenant.

        Parameters
        ----------
        dataset_name : str or None, default=None
            The name of the dataset to check.
        dataset_id : str or None, default=None
            The ID of the dataset to check.

        Returns
        -------
        bool
            Whether the dataset exists.
        """
        try:
            self.read_dataset(dataset_name=dataset_name, dataset_id=dataset_id)
            return True
        except ls_utils.LangSmithNotFoundError:
            return False

    @ls_utils.xor_args(("dataset_name", "dataset_id"))
    def read_dataset(
        self,
        *,
        dataset_name: Optional[str] = None,
        dataset_id: Optional[ID_TYPE] = None,
    ) -> ls_schemas.Dataset:
        """Read a dataset from the LangSmith API.

        Parameters
        ----------
        dataset_name : str or None, default=None
            The name of the dataset to read.
        dataset_id : UUID or None, default=None
            The ID of the dataset to read.

        Returns
        -------
        Dataset
            The dataset.
        """
        path = "/datasets"
        params: Dict[str, Any] = {"limit": 1}
        if dataset_id is not None:
            path += f"/{_as_uuid(dataset_id, 'dataset_id')}"
        elif dataset_name is not None:
            params["name"] = dataset_name
        else:
            raise ValueError("Must provide dataset_name or dataset_id")
        response = self._get_with_retries(
            path,
            params=params,
        )
        result = response.json()
        if isinstance(result, list):
            if len(result) == 0:
                raise ls_utils.LangSmithNotFoundError(
                    f"Dataset {dataset_name} not found"
                )
            return ls_schemas.Dataset(
                **result[0], _host_url=self._host_url, _tenant_id=self._get_tenant_id()
            )
        return ls_schemas.Dataset(
            **result, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
        )

    def read_dataset_openai_finetuning(
        self, dataset_id: Optional[str] = None, *, dataset_name: Optional[str] = None
    ) -> list:
        """
        Download a dataset in OpenAI Jsonl format and load it as a list of dicts.

        Parameters
        ----------
        dataset_id : str
            The ID of the dataset to download.
        dataset_name : str
            The name of the dataset to download.

        Returns
        -------
        list
            The dataset loaded as a list of dicts.
        """
        path = "/datasets"
        if dataset_id is not None:
            pass
        elif dataset_name is not None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
        else:
            raise ValueError("Must provide dataset_name or dataset_id")
        response = self._get_with_retries(
            f"{path}/{_as_uuid(dataset_id, 'dataset_id')}/openai_ft",
        )
        dataset = [json.loads(line) for line in response.text.strip().split("\n")]
        return dataset

    def list_datasets(
        self,
        *,
        dataset_ids: Optional[List[ID_TYPE]] = None,
        data_type: Optional[str] = None,
        dataset_name: Optional[str] = None,
        dataset_name_contains: Optional[str] = None,
    ) -> Iterator[ls_schemas.Dataset]:
        """List the datasets on the LangSmith API.

        Yields
        ------
        Dataset
            The datasets.
        """
        params: Dict[str, Any] = {}
        if dataset_ids is not None:
            params["id"] = dataset_ids
        if data_type is not None:
            params["data_type"] = data_type
        if dataset_name is not None:
            params["name"] = dataset_name
        if dataset_name_contains is not None:
            params["name_contains"] = dataset_name_contains

        yield from (
            ls_schemas.Dataset(
                **dataset, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
            )
            for dataset in self._get_paginated_list("/datasets", params=params)
        )

    @ls_utils.xor_args(("dataset_id", "dataset_name"))
    def delete_dataset(
        self,
        *,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
    ) -> None:
        """Delete a dataset from the LangSmith API.

        Parameters
        ----------
        dataset_id : UUID or None, default=None
            The ID of the dataset to delete.
        dataset_name : str or None, default=None
            The name of the dataset to delete.
        """
        if dataset_name is not None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
        if dataset_id is None:
            raise ValueError("Must provide either dataset name or ID")
        response = self.session.delete(
            f"{self.api_url}/datasets/{_as_uuid(dataset_id, 'dataset_id')}",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def clone_public_dataset(
        self,
        token_or_url: str,
        *,
        source_api_url: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> None:
        """Clone a public dataset to your own langsmith tenant.

        This operation is idempotent. If you already have a dataset with the given name,
        this function will do nothing.

        Args:
            token_or_url (str): The token of the public dataset to clone.
            source_api_url: The URL of the langsmith server where the data is hosted.
                Defaults to the API URL of your current client.
            dataset_name (str): The name of the dataset to create in your tenant.
                Defaults to the name of the public dataset.

        """
        source_api_url = source_api_url or self.api_url
        source_api_url, token_uuid = _parse_token_or_url(token_or_url, source_api_url)
        source_client = Client(
            # Placeholder API key not needed anymore in most cases, but
            # some private deployments may have API key-based rate limiting
            # that would cause this to fail if we provide no value.
            api_url=source_api_url,
            api_key="placeholder",
        )
        ds = source_client.read_shared_dataset(token_uuid)
        dataset_name = dataset_name or ds.name
        if self.has_dataset(dataset_name=dataset_name):
            logger.info(
                f"Dataset {dataset_name} already exists in your tenant. Skipping."
            )
            return
        try:
            # Fetch examples first
            examples = list(source_client.list_shared_examples(token_uuid))
            dataset = self.create_dataset(
                dataset_name=dataset_name,
                description=ds.description,
                data_type=ds.data_type or ls_schemas.DataType.kv,
            )
            try:
                self.create_examples(
                    inputs=[e.inputs for e in examples],
                    outputs=[e.outputs for e in examples],
                    dataset_id=dataset.id,
                )
            except BaseException as e:
                # Let's not do automatic clean up for now in case there might be
                # some other reasons why create_examples fails (i.e., not network issue
                # or keyboard interrupt).
                # The risk is that this is an existing dataset that has valid examples
                # populated from another source so we don't want to delete it.
                logger.error(
                    f"An error occurred while creating dataset {dataset_name}. "
                    "You should delete it manually."
                )
                raise e
        finally:
            del source_client

    def _get_data_type(self, dataset_id: ID_TYPE) -> ls_schemas.DataType:
        dataset = self.read_dataset(dataset_id=dataset_id)
        return dataset.data_type

    @ls_utils.xor_args(("dataset_id", "dataset_name"))
    def create_llm_example(
        self,
        prompt: str,
        generation: Optional[str] = None,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> ls_schemas.Example:
        """Add an example (row) to an LLM-type dataset."""
        return self.create_example(
            inputs={"input": prompt},
            outputs={"output": generation},
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            created_at=created_at,
        )

    @ls_utils.xor_args(("dataset_id", "dataset_name"))
    def create_chat_example(
        self,
        messages: List[Union[Mapping[str, Any], ls_schemas.BaseMessageLike]],
        generations: Optional[
            Union[Mapping[str, Any], ls_schemas.BaseMessageLike]
        ] = None,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> ls_schemas.Example:
        """Add an example (row) to a Chat-type dataset."""
        final_input = []
        for message in messages:
            if ls_utils.is_base_message_like(message):
                final_input.append(
                    ls_utils.convert_langchain_message(
                        cast(ls_schemas.BaseMessageLike, message)
                    )
                )
            else:
                final_input.append(cast(dict, message))
        final_generations = None
        if generations is not None:
            if ls_utils.is_base_message_like(generations):
                final_generations = ls_utils.convert_langchain_message(
                    cast(ls_schemas.BaseMessageLike, generations)
                )
            else:
                final_generations = cast(dict, generations)
        return self.create_example(
            inputs={"input": final_input},
            outputs=(
                {"output": final_generations} if final_generations is not None else None
            ),
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            created_at=created_at,
        )

    def create_example_from_run(
        self,
        run: ls_schemas.Run,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> ls_schemas.Example:
        """Add an example (row) to an LLM-type dataset."""
        if dataset_id is None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
            dataset_name = None  # Nested call expects only 1 defined
        dataset_type = self._get_data_type_cached(dataset_id)
        if dataset_type == ls_schemas.DataType.llm:
            if run.run_type != "llm":
                raise ValueError(
                    f"Run type {run.run_type} is not supported"
                    " for dataset of type 'LLM'"
                )
            try:
                prompt = ls_utils.get_prompt_from_inputs(run.inputs)
            except ValueError:
                raise ValueError(
                    "Error converting LLM run inputs to prompt for run"
                    f" {run.id} with inputs {run.inputs}"
                )
            inputs: Dict[str, Any] = {"input": prompt}
            if not run.outputs:
                outputs: Optional[Dict[str, Any]] = None
            else:
                try:
                    generation = ls_utils.get_llm_generation_from_outputs(run.outputs)
                except ValueError:
                    raise ValueError(
                        "Error converting LLM run outputs to generation for run"
                        f" {run.id} with outputs {run.outputs}"
                    )
                outputs = {"output": generation}
        elif dataset_type == ls_schemas.DataType.chat:
            if run.run_type != "llm":
                raise ValueError(
                    f"Run type {run.run_type} is not supported"
                    " for dataset of type 'chat'"
                )
            try:
                inputs = {"input": ls_utils.get_messages_from_inputs(run.inputs)}
            except ValueError:
                raise ValueError(
                    "Error converting LLM run inputs to chat messages for run"
                    f" {run.id} with inputs {run.inputs}"
                )
            if not run.outputs:
                outputs = None
            else:
                try:
                    outputs = {
                        "output": ls_utils.get_message_generation_from_outputs(
                            run.outputs
                        )
                    }
                except ValueError:
                    raise ValueError(
                        "Error converting LLM run outputs to chat generations"
                        f" for run {run.id} with outputs {run.outputs}"
                    )
        elif dataset_type == ls_schemas.DataType.kv:
            # Anything goes
            inputs = run.inputs
            outputs = run.outputs

        else:
            raise ValueError(f"Dataset type {dataset_type} not recognized.")
        return self.create_example(
            inputs=inputs,
            outputs=outputs,
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            created_at=created_at,
        )

    def create_examples(
        self,
        *,
        inputs: Sequence[Mapping[str, Any]],
        outputs: Optional[Sequence[Optional[Mapping[str, Any]]]] = None,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create examples in a dataset.

        Parameters
        ----------
        inputs : Sequence[Mapping[str, Any]]
            The input values for the examples.
        outputs : Optional[Sequence[Optional[Mapping[str, Any]]]], default=None
            The output values for the examples.
        dataset_id : Optional[ID_TYPE], default=None
            The ID of the dataset to create the examples in.
        dataset_name : Optional[str], default=None
            The name of the dataset to create the examples in.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If both `dataset_id` and `dataset_name` are `None`.
        """
        if dataset_id is None and dataset_name is None:
            raise ValueError("Either dataset_id or dataset_name must be provided.")

        if dataset_id is None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
        examples = [
            {
                "inputs": in_,
                "outputs": out_,
                "dataset_id": dataset_id,
            }
            for in_, out_ in zip(inputs, outputs or [None] * len(inputs))
        ]

        response = self.session.post(
            f"{self.api_url}/examples/bulk",
            headers={**self._headers, "Content-Type": "application/json"},
            data=json.dumps(examples, default=_serialize_json),
        )
        ls_utils.raise_for_status_with_text(response)

    @ls_utils.xor_args(("dataset_id", "dataset_name"))
    def create_example(
        self,
        inputs: Mapping[str, Any],
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None,
        outputs: Optional[Mapping[str, Any]] = None,
        example_id: Optional[ID_TYPE] = None,
    ) -> ls_schemas.Example:
        """Create a dataset example in the LangSmith API.

        Examples are rows in a dataset, containing the inputs
        and expected outputs (or other reference information)
        for a model or chain.

        Parameters
        ----------
        inputs : Mapping[str, Any]
            The input values for the example.
        dataset_id : UUID or None, default=None
            The ID of the dataset to create the example in.
        dataset_name : str or None, default=None
            The name of the dataset to create the example in.
        created_at : datetime or None, default=None
            The creation timestamp of the example.
        outputs : Mapping[str, Any] or None, default=None
            The output values for the example.
        exemple_id : UUID or None, default=None
            The ID of the example to create. If not provided, a new
            example will be created.

        Returns
        -------
        Example
            The created example.
        """
        if dataset_id is None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id

        data = {
            "inputs": inputs,
            "outputs": outputs,
            "dataset_id": dataset_id,
        }
        if created_at:
            data["created_at"] = created_at.isoformat()
        if example_id:
            data["id"] = example_id
        example = ls_schemas.ExampleCreate(**data)
        response = self.session.post(
            f"{self.api_url}/examples",
            headers={**self._headers, "Content-Type": "application/json"},
            data=example.json(),
        )
        ls_utils.raise_for_status_with_text(response)
        result = response.json()
        return ls_schemas.Example(
            **result, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
        )

    def read_example(self, example_id: ID_TYPE) -> ls_schemas.Example:
        """Read an example from the LangSmith API.

        Parameters
        ----------
        example_id : str or UUID
            The ID of the example to read.

        Returns
        -------
        Example
            The example.
        """
        response = self._get_with_retries(
            f"/examples/{_as_uuid(example_id, 'example_id')}",
        )
        return ls_schemas.Example(
            **response.json(),
            _host_url=self._host_url,
            _tenant_id=self._get_tenant_id(),
        )

    def list_examples(
        self,
        dataset_id: Optional[ID_TYPE] = None,
        dataset_name: Optional[str] = None,
        example_ids: Optional[Sequence[ID_TYPE]] = None,
        inline_s3_urls: bool = True,
    ) -> Iterator[ls_schemas.Example]:
        """Retrieve the example rows of the specified dataset.

        Parameters
        ----------
        dataset_id : UUID or None, default=None
            The ID of the dataset to filter by.
        dataset_name : str or None, default=None
            The name of the dataset to filter by.
        example_ids : List[UUID] or None, default=None
            The IDs of the examples to filter by.

        Yields
        ------
        Example
            The examples.
        """
        params: Dict[str, Any] = {}
        if dataset_id is not None:
            params["dataset"] = dataset_id
        elif dataset_name is not None:
            dataset_id = self.read_dataset(dataset_name=dataset_name).id
            params["dataset"] = dataset_id
        else:
            pass
        if example_ids is not None:
            params["id"] = example_ids
        params["inline_s3_urls"] = inline_s3_urls
        yield from (
            ls_schemas.Example(
                **example, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
            )
            for example in self._get_paginated_list("/examples", params=params)
        )

    def update_example(
        self,
        example_id: str,
        *,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Mapping[str, Any]] = None,
        dataset_id: Optional[ID_TYPE] = None,
    ) -> Dict[str, Any]:
        """Update a specific example.

        Parameters
        ----------
        example_id : str or UUID
            The ID of the example to update.
        inputs : Dict[str, Any] or None, default=None
            The input values to update.
        outputs : Mapping[str, Any] or None, default=None
            The output values to update.
        dataset_id : UUID or None, default=None
            The ID of the dataset to update.

        Returns
        -------
        Dict[str, Any]
            The updated example.
        """
        example = ls_schemas.ExampleUpdate(
            inputs=inputs,
            outputs=outputs,
            dataset_id=dataset_id,
        )
        response = self.session.patch(
            f"{self.api_url}/examples/{_as_uuid(example_id, 'example_id')}",
            headers={**self._headers, "Content-Type": "application/json"},
            data=example.json(exclude_none=True),
        )
        ls_utils.raise_for_status_with_text(response)
        return response.json()

    def delete_example(self, example_id: ID_TYPE) -> None:
        """Delete an example by ID.

        Parameters
        ----------
        example_id : str or UUID
            The ID of the example to delete.
        """
        response = self.session.delete(
            f"{self.api_url}/examples/{_as_uuid(example_id, 'example_id')}",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def _resolve_run_id(
        self,
        run: Union[ls_schemas.Run, ls_schemas.RunBase, str, uuid.UUID],
        load_child_runs: bool,
    ) -> ls_schemas.Run:
        """Resolve the run ID.

        Parameters
        ----------
        run : Run or RunBase or str or UUID
            The run to resolve.
        load_child_runs : bool
            Whether to load child runs.

        Returns
        -------
        Run
            The resolved run.

        Raises
        ------
        TypeError
            If the run type is invalid.
        """
        if isinstance(run, (str, uuid.UUID)):
            run_ = self.read_run(run, load_child_runs=load_child_runs)
        else:
            run_ = run
        return run_

    def _resolve_example_id(
        self,
        example: Union[ls_schemas.Example, str, uuid.UUID, dict, None],
        run: ls_schemas.Run,
    ) -> Optional[ls_schemas.Example]:
        """Resolve the example ID.

        Parameters
        ----------
        example : Example or str or UUID or dict or None
            The example to resolve.
        run : Run
            The run associated with the example.

        Returns
        -------
        Example or None
            The resolved example.
        """
        if isinstance(example, (str, uuid.UUID)):
            reference_example_ = self.read_example(example)
        elif isinstance(example, ls_schemas.Example):
            reference_example_ = example
        elif isinstance(example, dict):
            reference_example_ = ls_schemas.Example(
                **example, _host_url=self._host_url, _tenant_id=self._get_tenant_id()
            )
        elif run.reference_example_id is not None:
            reference_example_ = self.read_example(run.reference_example_id)
        else:
            reference_example_ = None
        return reference_example_

    def _select_eval_results(
        self,
        results: Union[ls_evaluator.EvaluationResult, ls_evaluator.EvaluationResults],
    ) -> List[ls_evaluator.EvaluationResult]:
        if isinstance(results, ls_evaluator.EvaluationResult):
            results_ = [results]
        elif isinstance(results, dict) and "results" in results:
            results_ = cast(List[ls_evaluator.EvaluationResult], results["results"])
        else:
            raise TypeError(
                f"Invalid evaluation result type {type(results)}."
                " Expected EvaluationResult or EvaluationResults."
            )
        return results_

    def evaluate_run(
        self,
        run: Union[ls_schemas.Run, ls_schemas.RunBase, str, uuid.UUID],
        evaluator: ls_evaluator.RunEvaluator,
        *,
        source_info: Optional[Dict[str, Any]] = None,
        reference_example: Optional[
            Union[ls_schemas.Example, str, dict, uuid.UUID]
        ] = None,
        load_child_runs: bool = False,
    ) -> ls_evaluator.EvaluationResult:
        """Evaluate a run.

        Parameters
        ----------
        run : Run or RunBase or str or UUID
            The run to evaluate.
        evaluator : RunEvaluator
            The evaluator to use.
        source_info : Dict[str, Any] or None, default=None
            Additional information about the source of the evaluation to log
            as feedback metadata.
        reference_example : Example or str or dict or UUID or None, default=None
            The example to use as a reference for the evaluation.
            If not provided, the run's reference example will be used.
        load_child_runs : bool, default=False
            Whether to load child runs when resolving the run ID.

        Returns
        -------
        Feedback
            The feedback object created by the evaluation.
        """
        run_ = self._resolve_run_id(run, load_child_runs=load_child_runs)
        reference_example_ = self._resolve_example_id(reference_example, run_)
        evaluator_response = evaluator.evaluate_run(
            run_,
            example=reference_example_,
        )
        results = self._log_evaluation_feedback(
            evaluator_response,
            run_,
            source_info=source_info,
        )
        # TODO: Return all results
        return results[0]

    def _log_evaluation_feedback(
        self,
        evaluator_response: Union[
            ls_evaluator.EvaluationResult, ls_evaluator.EvaluationResults
        ],
        run: ls_schemas.Run,
        source_info: Optional[Dict[str, Any]] = None,
    ) -> List[ls_evaluator.EvaluationResult]:
        results = self._select_eval_results(evaluator_response)
        for res in results:
            source_info_ = source_info or {}
            if res.evaluator_info:
                source_info_ = {**res.evaluator_info, **source_info_}
            run_id_ = res.target_run_id if res.target_run_id else run.id
            self.create_feedback(
                run_id_,
                res.key,
                score=res.score,
                value=res.value,
                comment=res.comment,
                correction=res.correction,
                source_info=source_info_,
                source_run_id=res.source_run_id,
                feedback_source_type=ls_schemas.FeedbackSourceType.MODEL,
            )
        return results

    async def aevaluate_run(
        self,
        run: Union[ls_schemas.Run, str, uuid.UUID],
        evaluator: ls_evaluator.RunEvaluator,
        *,
        source_info: Optional[Dict[str, Any]] = None,
        reference_example: Optional[
            Union[ls_schemas.Example, str, dict, uuid.UUID]
        ] = None,
        load_child_runs: bool = False,
    ) -> ls_evaluator.EvaluationResult:
        """Evaluate a run asynchronously.

        Parameters
        ----------
        run : Run or str or UUID
            The run to evaluate.
        evaluator : RunEvaluator
            The evaluator to use.
        source_info : Dict[str, Any] or None, default=None
            Additional information about the source of the evaluation to log
            as feedback metadata.
        reference_example : Optional Example or UUID, default=None
            The example to use as a reference for the evaluation.
            If not provided, the run's reference example will be used.
        load_child_runs : bool, default=False
            Whether to load child runs when resolving the run ID.

        Returns
        -------
        EvaluationResult
            The evaluation result object created by the evaluation.
        """
        run_ = self._resolve_run_id(run, load_child_runs=load_child_runs)
        reference_example_ = self._resolve_example_id(reference_example, run_)
        evaluator_response = await evaluator.aevaluate_run(
            run_,
            example=reference_example_,
        )
        # TODO: Return all results and use async API
        results = self._log_evaluation_feedback(
            evaluator_response,
            run_,
            source_info=source_info,
        )
        return results[0]

    def create_feedback(
        self,
        run_id: ID_TYPE,
        key: str,
        *,
        score: Union[float, int, bool, None] = None,
        value: Union[float, int, bool, str, dict, None] = None,
        correction: Union[dict, None] = None,
        comment: Union[str, None] = None,
        source_info: Optional[Dict[str, Any]] = None,
        feedback_source_type: Union[
            ls_schemas.FeedbackSourceType, str
        ] = ls_schemas.FeedbackSourceType.API,
        source_run_id: Optional[ID_TYPE] = None,
        feedback_id: Optional[ID_TYPE] = None,
        eager: bool = False,
        stop_after_attempt: int = 10,
    ) -> ls_schemas.Feedback:
        """Create a feedback in the LangSmith API.

        Parameters
        ----------
        run_id : str or UUID
            The ID of the run to provide feedback on.
        key : str
            The name of the metric, tag, or 'aspect' this feedback is about.
        score : float or int or bool or None, default=None
            The score to rate this run on the metric or aspect.
        value : float or int or bool or str or dict or None, default=None
            The display value or non-numeric value for this feedback.
        correction : dict or None, default=None
            The proper ground truth for this run.
        comment : str or None, default=None
            A comment about this feedback.
        source_info : Dict[str, Any] or None, default=None
            Information about the source of this feedback.
        feedback_source_type : FeedbackSourceType or str, default=FeedbackSourceType.API
            The type of feedback source, such as model (for model-generated feedback)
                or API.
        source_run_id : str or UUID or None, default=None,
            The ID of the run that generated this feedback, if a "model" type.
        feedback_id : str or UUID or None, default=None
            The ID of the feedback to create. If not provided, a random UUID will be
            generated.
        eager : bool, default=False
            Whether to skip the write queue when creating the feedback. This means
            that the feedback will be immediately available for reading, but may
            cause the write to fail if the API is under heavy load, since the target
            run_id may have not been created yet.
        stop_after_attempt : int, default=10
            The number of times to retry the request before giving up.
        """
        if not isinstance(feedback_source_type, ls_schemas.FeedbackSourceType):
            feedback_source_type = ls_schemas.FeedbackSourceType(feedback_source_type)
        if feedback_source_type == ls_schemas.FeedbackSourceType.API:
            feedback_source: ls_schemas.FeedbackSourceBase = (
                ls_schemas.APIFeedbackSource(metadata=source_info)
            )
        elif feedback_source_type == ls_schemas.FeedbackSourceType.MODEL:
            feedback_source = ls_schemas.ModelFeedbackSource(metadata=source_info)
        else:
            raise ValueError(f"Unknown feedback source type {feedback_source_type}")
        feedback_source.metadata = (
            feedback_source.metadata if feedback_source.metadata is not None else {}
        )
        if source_run_id is not None and "__run" not in feedback_source.metadata:
            feedback_source.metadata["__run"] = {"run_id": str(source_run_id)}
        if feedback_source.metadata and "__run" in feedback_source.metadata:
            # Validate that the linked run ID is a valid UUID
            # Run info may be a base model or dict.
            _run_meta: Union[dict, Any] = feedback_source.metadata["__run"]
            if hasattr(_run_meta, "dict") and callable(_run_meta):
                _run_meta = _run_meta.dict()
            if "run_id" in _run_meta:
                _run_meta["run_id"] = str(
                    _as_uuid(
                        feedback_source.metadata["__run"]["run_id"],
                        "feedback_source.metadata['__run']['run_id']",
                    )
                )
            feedback_source.metadata["__run"] = _run_meta
        feedback = ls_schemas.FeedbackCreate(
            id=feedback_id or uuid.uuid4(),
            run_id=run_id,
            key=key,
            score=score,
            value=value,
            correction=correction,
            comment=comment,
            feedback_source=feedback_source,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            modified_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.request_with_retries(
            "POST",
            self.api_url + "/feedback" + ("/eager" if eager else ""),
            request_kwargs={
                "data": json.dumps(
                    feedback.dict(exclude_none=True), default=_serialize_json
                ),
                "headers": {
                    **self._headers,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                "timeout": self.timeout_ms / 1000,
            },
            stop_after_attempt=stop_after_attempt,
            retry_on=(ls_utils.LangSmithNotFoundError,),
        )
        return ls_schemas.Feedback(**feedback.dict())

    def update_feedback(
        self,
        feedback_id: ID_TYPE,
        *,
        score: Union[float, int, bool, None] = None,
        value: Union[float, int, bool, str, dict, None] = None,
        correction: Union[dict, None] = None,
        comment: Union[str, None] = None,
    ) -> None:
        """Update a feedback in the LangSmith API.

        Parameters
        ----------
        feedback_id : str or UUID
            The ID of the feedback to update.
        score : float or int or bool or None, default=None
            The score to update the feedback with.
        value : float or int or bool or str or dict or None, default=None
            The value to update the feedback with.
        correction : dict or None, default=None
            The correction to update the feedback with.
        comment : str or None, default=None
            The comment to update the feedback with.
        """
        feedback_update: Dict[str, Any] = {}
        if score is not None:
            feedback_update["score"] = score
        if value is not None:
            feedback_update["value"] = value
        if correction is not None:
            feedback_update["correction"] = correction
        if comment is not None:
            feedback_update["comment"] = comment
        response = self.session.patch(
            self.api_url + f"/feedback/{_as_uuid(feedback_id, 'feedback_id')}",
            headers={**self._headers, "Content-Type": "application/json"},
            data=json.dumps(feedback_update, default=_serialize_json),
        )
        ls_utils.raise_for_status_with_text(response)

    def read_feedback(self, feedback_id: ID_TYPE) -> ls_schemas.Feedback:
        """Read a feedback from the LangSmith API.

        Parameters
        ----------
        feedback_id : str or UUID
            The ID of the feedback to read.

        Returns
        -------
        Feedback
            The feedback.
        """
        response = self._get_with_retries(
            f"/feedback/{_as_uuid(feedback_id, 'feedback_id')}",
        )
        return ls_schemas.Feedback(**response.json())

    def list_feedback(
        self,
        *,
        run_ids: Optional[Sequence[ID_TYPE]] = None,
        feedback_key: Optional[Sequence[str]] = None,
        feedback_source_type: Optional[Sequence[ls_schemas.FeedbackSourceType]] = None,
        **kwargs: Any,
    ) -> Iterator[ls_schemas.Feedback]:
        """List the feedback objects on the LangSmith API.

        Parameters
        ----------
        run_ids : List[str or UUID] or None, default=None
            The IDs of the runs to filter by.
        feedback_key: List[str] or None, default=None
            The feedback key(s) to filter by. Example: 'correctness'
            The query performs a union of all feedback keys.
        feedback_source_type: List[FeedbackSourceType] or None, default=None
            The type of feedback source, such as model
            (for model-generated feedback) or API.
        **kwargs : Any
            Additional keyword arguments.

        Yields
        ------
        Feedback
            The feedback objects.
        """
        params: dict = {
            "run": run_ids,
            **kwargs,
        }
        if feedback_key is not None:
            params["key"] = feedback_key
        if feedback_source_type is not None:
            params["source"] = feedback_source_type
        yield from (
            ls_schemas.Feedback(**feedback)
            for feedback in self._get_paginated_list("/feedback", params=params)
        )

    def delete_feedback(self, feedback_id: ID_TYPE) -> None:
        """Delete a feedback by ID.

        Parameters
        ----------
        feedback_id : str or UUID
            The ID of the feedback to delete.
        """
        response = self.session.delete(
            f"{self.api_url}/feedback/{_as_uuid(feedback_id, 'feedback_id')}",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    # Annotation Queue API

    def list_annotation_queues(
        self,
        *,
        queue_ids: Optional[List[ID_TYPE]] = None,
        name: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> Iterator[ls_schemas.AnnotationQueue]:
        params: dict = {
            "ids": (
                [_as_uuid(id_, f"queue_ids[{i}]") for i, id_ in enumerate(queue_ids)]
                if queue_ids is not None
                else None
            ),
            "name": name,
            "name_contains": name_contains,
        }
        yield from (
            ls_schemas.AnnotationQueue(**queue)
            for queue in self._get_paginated_list("/annotation-queues", params=params)
        )

    def create_annotation_queue(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        queue_id: Optional[ID_TYPE] = None,
    ) -> ls_schemas.AnnotationQueue:
        body = {
            "name": name,
            "description": description,
            "id": queue_id,
        }
        response = self.request_with_retries(
            "post",
            f"{self.api_url}/annotation-queues",
            {
                "json": {k: v for k, v in body.items() if v is not None},
                "headers": self._headers,
            },
        )
        ls_utils.raise_for_status_with_text(response)
        return ls_schemas.AnnotationQueue(**response.json())

    def read_annotation_queue(self, queue_id: ID_TYPE) -> ls_schemas.AnnotationQueue:
        # TODO: Replace when actual endpoint is added
        return next(self.list_annotation_queues(queue_ids=[queue_id]))

    def update_annotation_queue(
        self, queue_id: ID_TYPE, *, name: str, description: Optional[str] = None
    ) -> None:
        response = self.request_with_retries(
            "patch",
            f"{self.api_url}/annotation-queues/{_as_uuid(queue_id, 'queue_id')}",
            {
                "json": {
                    "name": name,
                    "description": description,
                },
                "headers": self._headers,
            },
        )
        ls_utils.raise_for_status_with_text(response)

    def delete_annotation_queue(self, queue_id: ID_TYPE) -> None:
        response = self.session.delete(
            f"{self.api_url}/annotation-queues/{_as_uuid(queue_id, 'queue_id')}",
            headers=self._headers,
        )
        ls_utils.raise_for_status_with_text(response)

    def add_runs_to_annotation_queue(
        self, queue_id: ID_TYPE, *, run_ids: List[ID_TYPE]
    ) -> None:
        response = self.request_with_retries(
            "post",
            f"{self.api_url}/annotation-queues/{_as_uuid(queue_id, 'queue_id')}/runs",
            {
                "json": [
                    str(_as_uuid(id_, f"run_ids[{i}]")) for i, id_ in enumerate(run_ids)
                ],
                "headers": self._headers,
            },
        )
        ls_utils.raise_for_status_with_text(response)

    def list_runs_from_annotation_queue(
        self, queue_id: ID_TYPE
    ) -> Iterator[ls_schemas.RunWithAnnotationQueueInfo]:
        path = f"/annotation-queues/{_as_uuid(queue_id, 'queue_id')}/runs"
        yield from (
            ls_schemas.RunWithAnnotationQueueInfo(**run)
            for run in self._get_paginated_list(path, params={"headers": self._headers})
        )

    async def arun_on_dataset(
        self,
        dataset_name: str,
        llm_or_chain_factory: Any,
        *,
        evaluation: Optional[Any] = None,
        concurrency_level: int = 5,
        project_name: Optional[str] = None,
        project_metadata: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        tags: Optional[List[str]] = None,
        input_mapper: Optional[Callable[[Dict], Any]] = None,
        revision_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously run the Chain or language model on a dataset
        and store traces to the specified project name.

        Args:
            dataset_name: Name of the dataset to run the chain on.
            llm_or_chain_factory: Language model or Chain constructor to run
                over the dataset. The Chain constructor is used to permit
                independent calls on each example without carrying over state.
            evaluation: Optional evaluation configuration to use when evaluating
            concurrency_level: The number of async tasks to run concurrently.
            project_name: Name of the project to store the traces in.
                Defaults to {dataset_name}-{chain class name}-{datetime}.
            project_metadata: Optional metadata to store with the project.
            verbose: Whether to print progress.
            tags: Tags to add to each run in the project.
            input_mapper: A function to map to the inputs dictionary from an Example
                to the format expected by the model to be evaluated. This is useful if
                your model needs to deserialize more complex schema or if your dataset
                has inputs with keys that differ from what is expected by your chain
                or agent.
            revision_id: Optional revision identifier to assign this test run to
                track the performance of different versions of your system.

        Returns:
            A dictionary containing the run's project name and the
            resulting model outputs.

        For the synchronous version, see client.run_on_dataset.

        Examples
        --------

        .. code-block:: python

            from langsmith import Client
            from langchain.chat_models import ChatOpenAI
            from langchain.chains import LLMChain
            from langchain.smith import RunEvalConfig

            # Chains may have memory. Passing in a constructor function lets the
            # evaluation framework avoid cross-contamination between runs.
            def construct_chain():
                llm = ChatOpenAI(temperature=0)
                chain = LLMChain.from_string(
                    llm,
                    "What's the answer to {your_input_key}"
                )
                return chain

            # Load off-the-shelf evaluators via config or the EvaluatorType (string or enum)
            evaluation_config = RunEvalConfig(
                evaluators=[
                    "qa",  # "Correctness" against a reference answer
                    "embedding_distance",
                    RunEvalConfig.Criteria("helpfulness"),
                    RunEvalConfig.Criteria({
                        "fifth-grader-score": "Do you have to be smarter than a fifth grader to answer this question?"
                    }),
                ]
            )

            client = Client()
            await client.arun_on_dataset(
                "<my_dataset_name>",
                construct_chain,
                evaluation=evaluation_config,
            )

        You can also create custom evaluators by subclassing the
        :class:`StringEvaluator <langchain.evaluation.schema.StringEvaluator>`
        or LangSmith's `RunEvaluator` classes.

        .. code-block:: python

            from typing import Optional
            from langchain.evaluation import StringEvaluator

            class MyStringEvaluator(StringEvaluator):

                @property
                def requires_input(self) -> bool:
                    return False

                @property
                def requires_reference(self) -> bool:
                    return True

                @property
                def evaluation_name(self) -> str:
                    return "exact_match"

                def _evaluate_strings(self, prediction, reference=None, input=None, **kwargs) -> dict:
                    return {"score": prediction == reference}


            evaluation_config = RunEvalConfig(
                custom_evaluators = [MyStringEvaluator()],
            )

            await client.arun_on_dataset(
                "<my_dataset_name>",
                construct_chain,
                evaluation=evaluation_config,
            )
        """  # noqa: E501
        try:
            from langchain.smith import arun_on_dataset as _arun_on_dataset
        except ImportError:
            raise ImportError(
                "The client.arun_on_dataset function requires the langchain"
                "package to run.\nInstall with pip install langchain"
            )
        return await _arun_on_dataset(
            dataset_name=dataset_name,
            llm_or_chain_factory=llm_or_chain_factory,
            client=self,
            evaluation=evaluation,
            concurrency_level=concurrency_level,
            project_name=project_name,
            project_metadata=project_metadata,
            verbose=verbose,
            tags=tags,
            input_mapper=input_mapper,
            revision_id=revision_id,
        )

    def run_on_dataset(
        self,
        dataset_name: str,
        llm_or_chain_factory: Any,
        *,
        evaluation: Optional[Any] = None,
        concurrency_level: int = 5,
        project_name: Optional[str] = None,
        project_metadata: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        tags: Optional[List[str]] = None,
        input_mapper: Optional[Callable[[Dict], Any]] = None,
        revision_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the Chain or language model on a dataset and store traces
        to the specified project name.

        Args:
            dataset_name: Name of the dataset to run the chain on.
            llm_or_chain_factory: Language model or Chain constructor to run
                over the dataset. The Chain constructor is used to permit
                independent calls on each example without carrying over state.
            evaluation: Configuration for evaluators to run on the
                results of the chain
            concurrency_level: The number of tasks to execute concurrently.
            project_name: Name of the project to store the traces in.
                Defaults to {dataset_name}-{chain class name}-{datetime}.
            project_metadata: Metadata to store with the project.
            verbose: Whether to print progress.
            tags: Tags to add to each run in the project.
            input_mapper: A function to map to the inputs dictionary from an Example
                to the format expected by the model to be evaluated. This is useful if
                your model needs to deserialize more complex schema or if your dataset
                has inputs with keys that differ from what is expected by your chain
                or agent.
            revision_id: Optional revision identifier to assign this test run to
                track the performance of different versions of your system.

        Returns:
            A dictionary containing the run's project name and the resulting model outputs.


        For the (usually faster) async version of this function, see `client.arun_on_dataset`.

        Examples
        --------

        .. code-block:: python

            from langsmith import Client
            from langchain.chat_models import ChatOpenAI
            from langchain.chains import LLMChain
            from langchain.smith import RunEvalConfig

            # Chains may have memory. Passing in a constructor function lets the
            # evaluation framework avoid cross-contamination between runs.
            def construct_chain():
                llm = ChatOpenAI(temperature=0)
                chain = LLMChain.from_string(
                    llm,
                    "What's the answer to {your_input_key}"
                )
                return chain

            # Load off-the-shelf evaluators via config or the EvaluatorType (string or enum)
            evaluation_config = RunEvalConfig(
                evaluators=[
                    "qa",  # "Correctness" against a reference answer
                    "embedding_distance",
                    RunEvalConfig.Criteria("helpfulness"),
                    RunEvalConfig.Criteria({
                        "fifth-grader-score": "Do you have to be smarter than a fifth grader to answer this question?"
                    }),
                ]
            )

            client = Client()
            client.run_on_dataset(
                "<my_dataset_name>",
                construct_chain,
                evaluation=evaluation_config,
            )

        You can also create custom evaluators by subclassing the
        :class:`StringEvaluator <langchain.evaluation.schema.StringEvaluator>`
        or LangSmith's `RunEvaluator` classes.

        .. code-block:: python

            from typing import Optional
            from langchain.evaluation import StringEvaluator

            class MyStringEvaluator(StringEvaluator):

                @property
                def requires_input(self) -> bool:
                    return False

                @property
                def requires_reference(self) -> bool:
                    return True

                @property
                def evaluation_name(self) -> str:
                    return "exact_match"

                def _evaluate_strings(self, prediction, reference=None, input=None, **kwargs) -> dict:
                    return {"score": prediction == reference}


            evaluation_config = RunEvalConfig(
                custom_evaluators = [MyStringEvaluator()],
            )

            client.run_on_dataset(
                "<my_dataset_name>",
                construct_chain,
                evaluation=evaluation_config,
            )
        """  # noqa: E501
        try:
            from langchain.smith import run_on_dataset as _run_on_dataset
        except ImportError:
            raise ImportError(
                "The client.run_on_dataset function requires the langchain"
                "package to run.\nInstall with pip install langchain"
            )
        return _run_on_dataset(
            dataset_name=dataset_name,
            llm_or_chain_factory=llm_or_chain_factory,
            concurrency_level=concurrency_level,
            client=self,
            evaluation=evaluation,
            project_name=project_name,
            project_metadata=project_metadata,
            verbose=verbose,
            tags=tags,
            input_mapper=input_mapper,
            revision_id=revision_id,
        )


def _tracing_thread_drain_queue(
    tracing_queue: Queue, limit: int = 100, block: bool = True
) -> List[TracingQueueItem]:
    next_batch: List[TracingQueueItem] = []
    try:
        # wait 250ms for the first item, then
        # - drain the queue with a 50ms block timeout
        # - stop draining if we hit the limit
        # shorter drain timeout is used instead of non-blocking calls to
        # avoid creating too many small batches
        if item := tracing_queue.get(block=block, timeout=0.25):
            next_batch.append(item)
        while item := tracing_queue.get(block=block, timeout=0.05):
            next_batch.append(item)
            if limit and len(next_batch) >= limit:
                break
    except Empty:
        pass
    return next_batch


def _tracing_thread_handle_batch(
    client: Client, tracing_queue: Queue, batch: List[TracingQueueItem]
) -> None:
    create = [it.item for it in batch if it.action == "create"]
    update = [it.item for it in batch if it.action == "update"]
    try:
        client.batch_ingest_runs(create=create, update=update, pre_sampled=True)
    except Exception:
        # exceptions are logged elsewhere, but we need to make sure the
        # background thread continues to run
        pass
    finally:
        for _ in batch:
            tracing_queue.task_done()


_AUTO_SCALE_UP_QSIZE_TRIGGER = 1000
_AUTO_SCALE_UP_NTHREADS_LIMIT = 16
_AUTO_SCALE_DOWN_NEMPTY_TRIGGER = 4


def _ensure_ingest_config(
    info: Optional[ls_schemas.LangSmithInfo],
) -> ls_schemas.BatchIngestConfig:
    default_config = ls_schemas.BatchIngestConfig(
        size_limit=100,
        scale_up_nthreads_limit=_AUTO_SCALE_UP_NTHREADS_LIMIT,
        scale_up_qsize_trigger=_AUTO_SCALE_UP_QSIZE_TRIGGER,
        scale_down_nempty_trigger=_AUTO_SCALE_DOWN_NEMPTY_TRIGGER,
    )
    if not info:
        return default_config
    try:
        if not info.batch_ingest_config:
            return default_config
        return info.batch_ingest_config
    except BaseException:
        return default_config


def _tracing_control_thread_func(client_ref: weakref.ref[Client]) -> None:
    client = client_ref()
    if client is None:
        return
    try:
        if not client.info:
            print(f"no info: {client.info}", file=sys.stderr, flush=True)
            return
    except BaseException as e:
        logger.debug("Error in tracing control thread: %s", e)
        return
    tracing_queue = client.tracing_queue
    assert tracing_queue is not None
    batch_ingest_config = _ensure_ingest_config(client.info)
    size_limit: int = batch_ingest_config["size_limit"]
    scale_up_nthreads_limit: int = batch_ingest_config["scale_up_nthreads_limit"]
    scale_up_qsize_trigger: int = batch_ingest_config["scale_up_qsize_trigger"]

    sub_threads: List[threading.Thread] = []
    # 1 for this func, 1 for getrefcount, 1 for _get_data_type_cached
    num_known_refs = 3

    # loop until
    while (
        # the main thread dies
        threading.main_thread().is_alive()
        # or we're the only remaining reference to the client
        and sys.getrefcount(client) > num_known_refs + len(sub_threads)
    ):
        for thread in sub_threads:
            if not thread.is_alive():
                sub_threads.remove(thread)
        if (
            len(sub_threads) < scale_up_nthreads_limit
            and tracing_queue.qsize() > scale_up_qsize_trigger
        ):
            new_thread = threading.Thread(
                target=_tracing_sub_thread_func, args=(weakref.ref(client),)
            )
            sub_threads.append(new_thread)
            new_thread.start()
        if next_batch := _tracing_thread_drain_queue(tracing_queue, limit=size_limit):
            _tracing_thread_handle_batch(client, tracing_queue, next_batch)
    # drain the queue on exit
    while next_batch := _tracing_thread_drain_queue(
        tracing_queue, limit=size_limit, block=False
    ):
        _tracing_thread_handle_batch(client, tracing_queue, next_batch)


def _tracing_sub_thread_func(client_ref: weakref.ref[Client]) -> None:
    client = client_ref()
    if client is None:
        return
    try:
        if not client.info:
            return
    except BaseException as e:
        logger.debug("Error in tracing control thread: %s", e)
        return
    tracing_queue = client.tracing_queue
    assert tracing_queue is not None
    batch_ingest_config = _ensure_ingest_config(client.info)
    size_limit = batch_ingest_config.get("size_limit", 100)
    seen_successive_empty_queues = 0

    # loop until
    while (
        # the main thread dies
        threading.main_thread().is_alive()
        # or we've seen the queue empty 4 times in a row
        and seen_successive_empty_queues
        <= batch_ingest_config["scale_down_nempty_trigger"]
    ):
        if next_batch := _tracing_thread_drain_queue(tracing_queue, limit=size_limit):
            seen_successive_empty_queues = 0
            _tracing_thread_handle_batch(client, tracing_queue, next_batch)
        else:
            seen_successive_empty_queues += 1

    # drain the queue on exit
    while next_batch := _tracing_thread_drain_queue(
        tracing_queue, limit=size_limit, block=False
    ):
        _tracing_thread_handle_batch(client, tracing_queue, next_batch)
