from abc import ABC, abstractmethod
from typing import List

from .._virtual_scenario import VirtualScenario

__all__ = ("ScenarioOrderer",)


class ScenarioOrderer(ABC):
    @abstractmethod
    async def sort(self, scenarios: List[VirtualScenario]) -> List[VirtualScenario]:
        pass
