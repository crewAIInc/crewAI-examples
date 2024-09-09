"""Decorator for creating a run tree from functions."""
from __future__ import annotations

import contextlib
import contextvars
import functools
import inspect
import logging
import traceback
import uuid
from concurrent import futures
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from langsmith import client, run_trees, utils

if TYPE_CHECKING:
    from langchain.schema.runnable import Runnable

logger = logging.getLogger(__name__)
_PARENT_RUN_TREE = contextvars.ContextVar[Optional[run_trees.RunTree]](
    "_PARENT_RUN_TREE", default=None
)
_PROJECT_NAME = contextvars.ContextVar[Optional[str]]("_PROJECT_NAME", default=None)
_TAGS = contextvars.ContextVar[Optional[List[str]]]("_TAGS", default=None)
_METADATA = contextvars.ContextVar[Optional[Dict[str, Any]]]("_METADATA", default=None)


def get_run_tree_context() -> Optional[run_trees.RunTree]:
    """Get the current run tree context."""
    return _PARENT_RUN_TREE.get()


def _is_traceable_function(func: Callable) -> bool:
    return getattr(func, "__langsmith_traceable__", False)


def is_traceable_function(func: Callable) -> bool:
    """Check if a function is @traceable decorated."""
    return (
        _is_traceable_function(func)
        or (isinstance(func, functools.partial) and _is_traceable_function(func.func))
        or (hasattr(func, "__call__") and _is_traceable_function(func.__call__))
    )


def is_async(func: Callable) -> bool:
    """Inspect function or wrapped function to see if it is async."""
    return inspect.iscoroutinefunction(func) or (
        hasattr(func, "__wrapped__") and inspect.iscoroutinefunction(func.__wrapped__)
    )


def _get_inputs(
    signature: inspect.Signature, *args: Any, **kwargs: Any
) -> Dict[str, Any]:
    """Return a dictionary of inputs from the function signature."""
    bound = signature.bind_partial(*args, **kwargs)
    bound.apply_defaults()
    arguments = dict(bound.arguments)
    arguments.pop("self", None)
    arguments.pop("cls", None)
    for param_name, param in signature.parameters.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # Update with the **kwargs, and remove the original entry
            # This is to help flatten out keyword arguments
            if param_name in arguments:
                arguments.update(arguments[param_name])
                arguments.pop(param_name)

    return arguments


class LangSmithExtra(TypedDict, total=False):
    """Any additional info to be injected into the run dynamically."""

    reference_example_id: Optional[client.ID_TYPE]
    run_extra: Optional[Dict]
    run_tree: Optional[run_trees.RunTree]
    project_name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    run_id: Optional[client.ID_TYPE]
    client: Optional[client.Client]


class _TraceableContainer(TypedDict, total=False):
    """Typed response when initializing a run a traceable."""

    new_run: Optional[run_trees.RunTree]
    project_name: Optional[str]
    outer_project: Optional[str]
    outer_metadata: Optional[Dict[str, Any]]
    outer_tags: Optional[List[str]]


def _container_end(
    container: _TraceableContainer,
    outputs: Optional[Any] = None,
    error: Optional[str] = None,
):
    """End the run."""
    run_tree = container.get("new_run")
    if run_tree is None:
        # Tracing disabled
        return
    outputs_ = outputs if isinstance(outputs, dict) else {"output": outputs}
    run_tree.end(outputs=outputs_, error=error)
    run_tree.patch()


def _collect_extra(extra_outer: dict, langsmith_extra: LangSmithExtra) -> dict:
    run_extra = langsmith_extra.get("run_extra", None)
    if run_extra:
        extra_inner = {**extra_outer, **run_extra}
    else:
        extra_inner = extra_outer
    return extra_inner


