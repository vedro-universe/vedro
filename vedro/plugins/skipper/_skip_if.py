from inspect import isclass
from typing import Callable, Optional, Type, cast

from vedro._scenario import Scenario

from ._skip import skip

__all__ = ("skip_if",)

RetType = Callable[[Type[Scenario]], Type[Scenario]]


def skip_if(cond: Callable[[], bool], reason: Optional[str] = None) -> RetType:
    if isclass(cond) and issubclass(cond, Scenario):
        raise TypeError()

    def wrapped(scenario: Type[Scenario]) -> Type[Scenario]:
        if cond():
            return cast(Type[Scenario], skip(reason)(scenario))
        return scenario

    return wrapped
