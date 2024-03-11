import asyncio
import time
from functools import wraps
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar, Union, overload

__all__ = ("ensure",)

# Type variable for the function being decorated
F = TypeVar("F", bound=Callable[..., Any])
# Type variable for coroutine functions
AF = TypeVar("AF", bound=Callable[..., Coroutine[Any, Any, Any]])

DelayValue = Union[float, int]
DelayCallable = Callable[[], DelayValue]

ExceptionType = Type[BaseException]
SwallowException = Union[Tuple[ExceptionType, ...], ExceptionType]


class ensure:
    def __init__(self, *, attempts: Optional[int] = None,
                 delay: Optional[Union[DelayValue, DelayCallable]] = None,
                 swallow: Optional[SwallowException] = None) -> None:
        self.attempts = attempts or 3
        self.delay = delay or 0.0
        self._swallow = (BaseException,) if (swallow is None) else swallow

    @overload
    def __call__(self, fn: F) -> F:
        ...

    @overload
    def __call__(self, fn: AF) -> AF:
        ...

    def __call__(self, fn:  Any) -> Any:
        if asyncio.iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                exception = None
                for attempt in range(self.attempts):
                    try:
                        return await fn(*args, **kwargs)
                    except self._swallow as e:
                        exception = e
                        delay = self.delay() if callable(self.delay) else self.delay
                        await asyncio.sleep(delay)
                if exception:
                    raise exception

            return async_wrapper
        else:
            @wraps(fn)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                exception = None
                for attempt in range(self.attempts):
                    try:
                        return fn(*args, **kwargs)
                    except self._swallow as e:
                        exception = e
                        delay = self.delay() if callable(self.delay) else self.delay
                        time.sleep(delay)
                if exception:
                    raise exception

            return sync_wrapper
