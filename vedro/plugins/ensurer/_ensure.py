import asyncio
import time
from functools import wraps
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar, Union, cast, overload

__all__ = ("Ensure", "AttemptType", "DelayValueType", "DelayCallableType", "DelayType",
           "ExceptionType", "SwallowExceptionType", "LoggerType",)

F = TypeVar("F", bound=Callable[..., Any])
AF = TypeVar("AF", bound=Callable[..., Coroutine[Any, Any, Any]])

AttemptType = int
DelayValueType = Union[float, int]
DelayCallableType = Callable[[AttemptType], DelayValueType]
DelayType = Union[DelayValueType, DelayCallableType]

ExceptionType = Type[BaseException]
SwallowExceptionType = Union[Tuple[ExceptionType, ...], ExceptionType]

LoggerType = Callable[[Any, AttemptType, Union[BaseException, None]], Any]


class Ensure:
    def __init__(self, *, attempts: AttemptType = 3,
                 delay: DelayType = 0.0,
                 swallow: SwallowExceptionType = BaseException,
                 logger: Optional[LoggerType] = None) -> None:
        self._attempts = attempts
        self._delay = delay
        self._swallow = swallow
        self._logger = logger

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
            for attempt in range(1, self._attempts + 1):
                try:
                    res = fn(*args, **kwargs)
                    if self._logger and attempt > 1:
                        self._logger(fn, attempt, None)
                    return res
                except self._swallow as e:
                    exception = e
                    delay = self._delay(attempt) if callable(self._delay) else self._delay
                    if self._logger and self._attempts > 1:
                        self._logger(fn, attempt, e)
                    time.sleep(delay)
            if exception:
                raise exception

        return cast(F, sync_wrapper)

    def _async_wrapper(self, fn: AF) -> AF:
        @wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            exception = None
            for attempt in range(1, self._attempts + 1):
                try:
                    res = await fn(*args, **kwargs)
                    if self._logger and attempt > 1:
                        self._logger(fn, attempt, None)
                    return res
                except self._swallow as e:
                    exception = e
                    delay = self._delay(attempt) if callable(self._delay) else self._delay
                    if self._logger and self._attempts > 1:
                        self._logger(fn, attempt, e)
                    await asyncio.sleep(delay)
            if exception:
                raise exception

        return cast(AF, async_wrapper)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(attempts={self._attempts}, delay={self._delay!r}, swallow={self._swallow!r})")
