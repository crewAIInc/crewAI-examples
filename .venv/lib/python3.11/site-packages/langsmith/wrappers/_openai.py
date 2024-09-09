from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable, List, TypeVar, Union

from langsmith import run_helpers

if TYPE_CHECKING:
    from openai import AsyncOpenAI, OpenAI
    from openai.types.chat.chat_completion_chunk import (
        ChatCompletionChunk,
    )
    from openai.types.completion import Completion

C = TypeVar("C", bound=Union["OpenAI", "AsyncOpenAI"])


def _reduce_chat(all_chunks: List[ChatCompletionChunk]) -> dict:
    all_content = []
    for chunk in all_chunks:
        content = chunk.choices[0].delta.content
        if content is not None:
            all_content.append(content)
    content = "".join(all_content)
    if all_chunks:
        d = all_chunks[-1].model_dump()
        d["choices"] = [{"message": {"role": "assistant", "content": content}}]
    else:
        d = {"choices": [{"message": {"role": "assistant", "content": content}}]}

    return d


def _reduce_completions(all_chunks: List[Completion]) -> dict:
    all_content = []
    for chunk in all_chunks:
        content = chunk.choices[0].text
        if content is not None:
            all_content.append(content)
    content = "".join(all_content)
    if all_chunks:
        d = all_chunks[-1].model_dump()
        d["choices"] = [{"text": content}]
    else:
        d = {"choices": [{"text": content}]}

    return d


def _get_wrapper(original_create: Callable, name: str, reduce_fn: Callable) -> Callable:
    @functools.wraps(original_create)
    def create(*args, stream: bool = False, **kwargs):
        decorator = run_helpers.traceable(
            name=name, run_type="llm", reduce_fn=reduce_fn if stream else None
        )

        return decorator(original_create)(*args, stream=stream, **kwargs)

    @functools.wraps(original_create)
    async def acreate(*args, stream: bool = False, **kwargs):
        decorator = run_helpers.traceable(
            name=name, run_type="llm", reduce_fn=reduce_fn if stream else None
        )
        if stream:
            # TODO: This slightly alters the output to be a generator instead of the
            # stream object. We can probably fix this with a bit of simple changes
            res = decorator(original_create)(*args, stream=stream, **kwargs)
            return res
        return await decorator(original_create)(*args, stream=stream, **kwargs)

    return acreate if run_helpers.is_async(original_create) else create


def wrap_openai(client: C) -> C:
    """Patch the OpenAI client to make it traceable.

    Args:
        client (Union[OpenAI, AsyncOpenAI]): The client to patch.

    Returns:
        Union[OpenAI, AsyncOpenAI]: The patched client.

    """
    client.chat.completions.create = _get_wrapper(  # type: ignore[method-assign]
        client.chat.completions.create, "ChatOpenAI", _reduce_chat
    )
    client.completions.create = _get_wrapper(  # type: ignore[method-assign]
        client.completions.create, "OpenAI", _reduce_completions
    )
    return client