def _setup_run(
    func: Callable,
    run_type: str,
    extra_outer: dict,
    langsmith_extra: Optional[LangSmithExtra] = None,
    name: Optional[str] = None,
    executor: Optional[futures.ThreadPoolExecutor] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    tags: Optional[List[str]] = None,
    client: Optional[client.Client] = None,
    args: Any = None,
    kwargs: Any = None,
) -> _TraceableContainer:
    outer_project = _PROJECT_NAME.get() or utils.get_tracer_project()
    langsmith_extra = langsmith_extra or LangSmithExtra()
    parent_run_ = langsmith_extra.get("run_tree") or _PARENT_RUN_TREE.get()
    if not parent_run_ and not utils.tracing_is_enabled():
        utils.log_once(
            logging.DEBUG, "LangSmith tracing is disabled, returning original function."
        )
        return _TraceableContainer(
            new_run=None,
            project_name=outer_project,
            outer_project=outer_project,
            outer_metadata=None,
            outer_tags=None,
        )
    # Else either the env var is set OR a parent run was explicitly set,
    # which occurs in the `as_runnable()` flow
    project_name_ = langsmith_extra.get("project_name", outer_project)
    signature = inspect.signature(func)
    name_ = name or func.__name__
    docstring = func.__doc__
    extra_inner = _collect_extra(extra_outer, langsmith_extra)
    outer_metadata = _METADATA.get()
    metadata_ = {
        **(langsmith_extra.get("metadata") or {}),
        **(outer_metadata or {}),
    }
    _METADATA.set(metadata_)
    metadata_.update(metadata or {})
    metadata_["ls_method"] = "traceable"
    extra_inner["metadata"] = metadata_
    try:
        inputs = _get_inputs(signature, *args, **kwargs)
    except TypeError as e:
        logger.debug(f"Failed to infer inputs for {name_}: {e}")
        inputs = {"args": args, "kwargs": kwargs}
    outer_tags = _TAGS.get()
    tags_ = (langsmith_extra.get("tags") or []) + (outer_tags or [])
    _TAGS.set(tags_)
    tags_ += tags or []
    id_ = langsmith_extra.get("run_id", uuid.uuid4())
    client_ = langsmith_extra.get("client", client)
    if parent_run_ is not None:
        new_run = parent_run_.create_child(
            name=name_,
            run_type=run_type,
            serialized={
                "name": name,
                "signature": str(signature),
                "doc": docstring,
            },
            inputs=inputs,
            tags=tags_,
            extra=extra_inner,
            run_id=id_,
        )
    else:
        new_run = run_trees.RunTree(
            id=id_,
            name=name_,
            serialized={
                "name": name,
                "signature": str(signature),
                "doc": docstring,
            },
            inputs=inputs,
            run_type=run_type,
            reference_example_id=langsmith_extra.get("reference_example_id"),
            project_name=project_name_,
            extra=extra_inner,
            tags=tags_,
            executor=executor,
            client=client_,
        )

    new_run.post()
    response_container = _TraceableContainer(
        new_run=new_run,
        project_name=project_name_,
        outer_project=outer_project,
        outer_metadata=outer_metadata,
        outer_tags=outer_tags,
    )
    _PROJECT_NAME.set(response_container["project_name"])
    _PARENT_RUN_TREE.set(response_container["new_run"])
    return response_container


R = TypeVar("R", covariant=True)


