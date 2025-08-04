import traceback
from dataclasses import dataclass
from time import sleep
from typing import Awaitable, Callable, Generic, TypeVar, Union, cast

from .retry_response import RetryResponse

T = TypeVar("T")


@dataclass(frozen=True)
class AsyncRetry(Generic[T]):
    """
    Allows a callable to be called again if it throws an error.
    """

    callable: Callable[..., Awaitable[T]] = None  # type: ignore
    error_handler: Callable[["Retry", Exception, int], Awaitable[bool]] = None  # type: ignore
    """
    If the return value is `False`,
    it will stop retrying.
    """
    retry_handler: Callable[["Retry", T, int], Awaitable[bool]] = None  # type: ignore
    """
    If return value is `True`,
    it will retry the `callable`.
    """
    retry_count: int = 3
    intermission: Union[float, Callable[["AsyncRetry"], Awaitable[float]]] = 0
    """
    Sleep time between each retry.
    
    In seconds.
    """
    log: bool = True

    async def __call__(self, *args, **kwargs):
        return await self.run(*args, **kwargs)

    async def run(self, *args, **kwargs):
        max_attempts_count = self.retry_count + 1

        for i in range(1, max_attempts_count):
            if i > 1:
                if self.log:
                    print(f"({i}/{self.retry_count}) Retrying...")

                intermission: float = 0

                if isinstance(self.intermission, Callable):
                    intermission = await self.intermission(self)

                else:
                    intermission = self.intermission

                if intermission > 0:
                    sleep(intermission)

            try:
                result = await self.callable(*args, **kwargs)

                if self.retry_handler is not None:
                    if await self.retry_handler(
                        self,
                        result,
                        i,
                    ):
                        continue

                return RetryResponse(
                    value=result,
                    ok=True,
                    error=None,  # type: ignore
                    attempts=i,
                    max_attempts_count=max_attempts_count,
                )

            except Exception as e:
                if self.log:
                    print(traceback.format_exc())

                ok = True

                if self.error_handler is not None:
                    ok = await self.error_handler(self, e, i)

                if not ok:
                    return RetryResponse(
                        value=cast(T, None),
                        ok=False,
                        error=e,
                        attempts=i,
                        max_attempts_count=max_attempts_count,
                    )

        if self.log:
            print(
                f"Failed after retrying {self.retry_count} time(s)!",
            )

        return RetryResponse(
            value=cast(T, None),
            ok=False,
            error=None,  # type: ignore
            attempts=self.retry_count + 1,
            max_attempts_count=max_attempts_count,
        )
