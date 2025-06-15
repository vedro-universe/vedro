from inspect import isclass
from os import linesep
from typing import Any, Callable, Optional, Type, TypeVar, cast

from vedro._scenario import Scenario

from ._skip import skip

__all__ = ("skip_if",)


T = TypeVar("T", bound=Scenario)
Decorator = Callable[[Type[T]], Type[T]]


def skip_if(cond: Callable[[], bool], reason: Optional[str] = None) -> Decorator[T]:
    if not callable(cond):
        raise TypeError(_format_skip_if_usage_error(reason))

    def apply_skip_if(scenario: Type[T]) -> Type[T]:
        if not isclass(scenario) or not issubclass(scenario, Scenario):
            raise TypeError(_format_skip_if_usage_error(reason))
        if cond():
            decorator = skip(reason) if reason is not None else skip()  # type: ignore
            return decorator(scenario)
        else:
            return cast(Type[T], scenario)

    return apply_skip_if


def _format_skip_if_usage_error(maybe_reason: Any) -> str:
    if maybe_reason is not None:
        decorator_repr = f"skip_if(<cond>, {maybe_reason!r})"
    else:
        decorator_repr = "skip_if(<cond>)"

    return linesep.join([
        "Decorator @skip_if must be used as @skip_if(<condition>, 'reason?') "
        "and only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @{decorator_repr}",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @scenario[{decorator_repr}]",
        "    def subject():",
        "        ...",
    ])
