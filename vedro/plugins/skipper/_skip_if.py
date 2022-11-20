from inspect import isclass
from typing import Callable, Optional, Type, TypeVar

from vedro._scenario import Scenario

from ._skip import skip

__all__ = ("skip_if",)


T = TypeVar("T", bound=Type[Scenario])


def skip_if(cond: Callable[[], bool], reason: Optional[str] = None) -> Callable[[T], T]:
    if isclass(cond) or not callable(cond):
        raise TypeError('Usage: @skip_if(<condition>, "reason?")')

    def wrapped(scenario: T) -> T:
        if not issubclass(scenario, Scenario):
            raise TypeError("Decorator @skip_if can be used only with 'vedro.Scenario' subclasses")
        if cond():
            return skip(reason)(scenario)
        return scenario

    return wrapped
