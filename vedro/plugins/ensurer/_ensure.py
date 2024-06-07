import asyncio
import time
from functools import wraps
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar, Union, cast, overload

__all__ = ("ensure",)

# Type variable for the function being decorated
F = TypeVar("F", bound=Callable[..., Any])
# Type variable for coroutine functions
AF = TypeVar("AF", bound=Callable[..., Coroutine[Any, Any, Any]])

DelayValue = Union[float, int]
DelayCallable = Callable[[int], DelayValue]

ExceptionType = Type[BaseException]
SwallowException = Union[Tuple[ExceptionType, ...], ExceptionType]


class ensure:
    def __init__(self, *, attempts: Optional[int] = None,
                 delay: Optional[Union[DelayValue, DelayCallable]] = None,
                 swallow: Optional[SwallowException] = None) -> None:
        self._attempts = attempts or 3
        self._delay = delay or 0.0
        self._swallow = (BaseException,) if (swallow is None) else swallow

    @overload
    def __call__(self, fn: F) -> F:
        ...

    @overload
    def __call__(self, fn: AF) -> AF:
        ...

    def __call__(self, fn: Any) -> Any:
        if asyncio.iscoroutinefunction(fn):
            return self._async_wrapper(fn)
        else:
            return self._sync_wrapper(fn)

    def _sync_wrapper(self, fn: F) -> F:
        @wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            exception = None
            for attempt in range(self._attempts):
                try:
                    return fn(*args, **kwargs)
                except self._swallow as e:
                    exception = e
                    delay = self._delay(attempt) if callable(self._delay) else self._delay
                    time.sleep(delay)
            if exception:
                raise exception

        return cast(F, sync_wrapper)

    def _async_wrapper(self, fn: AF) -> AF:
        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            exception = None
            for attempt in range(self._attempts):
                try:
                    return await fn(*args, **kwargs)
                except self._swallow as e:
                    exception = e
                    delay = self._delay(attempt) if callable(self._delay) else self._delay
                    await asyncio.sleep(delay)
            if exception:
                raise exception

        return cast(AF, async_wrapper)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(attempts={self._attempts}, delay={self._delay!r}, swallow={self._swallow!r})")
