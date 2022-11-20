from abc import ABC, abstractmethod

from .._report import Report
from ..scenario_scheduler import ScenarioScheduler

__all__ = ("ScenarioRunner",)


class ScenarioRunner(ABC):
    @abstractmethod
    async def run(self, scheduler: ScenarioScheduler) -> Report:
        pass
