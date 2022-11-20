from inspect import isclass
from typing import Callable, Type, TypeVar, overload

from vedro._scenario import Scenario

__all__ = ("only",)

T = TypeVar("T", bound=Type[Scenario])


@overload
def only(scenario_or_reason: T) -> T:  # pragma: no cover
    pass


@overload
def only(scenario_or_reason: None = None) -> Callable[[T], T]:  # pragma: no cover
    pass


def only(scenario_or_nothing=None):  # type: ignore
    def wrapped(scenario: T) -> T:
        if not issubclass(scenario, Scenario):
            raise TypeError("Decorator @only can be used only with 'vedro.Scenario' subclasses")
        setattr(scenario, "__vedro__only__", True)
        return scenario

    if scenario_or_nothing is None:
        return wrapped
    elif isclass(scenario_or_nothing):
        return wrapped(scenario_or_nothing)
    else:
        raise TypeError("Usage: @only")
