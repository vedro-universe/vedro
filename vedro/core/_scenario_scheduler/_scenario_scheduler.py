from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterator, List

from .._scenario_result import AggregatedResult, ScenarioResult
from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioScheduler",)


class ScenarioScheduler(ABC):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        self._discovered = OrderedDict((scn.unique_id, scn) for scn in scenarios)

    @property
    def discovered(self) -> Iterator[VirtualScenario]:
        for scenario_id in self._discovered:
            yield self._discovered[scenario_id]

    @property
    @abstractmethod
    def scheduled(self) -> Iterator[VirtualScenario]:
        pass

    @abstractmethod
    def schedule(self, scenario: VirtualScenario) -> None:
        pass

    @abstractmethod
    def ignore(self, scenario: VirtualScenario) -> None:
        pass

    @abstractmethod
    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        pass

    def __aiter__(self) -> "ScenarioScheduler":
        return self

    @abstractmethod
    async def __anext__(self) -> VirtualScenario:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
