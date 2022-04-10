from inspect import isclass
from typing import Any, Optional, Type, Union

from vedro._scenario import Scenario

__all__ = ("skip",)


def skip(scenario_or_reason: Optional[Union[Type[Scenario], str]] = None) -> Any:
    def wrapped(scenario: Type[Scenario]) -> Type[Scenario]:
        setattr(scenario, "__vedro__skipped__", True)
        return scenario

    if (scenario_or_reason is None) or isinstance(scenario_or_reason, str):
        return wrapped
    elif isclass(scenario_or_reason) and issubclass(scenario_or_reason, Scenario):
        return wrapped(scenario_or_reason)
    else:
        raise TypeError()
