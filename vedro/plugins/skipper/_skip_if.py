from inspect import isclass
from typing import Callable, Optional, Type, TypeVar

from vedro._scenario import Scenario

from ._skip import skip

__all__ = ("skip_if",)


T = TypeVar("T", bound=Type[Scenario])


def skip_if(cond: Callable[[], bool], reason: Optional[str] = None) -> Callable[[T], T]:
    if isclass(cond) and issubclass(cond, Scenario):
        raise TypeError('Usage: @skip_if(<condition>, "reason?")')

    def wrapped(scenario: T) -> T:
        if cond():
            return skip(reason)(scenario)
        return scenario

    return wrapped
