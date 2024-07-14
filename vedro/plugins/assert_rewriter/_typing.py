import sys

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:
    try:
        from typing_extensions import override
    except (ModuleNotFoundError, ImportError):  # pragma: no cover
        from typing import Any, Callable, TypeVar

        _F = TypeVar("_F", bound=Callable[..., Any])

        def override(func: _F, /) -> _F:
            return func

__all__ = ("override",)
