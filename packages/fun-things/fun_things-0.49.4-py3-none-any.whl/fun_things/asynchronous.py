import asyncio
import inspect
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Optional,
    TypeVar,
    Union,
)

T1 = TypeVar("T1")
T2 = TypeVar("T2")


def _subdivide_predicate(value):
    """
    Determines if a value should be subdivided into individual elements.
    
    This is a helper function used by as_asyncgen to decide whether a
    value should be yielded as-is or iterated through.
    
    Args:
        value: The value to check.
        
    Returns:
        bool: True if the value should be subdivided (it's an iterable but not a string or bytes),
              False otherwise.
    """
    if isinstance(value, str):
        return False

    if isinstance(value, bytes):
        return False

    return isinstance(value, Iterable)


async def as_asyncgen(
    value,
    subdivide_predicate: Callable[[Any], bool] = _subdivide_predicate,
):
    """
    Calls a function as an async generator.

    Also awaits async functions.
    """
    if inspect.isasyncgen(value):
        # Already an async generator.
        async for subvalue in value:
            yield subvalue

        return

    if inspect.isawaitable(value):
        value = await value

    if subdivide_predicate(value):
        for subvalue in value:
            yield subvalue

        return

    yield value


async def as_async(
    value: Union[Coroutine[Any, Any, T1], T1],
) -> T1:
    """
    Converts a value to its async equivalent, awaiting it if it's awaitable.
    
    This function is useful for handling both coroutines/awaitables and regular values
    with the same code path.
    
    Args:
        value: Either a coroutine/awaitable object or a regular value.
        
    Returns:
        T1: The result of awaiting the value if it was awaitable, otherwise the value itself.
    
    Examples:
        >>> await as_async(some_coroutine())  # Returns the awaited result
        >>> await as_async(regular_value)     # Returns regular_value unchanged
    """
    if inspect.isawaitable(value):
        value = await value

    return value  # type: ignore


def as_sync(
    value: Union[Coroutine[Any, Any, T1], T1],
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> T1:
    """
    Converts an async value to its synchronous equivalent.
    
    This function makes it possible to use async functions in a synchronous context
    by running them to completion on an event loop.
    
    Args:
        value: Either a coroutine/awaitable object or a regular value.
        loop: An optional event loop to use. If None, a new event loop will be created.
        
    Returns:
        T1: The result of running the coroutine to completion if value was awaitable,
            otherwise the value itself.
    
    Examples:
        >>> as_sync(some_coroutine())  # Runs the coroutine and returns its result
        >>> as_sync(regular_value)     # Returns regular_value unchanged
    """
    if inspect.isawaitable(value):
        loop = loop or asyncio.new_event_loop()

        return loop.run_until_complete(value)

    return value


def as_gen(
    value: Union[
        Generator[T1, T2, Any],
        AsyncGenerator[T1, T2],
        Awaitable[T1],
        T1,
    ],
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Generator[T1, T2, Any]:
    """
    Converts a function into a `Generator`.
    """
    loop = loop or asyncio.new_event_loop()

    if inspect.isawaitable(value):
        value = loop.run_until_complete(value)

    if inspect.isgenerator(value):
        for subvalue in value:
            yield subvalue

        return

    if inspect.isasyncgen(value):
        while True:
            try:
                yield loop.run_until_complete(value.__anext__())

            except StopAsyncIteration:
                return

    yield value  # type: ignore
