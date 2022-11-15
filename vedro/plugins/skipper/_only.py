from inspect import isclass
from typing import Callable, Type, TypeVar, overload

from vedro._scenario import Scenario

__all__ = ("only",)

T = TypeVar("T", bound=Type[Scenario])


@overload
def only(scenario_or_reason: T) -> T:
    pass


@overload
def only(scenario_or_reason: None = None) -> Callable[[T], T]:
    pass


def only(scenario_or_nothing=None):  # type: ignore
    def wrapped(scenario: T) -> T:
        assert issubclass(scenario, Scenario)
        setattr(scenario, "__vedro__only__", True)
        return scenario

    if scenario_or_nothing is None:
        return wrapped
    elif isclass(scenario_or_nothing) and issubclass(scenario_or_nothing, Scenario):
        return wrapped(scenario_or_nothing)
    else:
        raise TypeError("Usage: @only")
