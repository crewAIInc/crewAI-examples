"""Generic utility functions."""

import enum
import functools
import logging
import os
import subprocess
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import requests

from langsmith import schemas as ls_schemas

_LOGGER = logging.getLogger(__name__)


class LangSmithError(Exception):
    """An error occurred while communicating with the LangSmith API."""


class LangSmithAPIError(LangSmithError):
    """Internal server error while communicating with LangSmith."""


class LangSmithUserError(LangSmithError):
    """User error caused an exception when communicating with LangSmith."""


class LangSmithRateLimitError(LangSmithError):
    """You have exceeded the rate limit for the LangSmith API."""


class LangSmithAuthError(LangSmithError):
    """Couldn't authenticate with the LangSmith API."""


class LangSmithNotFoundError(LangSmithError):
    """Couldn't find the requested resource."""


class LangSmithConflictError(LangSmithError):
    """The resource already exists."""


class LangSmithConnectionError(LangSmithError):
    """Couldn't connect to the LangSmith API."""


def tracing_is_enabled() -> bool:
    """Return True if tracing is enabled."""
    return (
        os.environ.get(
            "LANGCHAIN_TRACING_V2", os.environ.get("LANGCHAIN_TRACING", "")
        ).lower()
        == "true"
    )


def xor_args(*arg_groups: Tuple[str, ...]) -> Callable:
    """Validate specified keyword args are mutually exclusive."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Validate exactly one arg in each group is not None."""
            counts = [
                sum(1 for arg in arg_group if kwargs.get(arg) is not None)
                for arg_group in arg_groups
            ]
            invalid_groups = [i for i, count in enumerate(counts) if count != 1]
            if invalid_groups:
                invalid_group_names = [", ".join(arg_groups[i]) for i in invalid_groups]
                raise ValueError(
                    "Exactly one argument in each of the following"
                    " groups must be defined:"
                    f" {', '.join(invalid_group_names)}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def raise_for_status_with_text(response: requests.Response) -> None:
    """Raise an error with the response text."""
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(str(e), response.text) from e


def get_enum_value(enu: Union[enum.Enum, str]) -> str:
    """Get the value of a string enum."""
    if isinstance(enu, enum.Enum):
        return enu.value
    return enu


@functools.lru_cache(maxsize=1)
def log_once(level: int, message: str) -> None:
    _LOGGER.log(level, message)


def _get_message_type(message: Mapping[str, Any]) -> str:
    if not message:
        raise ValueError("Message is empty.")
    if "lc" in message:
        if "id" not in message:
            raise ValueError(
                f"Unexpected format for serialized message: {message}"
                " Message does not have an id."
            )
        return message["id"][-1].replace("Message", "").lower()
    else:
        if "type" not in message:
            raise ValueError(
                f"Unexpected format for stored message: {message}"
                " Message does not have a type."
            )
        return message["type"]


def _get_message_fields(message: Mapping[str, Any]) -> Mapping[str, Any]:
    if not message:
        raise ValueError("Message is empty.")
    if "lc" in message:
        if "kwargs" not in message:
            raise ValueError(
                f"Unexpected format for serialized message: {message}"
                " Message does not have kwargs."
            )
        return message["kwargs"]
    else:
        if "data" not in message:
            raise ValueError(
                f"Unexpected format for stored message: {message}"
                " Message does not have data."
            )
        return message["data"]


def _convert_message(message: Mapping[str, Any]) -> Dict[str, Any]:
    """Extract message from a message object."""
    message_type = _get_message_type(message)
    message_data = _get_message_fields(message)
    return {"type": message_type, "data": message_data}


def get_messages_from_inputs(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    if "messages" in inputs:
        return [_convert_message(message) for message in inputs["messages"]]
    if "message" in inputs:
        return [_convert_message(inputs["message"])]
    raise ValueError(f"Could not find message(s) in run with inputs {inputs}.")


def get_message_generation_from_outputs(outputs: Mapping[str, Any]) -> Dict[str, Any]:
    if "generations" not in outputs:
        raise ValueError(f"No generations found in in run with output: {outputs}.")
    generations = outputs["generations"]
    if len(generations) != 1:
        raise ValueError(
            "Chat examples expect exactly one generation."
            f" Found {len(generations)} generations: {generations}."
        )
    first_generation = generations[0]
    if "message" not in first_generation:
        raise ValueError(
            f"Unexpected format for generation: {first_generation}."
            " Generation does not have a message."
        )
    return _convert_message(first_generation["message"])


def get_prompt_from_inputs(inputs: Mapping[str, Any]) -> str:
    if "prompt" in inputs:
        return inputs["prompt"]
    if "prompts" in inputs:
        prompts = inputs["prompts"]
        if len(prompts) == 1:
            return prompts[0]
        raise ValueError(
            f"Multiple prompts in run with inputs {inputs}."
            " Please create example manually."
        )
    raise ValueError(f"Could not find prompt in run with inputs {inputs}.")


def get_llm_generation_from_outputs(outputs: Mapping[str, Any]) -> str:
    if "generations" not in outputs:
        raise ValueError(f"No generations found in in run with output: {outputs}.")
    generations = outputs["generations"]
    if len(generations) != 1:
        raise ValueError(f"Multiple generations in run: {generations}")
    first_generation = generations[0]
    if "text" not in first_generation:
        raise ValueError(f"No text in generation: {first_generation}")
    return first_generation["text"]


@functools.lru_cache(maxsize=1)
def get_docker_compose_command() -> List[str]:
    """Get the correct docker compose command for this system."""
    try:
        subprocess.check_call(
            ["docker", "compose", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return ["docker", "compose"]
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.check_call(
                ["docker-compose", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return ["docker-compose"]
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ValueError(
                "Neither 'docker compose' nor 'docker-compose'"
                " commands are available. Please install the Docker"
                " server following the instructions for your operating"
                " system at https://docs.docker.com/engine/install/"
            )


def convert_langchain_message(message: ls_schemas.BaseMessageLike) -> dict:
    """Convert a LangChain message to an example."""
    converted: Dict[str, Any] = {
        "type": message.type,
        "data": {"content": message.content},
    }
    # Check for presence of keys in additional_kwargs
    if message.additional_kwargs and len(message.additional_kwargs) > 0:
        converted["data"]["additional_kwargs"] = {**message.additional_kwargs}
    return converted


def is_base_message_like(obj: object) -> bool:
    """
    Check if the given object is similar to BaseMessage.

    Args:
        obj (object): The object to check.

    Returns:
        bool: True if the object is similar to BaseMessage, False otherwise.
    """
    return all(
        [
            isinstance(getattr(obj, "content", None), str),
            isinstance(getattr(obj, "additional_kwargs", None), dict),
            hasattr(obj, "type") and isinstance(getattr(obj, "type"), str),
        ]
    )


def get_tracer_project(return_default_value=True) -> Optional[str]:
    """Get the project name for a LangSmith tracer."""
    return os.environ.get(
        # Hosted LangServe projects get precedence over all other defaults.
        # This is to make sure that we always use the associated project
        # for a hosted langserve deployment even if the customer sets some
        # other project name in their environment.
        "HOSTED_LANGSERVE_PROJECT_NAME",
        os.environ.get(
            "LANGCHAIN_PROJECT",
            os.environ.get(
                # This is the legacy name for a LANGCHAIN_PROJECT, so it
                # has lower precedence than LANGCHAIN_PROJECT
                "LANGCHAIN_SESSION",
                "default" if return_default_value else None,
            ),
        ),
    )


class FilterPoolFullWarning(logging.Filter):
    """Filter urrllib3 warnings logged when the connection pool isn't reused."""

    def filter(self, record) -> bool:
        """urllib3.connectionpool:Connection pool is full, discarding connection: ..."""
        return (
            "Connection pool is full, discarding connection" not in record.getMessage()
        )
