from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterator, List

from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioScheduler",)


class ScenarioScheduler(ABC):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        self._scenarios = OrderedDict((scn.unique_id, scn) for scn in scenarios)

    @property
    def scenarios(self) -> Iterator[VirtualScenario]:
        for scenario_id in list(self._scenarios.keys()):
            if scenario_id in self._scenarios:
                yield self._scenarios[scenario_id]

    def ignore(self, scenario: VirtualScenario) -> None:
        self._scenarios.pop(scenario.unique_id, None)

    @abstractmethod
    def __aiter__(self) -> "ScenarioScheduler":
        pass

    @abstractmethod
    async def __anext__(self) -> VirtualScenario:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<>"
