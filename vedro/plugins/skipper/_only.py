from inspect import isclass
from typing import Callable, Type, TypeVar, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("only",)

T = TypeVar("T", bound=Type[Scenario])


@overload
def only(scenario_or_nothing: T) -> T:  # pragma: no cover
    pass


@overload
def only(scenario_or_nothing: None = None) -> Callable[[T], T]:  # pragma: no cover
    pass


def only(scenario_or_nothing=None):  # type: ignore
    def wrapped(scenario: T) -> T:
        if not issubclass(scenario, Scenario):
            raise TypeError("Decorator @only can be used only with 'vedro.Scenario' subclasses")

        set_scenario_meta(scenario, key="only", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__only__")

        return scenario

    if scenario_or_nothing is None:
        return wrapped
    elif isclass(scenario_or_nothing):
        return wrapped(scenario_or_nothing)
    else:
        raise TypeError("Usage: @only")
