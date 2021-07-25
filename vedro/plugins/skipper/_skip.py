from typing import Any, Type, Union

from vedro import Scenario

__all__ = ("skip",)


def skip(scenario_or_reason: Union[Type[Scenario], str]) -> Any:
    def wrapped(scenario: Type[Scenario]) -> Type[Scenario]:
        setattr(scenario, "__vedro__skipped__", True)
        return scenario

    if isinstance(scenario_or_reason, str):
        return wrapped
    elif issubclass(scenario_or_reason, Scenario):
        return wrapped(scenario_or_reason)
    else:
        raise TypeError()