@runtime_checkable
class SupportsLangsmithExtra(Protocol, Generic[R]):
    def __call__(
        self,
        *args: Any,
        langsmith_extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> R:
        ...


@overload
def traceable(
    func: Callable[..., R],
) -> Callable[..., R]:
    ...


@overload
def traceable(
    run_type: str = "chain",
    *,
    name: Optional[str] = None,
    executor: Optional[futures.ThreadPoolExecutor] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    tags: Optional[List[str]] = None,
    client: Optional[client.Client] = None,
    extra: Optional[Dict] = None,
    reduce_fn: Optional[Callable] = None,
) -> Callable[[Callable[..., R]], SupportsLangsmithExtra[R]]:
    ...


def traceable(
    *args: Any,
    **kwargs: Any,
) -> Union[Callable, Callable[[Callable], Callable]]:
    """Decorator for creating or adding a run to a run tree.

    Args:
        run_type: The type of run to create. Examples: llm, chain, tool, prompt,
            retriever, etc. Defaults to "chain".
        name: The name of the run. Defaults to the function name.
        executor: The thread pool executor to use for the run. Defaults to None,
            which will use the default executor.
        metadata: The metadata to add to the run. Defaults to None.
        tags: The tags to add to the run. Defaults to None.
        client: The client to use for logging the run to LangSmith. Defaults to
            None, which will use the default client.
        reduce_fn: A function to reduce the output of the function if the function
            returns a generator. Defaults to None, which means the values will be
                logged as a list. Note: if the iterator is never exhausted (e.g.
                the function returns an infinite generator), this will never be
                called, and the run itself will be stuck in a pending state.

    """
    run_type = (
        args[0]
        if args and isinstance(args[0], str)
        else (kwargs.get("run_type") or "chain")
    )
    extra_outer = kwargs.get("extra") or {}
    name = kwargs.get("name")
    executor = kwargs.get("executor")
    metadata = kwargs.get("metadata")
    tags = kwargs.get("tags")
    client = kwargs.get("client")
    reduce_fn = kwargs.get("reduce_fn")

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(
            *args: Any,
            langsmith_extra: Optional[LangSmithExtra] = None,
            **kwargs: Any,
        ) -> Any:
            """Async version of wrapper function"""
            context_run = _PARENT_RUN_TREE.get()
            run_container = _setup_run(
                func,
                run_type=run_type,
                langsmith_extra=langsmith_extra,
                extra_outer=extra_outer,
                name=name,
                executor=executor,
                metadata=metadata,
                tags=tags,
                client=client,
                args=args,
                kwargs=kwargs,
            )
            func_accepts_parent_run = (
                inspect.signature(func).parameters.get("run_tree", None) is not None
            )
            try:
                if func_accepts_parent_run:
                    function_result = await func(
                        *args, run_tree=run_container["new_run"], **kwargs
                    )
                else:
                    function_result = await func(*args, **kwargs)
            except Exception as e:
                stacktrace = traceback.format_exc()
                _container_end(run_container, error=stacktrace)
                raise e
            finally:
                _PARENT_RUN_TREE.set(context_run)
                _PROJECT_NAME.set(run_container["outer_project"])
                _TAGS.set(run_container["outer_tags"])
                _METADATA.set(run_container["outer_metadata"])
            _container_end(run_container, outputs=function_result)
            return function_result

        @functools.wraps(func)
        async def async_generator_wrapper(
            *args: Any, langsmith_extra: Optional[LangSmithExtra] = None, **kwargs: Any
        ) -> AsyncGenerator:
            context_run = _PARENT_RUN_TREE.get()
            run_container = _setup_run(
                func,
                run_type=run_type,
                langsmith_extra=langsmith_extra,
                extra_outer=extra_outer,
                name=name,
                executor=executor,
                metadata=metadata,
                tags=tags,
                client=client,
                args=args,
                kwargs=kwargs,
            )
            func_accepts_parent_run = (
                inspect.signature(func).parameters.get("run_tree", None) is not None
            )
            results: List[Any] = []
            try:
                if func_accepts_parent_run:
                    async_gen_result = func(
                        *args, run_tree=run_container["new_run"], **kwargs
                    )
                else:
                    # TODO: Nesting is ambiguous if a nested traceable function is only
                    # called mid-generation. Need to explicitly accept run_tree to get
                    # around this.
                    async_gen_result = func(*args, **kwargs)
                _PARENT_RUN_TREE.set(context_run)
                _PROJECT_NAME.set(run_container["outer_project"])
                _TAGS.set(run_container["outer_tags"])
                _METADATA.set(run_container["outer_metadata"])
                # Can't iterate through if it's a coroutine
                if inspect.iscoroutine(async_gen_result):
                    async_gen_result = await async_gen_result
                async for item in async_gen_result:
                    results.append(item)
                    yield item
            except BaseException as e:
                stacktrace = traceback.format_exc()
                _container_end(run_container, error=stacktrace)
                raise e
            finally:
                _PARENT_RUN_TREE.set(context_run)
                _PROJECT_NAME.set(run_container["outer_project"])
                _TAGS.set(run_container["outer_tags"])
                _METADATA.set(run_container["outer_metadata"])
            if results:
                if reduce_fn:
                    try:
                        function_result = reduce_fn(results)
                    except Exception as e:
                        logger.error(e)
                        function_result = results
                else:
                    function_result = results
            else:
                function_result = None
            _container_end(run_container, outputs=function_result)

        @functools.wraps(func)
        def wrapper(
            *args: Any,
            langsmith_extra: Optional[LangSmithExtra] = None,
            **kwargs: Any,
        ) -> Any:
            """Create a new run or create_child() if run is passed in kwargs."""
            context_run = _PARENT_RUN_TREE.get()
            run_container = _setup_run(
                func,
                run_type=run_type,
                langsmith_extra=langsmith_extra,
                extra_outer=extra_outer,
                name=name,
                executor=executor,
                metadata=metadata,
                tags=tags,
                client=client,
                args=args,
                kwargs=kwargs,
            )
            func_accepts_parent_run = (
                inspect.signature(func).parameters.get("run_tree", None) is not None
            )
            try:
                if func_accepts_parent_run:
                    function_result = func(
                        *args, run_tree=run_container["new_run"], **kwargs
                    )
                else:
                    function_result = func(*args, **kwargs)
            except BaseException as e:
                stacktrace = traceback.format_exc()
                _container_end(run_container, error=stacktrace)
                raise e
            finally:
                _PARENT_RUN_TREE.set(context_run)
                _PROJECT_NAME.set(run_container["outer_project"])
                _TAGS.set(run_container["outer_tags"])
                _METADATA.set(run_container["outer_metadata"])
            _container_end(run_container, outputs=function_result)
            return function_result

        @functools.wraps(func)
        def generator_wrapper(
            *args: Any, langsmith_extra: Optional[LangSmithExtra] = None, **kwargs: Any
        ) -> Any:
            context_run = _PARENT_RUN_TREE.get()
            run_container = _setup_run(
                func,
                run_type=run_type,
                langsmith_extra=langsmith_extra,
                extra_outer=extra_outer,
                name=name,
                executor=executor,
                metadata=metadata,
                tags=tags,
                client=client,
                args=args,
                kwargs=kwargs,
            )

            func_accepts_parent_run = (
                inspect.signature(func).parameters.get("run_tree", None) is not None
            )
            results: List[Any] = []
            try:
                if func_accepts_parent_run:
                    generator_result = func(
                        *args, run_tree=run_container["new_run"], **kwargs
                    )
                else:
                    # TODO: Nesting is ambiguous if a nested traceable function is only
                    # called mid-generation. Need to explicitly accept run_tree to get
                    # around this.
                    generator_result = func(*args, **kwargs)
                for item in generator_result:
                    results.append(item)
                    yield item
            except BaseException as e:
                stacktrace = traceback.format_exc()
                _container_end(run_container, error=stacktrace)
                raise e
            finally:
                _PARENT_RUN_TREE.set(context_run)
                _PROJECT_NAME.set(run_container["outer_project"])
                _TAGS.set(run_container["outer_tags"])
                _METADATA.set(run_container["outer_metadata"])
            if results:
                if reduce_fn:
                    try:
                        function_result = reduce_fn(results)
                    except Exception as e:
                        logger.error(e)
                        function_result = results
                else:
                    function_result = results
            else:
                function_result = None
            _container_end(run_container, outputs=function_result)

        if inspect.isasyncgenfunction(func):
            selected_wrapper: Callable = async_generator_wrapper
        elif is_async(func):
            if reduce_fn:
                selected_wrapper = async_generator_wrapper
            else:
                selected_wrapper = async_wrapper
        elif reduce_fn or inspect.isgeneratorfunction(func):
            selected_wrapper = generator_wrapper
        else:
            selected_wrapper = wrapper
        setattr(selected_wrapper, "__langsmith_traceable__", True)
        return selected_wrapper

    # If the decorator is called with no arguments, then it's being used as a
    # decorator, so we return the decorator function
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorator(args[0])
    # Else it's being used as a decorator factory, so we return the decorator
    return decorator


@contextlib.contextmanager
def trace(
    name: str,
    run_type: str,
    *,
    inputs: Optional[Dict] = None,
    extra: Optional[Dict] = None,
    executor: Optional[futures.ThreadPoolExecutor] = None,
    project_name: Optional[str] = None,
    run_tree: Optional[run_trees.RunTree] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Generator[run_trees.RunTree, None, None]:
    """Context manager for creating a run tree."""
    outer_tags = _TAGS.get()
    outer_metadata = _METADATA.get()
    outer_project = _PROJECT_NAME.get() or utils.get_tracer_project()
    parent_run_ = _PARENT_RUN_TREE.get() if run_tree is None else run_tree

    # Merge and set context varaibles
    tags_ = sorted(set((tags or []) + (outer_tags or [])))
    _TAGS.set(tags_)
    metadata = {**(metadata or {}), **(outer_metadata or {}), "ls_method": "trace"}
    _METADATA.set(metadata)

    extra_outer = extra or {}
    extra_outer["metadata"] = metadata

    project_name_ = project_name or outer_project
    if parent_run_ is not None:
        new_run = parent_run_.create_child(
            name=name,
            run_type=run_type,
            extra=extra_outer,
            inputs=inputs,
            tags=tags_,
        )
    else:
        new_run = run_trees.RunTree(
            name=name,
            run_type=run_type,
            extra=extra_outer,
            executor=executor,
            project_name=project_name_,
            inputs=inputs or {},
            tags=tags_,
        )
    new_run.post()
    _PARENT_RUN_TREE.set(new_run)
    _PROJECT_NAME.set(project_name_)
    try:
        yield new_run
    except (Exception, KeyboardInterrupt, BaseException) as e:
        tb = traceback.format_exc()
        new_run.end(error=tb)
        new_run.patch()
        raise e
    finally:
        _PARENT_RUN_TREE.set(parent_run_)
        _PROJECT_NAME.set(outer_project)
        _TAGS.set(outer_tags)
        _METADATA.set(outer_metadata)
    if new_run.end_time is None:
        # User didn't call end() on the run, so we'll do it for them
        new_run.end()
    new_run.patch()


def as_runnable(traceable_fn: Callable) -> Runnable:
    try:
        from langchain.callbacks.manager import (
            AsyncCallbackManager,
            CallbackManager,
        )
        from langchain.callbacks.tracers.langchain import LangChainTracer
        from langchain.schema.runnable import RunnableConfig, RunnableLambda
        from langchain.schema.runnable.utils import Input, Output
    except ImportError as e:
        raise ImportError(
            "as_runnable requires langchain to be installed. "
            "You can install it with `pip install langchain`."
        ) from e
    if not is_traceable_function(traceable_fn):
        try:
            fn_src = inspect.getsource(traceable_fn)
        except Exception:
            fn_src = "<source unavailable>"
        raise ValueError(
            f"as_runnable expects a function wrapped by the LangSmith"
            f" @traceable decorator. Got {traceable_fn} defined as:\n{fn_src}"
        )

    class RunnableTraceable(RunnableLambda):
        """RunnableTraceable converts a @traceable decorated function
        to a Runnable in a way that hands off the LangSmith tracing context.
        """

        def __init__(
            self,
            func: Callable,
            afunc: Optional[Callable[..., Awaitable[Output]]] = None,
        ) -> None:
            wrapped: Optional[Callable[[Input], Output]] = None
            awrapped = self._wrap_async(afunc)
            if is_async(func):
                if awrapped is not None:
                    raise TypeError(
                        "Func was provided as a coroutine function, but afunc was "
                        "also provided. If providing both, func should be a regular "
                        "function to avoid ambiguity."
                    )
                wrapped = cast(Callable[[Input], Output], self._wrap_async(func))
            elif is_traceable_function(func):
                wrapped = cast(Callable[[Input], Output], self._wrap_sync(func))
            if wrapped is None:
                raise ValueError(
                    f"{self.__class__.__name__} expects a function wrapped by"
                    " the LangSmith"
                    f" @traceable decorator. Got {func}"
                )

            super().__init__(
                wrapped,
                cast(
                    Optional[Callable[[Input], Awaitable[Output]]],
                    awrapped,
                ),
            )

        @staticmethod
        def _configure_run_tree(callback_manager: Any) -> Optional[run_trees.RunTree]:
            run_tree: Optional[run_trees.RunTree] = None
            if isinstance(callback_manager, (CallbackManager, AsyncCallbackManager)):
                lc_tracers = [
                    handler
                    for handler in callback_manager.handlers
                    if isinstance(handler, LangChainTracer)
                ]
                if lc_tracers:
                    lc_tracer = lc_tracers[0]
                    run_tree = run_trees.RunTree(
                        id=callback_manager.parent_run_id,
                        session_name=lc_tracer.project_name,
                        name="Wrapping",
                        run_type="chain",
                        inputs={},
                        tags=callback_manager.tags,
                        extra={"metadata": callback_manager.metadata},
                    )
            return run_tree

        @staticmethod
        def _wrap_sync(
            func: Callable[..., Output],
        ) -> Callable[[Input, RunnableConfig], Output]:
            """Wrap a synchronous function to make it asynchronous."""

            def wrap_traceable(inputs: dict, config: RunnableConfig) -> Any:
                run_tree = RunnableTraceable._configure_run_tree(
                    config.get("callbacks")
                )
                return func(**inputs, langsmith_extra={"run_tree": run_tree})

            return cast(Callable[[Input, RunnableConfig], Output], wrap_traceable)

        @staticmethod
        def _wrap_async(
            afunc: Optional[Callable[..., Awaitable[Output]]],
        ) -> Optional[Callable[[Input, RunnableConfig], Awaitable[Output]]]:
            """Wrap an async function to make it synchronous."""

            if afunc is None:
                return None

            if not is_traceable_function(afunc):
                raise ValueError(
                    "RunnableTraceable expects a function wrapped by the LangSmith"
                    f" @traceable decorator. Got {afunc}"
                )
            afunc_ = cast(Callable[..., Awaitable[Output]], afunc)

            async def awrap_traceable(inputs: dict, config: RunnableConfig) -> Any:
                run_tree = RunnableTraceable._configure_run_tree(
                    config.get("callbacks")
                )
                return await afunc_(**inputs, langsmith_extra={"run_tree": run_tree})

            return cast(
                Callable[[Input, RunnableConfig], Awaitable[Output]], awrap_traceable
            )

    return RunnableTraceable(traceable_fn)
