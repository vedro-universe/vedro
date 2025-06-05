from abc import ABC, abstractmethod
from typing import List

from vedro.core import VirtualScenario

from ._scenario_source import ScenarioSource

__all__ = ("ScenarioProvider",)


class ScenarioProvider(ABC):
    @abstractmethod
    async def provide(self, source: ScenarioSource) -> List[VirtualScenario]:
        pass
