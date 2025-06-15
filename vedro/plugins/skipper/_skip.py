from inspect import isclass
from os import linesep
from typing import Any, Callable, Type, TypeVar, Union, cast, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("skip",)


T = TypeVar("T", bound=Scenario)
Decorator = Callable[[Type[T]], Type[T]]


@overload
def skip(scenario_or_reason: Type[T]) -> Type[T]:  # @skip
    pass


@overload
def skip() -> Decorator[T]:  # @skip()
    pass


@overload
def skip(scenario_or_reason: str) -> Decorator[T]:  # @skip("reason")
    pass


def skip(scenario_or_reason: Union[Type[T], str, None] = None) -> Union[Type[T], Decorator[T]]:
    def apply_skip(scn: Type[T]) -> Type[T]:
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_skip_usage_error(scenario_or_reason))

        set_scenario_meta(scn, key="skipped", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__skipped__")

        if isinstance(reason := scenario_or_reason, str):
            set_scenario_meta(scn, key="skip_reason", value=reason, plugin=SkipperPlugin,
                              fallback_key="__vedro__skip_reason__")

        return cast(Type[T], scn)

    # @skip() or @skip("reason")
    if (scenario_or_reason is None) or isinstance(scenario_or_reason, str):
        return apply_skip
    # @skip
    return apply_skip(scenario_or_reason)


def _format_skip_usage_error(maybe_reason: Any) -> str:
    if isinstance(maybe_reason, str):
        decorator_repr = f"skip({maybe_reason!r})"
        fn_decorator_repr = f"scenario[{decorator_repr}]"
    else:
        decorator_repr = "skip"
        fn_decorator_repr = f"scenario[{decorator_repr}]()"

    return linesep.join([
        "Decorator @skip can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        f"    @{decorator_repr}",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        f"    @{fn_decorator_repr}",
        "    def subject():",
        "        ...",
    ])
