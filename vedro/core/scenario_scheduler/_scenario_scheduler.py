from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterator, List

from .._virtual_scenario import VirtualScenario
from ..scenario_result import AggregatedResult, ScenarioResult

__all__ = ("ScenarioScheduler",)


class ScenarioScheduler(ABC):
    """
    Defines an abstract base class for a scenario scheduler.

    A scenario scheduler is responsible for managing the execution of scenarios,
    including scheduling, ignoring, and aggregating results.
    """

    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        """
        Initialize the ScenarioScheduler with a list of discovered scenarios.

        :param scenarios: A list of virtual scenarios to be managed by the scheduler.
        """
        self._discovered = OrderedDict((scn.unique_id, scn) for scn in scenarios)

    @property
    def discovered(self) -> Iterator[VirtualScenario]:
        """
        Get an iterator over the discovered scenarios.

        Discovered scenarios are those initially provided to the scheduler.

        :return: An iterator over the discovered virtual scenarios.
        """
        for scenario_id in self._discovered:
            yield self._discovered[scenario_id]

    @property
    @abstractmethod
    def scheduled(self) -> Iterator[VirtualScenario]:
        """
        Get an iterator over the scheduled scenarios.

        Scheduled scenarios are those that are currently queued for execution.
        This property must be implemented by subclasses.

        :return: An iterator over the scheduled virtual scenarios.
        """
        pass

    @abstractmethod
    def schedule(self, scenario: VirtualScenario) -> None:
        """
        Schedule a scenario for execution.

        This method must be implemented by subclasses to handle the addition
        of a scenario to the scheduler's execution queue.

        :param scenario: The virtual scenario to be scheduled.
        """
        pass

    @abstractmethod
    def ignore(self, scenario: VirtualScenario) -> None:
        """
        Remove a scenario from the scheduler.

        This method must be implemented by subclasses to handle the removal
        of a scenario from both the discovered and scheduled lists.

        :param scenario: The virtual scenario to be ignored.
        """
        pass

    @abstractmethod
    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        """
        Aggregate the results of a scenario's executions.

        This method must be implemented by subclasses to create an aggregated
        result representing the combined outcomes of a scenario's executions.

        :param scenario_results: A list of scenario results to be aggregated.
        :return: An aggregated result representing the combined outcome of the executions.
        """
        pass

    def __aiter__(self) -> "ScenarioScheduler":
        """
        Prepare the scheduler for asynchronous iteration.

        :return: The scheduler instance itself.
        """
        return self

    @abstractmethod
    async def __anext__(self) -> VirtualScenario:
        """
        Retrieve the next scenario to be executed asynchronously.

        This method must be implemented by subclasses to provide support
        for asynchronous iteration over scheduled scenarios.

        :return: The next virtual scenario to be executed.
        :raises StopAsyncIteration: If no more scenarios are available for execution.
        """
        pass

    def __repr__(self) -> str:
        """
        Return a string representation of the scheduler.

        :return: A string describing the scheduler instance.
        """
        return f"<{self.__class__.__name__}>"
