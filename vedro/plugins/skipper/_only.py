from inspect import isclass
from typing import Any, Type, Union

from vedro._scenario import Scenario

__all__ = ("only",)


def only(scenario_or_nothing: Union[Type[Scenario], None] = None) -> Any:
    def wrapped(scenario: Type[Scenario]) -> Type[Scenario]:
        setattr(scenario, "__vedro__only__", True)
        return scenario

    if scenario_or_nothing is None:
        return wrapped
    elif isclass(scenario_or_nothing) and issubclass(scenario_or_nothing, Scenario):
        return wrapped(scenario_or_nothing)
    else:
        raise TypeError()
