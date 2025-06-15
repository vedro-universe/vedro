from inspect import isclass
from os import linesep
from typing import Callable, Type, TypeVar, Union, cast, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("only",)

T = TypeVar("T", bound=Scenario)
Decorator = Callable[[Type[T]], Type[T]]


@overload
def only(scenario: Type[T]) -> Type[T]:  # @only
    pass


@overload
def only() -> Decorator[T]:  # @only()
    pass


def only(scenario: Union[Type[T], None] = None) -> Union[Type[T], Decorator[T]]:
    def apply_only(scn: Type[T]) -> Type[T]:
        if not isclass(scn) or not issubclass(scn, Scenario):
            raise TypeError(_format_only_usage_error())

        set_scenario_meta(scn, key="only", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__only__")

        return cast(Type[T], scn)

    # @only()
    if scenario is None:
        return apply_only
    # @only
    return apply_only(scenario)


def _format_only_usage_error() -> str:
    return linesep.join([
        "Decorator @only can be used only with Vedro scenarios:",
        "",
        "cls-based:",
        "    @only",
        "    class Scenario(vedro.Scenario):",
        "        ...",
        "",
        "fn-based:",
        "    @scenario[only]()",
        "    def subject():",
        "        ...",
    ])
