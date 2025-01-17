from inspect import isclass
from typing import Callable, Type, TypeVar, overload

from vedro._scenario import Scenario
from vedro.core import set_scenario_meta

from ._skipper import SkipperPlugin

__all__ = ("skip",)


T = TypeVar("T", bound=Type[Scenario])


@overload
def skip(reason: T) -> T:  # pragma: no cover
    pass


@overload
def skip(reason: str) -> Callable[[T], T]:  # pragma: no cover
    pass


@overload
def skip(reason: None = None) -> Callable[[T], T]:  # pragma: no cover
    pass


def skip(reason=None):  # type: ignore
    def wrapped(scenario: T) -> T:
        if not issubclass(scenario, Scenario):
            raise TypeError("Decorator @skip can be used only with 'vedro.Scenario' subclasses")

        set_scenario_meta(scenario, key="skipped", value=True, plugin=SkipperPlugin,
                          fallback_key="__vedro__skipped__")

        if isinstance(reason, str):
            set_scenario_meta(scenario, key="skip_reason", value=reason, plugin=SkipperPlugin,
                              fallback_key="__vedro__skip_reason__")

        return scenario

    if (reason is None) or isinstance(reason, str):
        return wrapped
    elif isclass(reason):
        return wrapped(reason)
    else:
        raise TypeError('Usage: @skip or @skip("reason")')
