from abc import ABC, abstractmethod

from .._report import Report
from ..scenario_scheduler import ScenarioScheduler

__all__ = ("ScenarioRunner",)


class ScenarioRunner(ABC):
    """
    Defines an abstract base class for a scenario runner.

    A scenario runner is responsible for executing scenarios provided by a scheduler
    and producing a report of the results.
    """

    @abstractmethod
    async def run(self, scheduler: ScenarioScheduler) -> Report:
        """
        Execute scenarios provided by the scheduler and return a report.

        Subclasses must implement this method to define the execution logic,
        including handling scenario execution, managing interruptions, and
        aggregating results into the final report.

        :param scheduler: The scheduler providing scenarios to execute.
        :return: A report containing the results of all executed scenarios.
        """
        pass
