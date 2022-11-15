from inspect import isclass
from typing import Callable, Type, TypeVar, overload

from vedro._scenario import Scenario

__all__ = ("skip",)


T = TypeVar("T", bound=Type[Scenario])


@overload
def skip(scenario_or_reason: T) -> T:
    pass


@overload
def skip(scenario_or_reason: str) -> Callable[[T], T]:
    pass


@overload
def skip(scenario_or_reason: None = None) -> Callable[[T], T]:
    pass


def skip(scenario_or_reason=None):  # type: ignore
    def wrapped(scenario: T) -> T:
        assert issubclass(scenario, Scenario)
        setattr(scenario, "__vedro__skipped__", True)
        if isinstance(scenario_or_reason, str):
            setattr(scenario, "__vedro__skip_reason__", scenario_or_reason)
        return scenario

    if (scenario_or_reason is None) or isinstance(scenario_or_reason, str):
        return wrapped
    elif isclass(scenario_or_reason) and issubclass(scenario_or_reason, Scenario):
        return wrapped(scenario_or_reason)
    else:
        raise TypeError('Usage: @skip or @skip("reason")')
