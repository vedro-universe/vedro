import sys
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Union, cast

__all__ = ("effect",)


if sys.version_info >= (3, 10):
    from typing import Coroutine, ParamSpec, overload

    P = ParamSpec("P")

    T = ParamSpec("T")
    AsyncCallable = Callable[T, Coroutine[Any, Any, bool]]
    SyncCallable = Callable[T, bool]

    @overload
    def effect(fn: AsyncCallable[P]) -> AsyncCallable[P]: ...

    @overload
    def effect(fn: SyncCallable[P]) -> SyncCallable[P]: ...

    def effect(
        fn: Union[AsyncCallable[P], SyncCallable[P]]
    ) -> Union[AsyncCallable[P], SyncCallable[P]]:
        if iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
                result = await fn(*args, **kwargs)
                if result is None:
                    return True
                if not isinstance(result, bool) or result is not True:
                    raise TypeError(
                        f"Effect '{fn.__name__}' must return True (type: bool), "
                        f"got {result!r} (type: {type(result).__name__})"
                    )
                return cast(bool, result)

            setattr(async_wrapper, "__vedro__effect__", True)
            return cast(AsyncCallable[P], async_wrapper)
        else:
            @wraps(fn)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
                result = fn(*args, **kwargs)
                if result is None:
                    return True
                if not isinstance(result, bool) or result is not True:
                    raise TypeError(
                        f"Effect '{fn.__name__}' must return True (type: bool), "
                        f"got {result!r} (type: {type(result).__name__})"
                    )
                return cast(bool, result)

            setattr(wrapper, "__vedro__effect__", True)
            return wrapper
else:
    from typing import TypeVar

    T = TypeVar("T")

    def effect(fn: T) -> T:
        if iscoroutinefunction(fn):
            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await fn(*args, **kwargs)
                if result is None:
                    return True
                if not isinstance(result, bool) or result is not True:
                    raise TypeError(
                        f"Effect '{fn.__name__}' must return True (type: bool), "
                        f"got {result!r} (type: {type(result).__name__})"
                    )
                return result

            setattr(async_wrapper, "__vedro__effect__", True)
            return cast(T, async_wrapper)
        else:
            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                result = fn(*args, **kwargs)
                if result is None:
                    return True
                if not isinstance(result, bool) or result is not True:
                    raise TypeError(
                        f"Effect '{fn.__name__}' must return True (type: bool), "
                        f"got {result!r} (type: {type(result).__name__})"
                    )
                return result

            setattr(wrapper, "__vedro__effect__", True)
            return cast(T, wrapper)
