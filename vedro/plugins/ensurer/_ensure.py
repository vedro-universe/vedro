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

LoggerType = Callable[[Callable[..., Any], AttemptType, Union[BaseException, None]], Any]


class Ensure:
    """
    Provides functionality to ensure a function succeeds within a specified number of attempts.

    This class retries a given function or coroutine function a specified number of times,
    optionally with a delay between attempts, and can log each attempt.
    """

    def __init__(self, *, attempts: AttemptType = 3,
                 delay: DelayType = 0.0,
                 swallow: SwallowExceptionType = BaseException,
                 logger: Optional[LoggerType] = None) -> None:
        """
        Initialize the Ensure instance with retry configurations.

        :param attempts: The number of attempts to try executing the function. Default is 3.
        :param delay: The delay between attempts. Can be a fixed value or a callable
            returning a value.
        :param swallow: The exception(s) to be caught and retried. Default is BaseException.
        :param logger: An optional logging callable to log each attempt. Default is None.
        """
        self._attempts = attempts
        self._delay = delay
        self._swallow = swallow
        self._logger = logger

    @overload
    def __call__(self, fn: F) -> F:
        """
        Apply the Ensure decorator to a synchronous function.

        :param fn: The synchronous function to be decorated.
        :return: The decorated function.
        """
        ...  # pragma: no cover

    @overload
    def __call__(self, fn: AF) -> AF:
        """
        Apply the Ensure decorator to an asynchronous function.

        :param fn: The asynchronous function to be decorated.
        :return: The decorated coroutine function.
        """
        ...  # pragma: no cover

    def __call__(self, fn: Any) -> Any:
        """
        Determine whether the function is async or async and apply the appropriate wrapper.

        :param fn: The function to be decorated.
        :return: The decorated function or coroutine function.
        """
        if asyncio.iscoroutinefunction(fn):
            return self._async_wrapper(fn)
        else:
            return self._sync_wrapper(fn)

    def _sync_wrapper(self, fn: F) -> F:
        """
        Wrap a synchronous function with retry logic.

        :param fn: The synchronous function to be wrapped.
        :return: The wrapped function with retry logic.
        """
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
            if exception:  # pragma: no branch
                raise exception

        return cast(F, sync_wrapper)

    def _async_wrapper(self, fn: AF) -> AF:
        """
        Wrap an asynchronous function with retry logic.

        :param fn: The asynchronous function to be wrapped.
        :return: The wrapped coroutine function with retry logic.
        """
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
            if exception:  # pragma: no branch
                raise exception

        return cast(AF, async_wrapper)

    def __repr__(self) -> str:
        """
        Return a string representation of the Ensure instance.

        :return: A string representation of the Ensure instance with its configurations.
        """
        return (f"{self.__class__.__name__}"
                f"(attempts={self._attempts}, delay={self._delay!r}, swallow={self._swallow!r})")
