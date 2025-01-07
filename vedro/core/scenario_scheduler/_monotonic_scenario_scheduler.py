from collections import OrderedDict
from typing import Iterator, List, Tuple

from .._virtual_scenario import VirtualScenario
from ..scenario_result import AggregatedResult, ScenarioResult
from ._scenario_scheduler import ScenarioScheduler

__all__ = ("MonotonicScenarioScheduler",)


class MonotonicScenarioScheduler(ScenarioScheduler):
    """
    Implements a monotonic scenario scheduler.

    This scheduler ensures that scenarios are executed in a monotonic order, based on
    their discovery order, and supports scheduling scenarios for repeated execution.
    """

    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        """
        Initialize the MonotonicScenarioScheduler with the provided scenarios.

        :param scenarios: A list of virtual scenarios to be managed by the scheduler.
        """
        super().__init__(scenarios)
        self._scheduled = OrderedDict((k, (v, 0)) for k, v in reversed(self._discovered.items()))
        self._queue: OrderedDict[str, Tuple[VirtualScenario, int]] = OrderedDict()

    @property
    def scheduled(self) -> Iterator[VirtualScenario]:
        """
        Get an iterator over the scheduled scenarios.

        Each scenario is yielded once for each time it has been scheduled, plus its
        initial occurrence.

        :return: An iterator over the scheduled scenarios.
        """
        for scenario_id in reversed(self._scheduled):
            scenario, repeats = self._scheduled[scenario_id]
            for _ in range(repeats + 1):
                yield scenario

    def ignore(self, scenario: VirtualScenario) -> None:
        """
        Remove a scenario from the scheduler.

        This method removes the scenario from both the scheduled list and the execution queue.

        :param scenario: The virtual scenario to be ignored.
        """
        self._scheduled.pop(scenario.unique_id, None)
        self._queue.pop(scenario.unique_id, None)

    def __aiter__(self) -> "ScenarioScheduler":
        """
        Prepare the scheduler for asynchronous iteration.

        This method resets the queue to match the current scheduled scenarios.

        :return: The scheduler instance itself.
        """
        self._queue = self._scheduled.copy()
        return super().__aiter__()

    async def __anext__(self) -> VirtualScenario:
        """
        Retrieve the next scenario to be executed in the queue.

        If the scenario has been scheduled multiple times, it decrements the repeat count
        and re-adds the scenario to the queue.

        :return: The next virtual scenario to be executed.
        :raises StopAsyncIteration: If no more scenarios are available in the queue.
        """
        while len(self._queue) > 0:
            _, (scenario, repeats) = self._queue.popitem()
            if repeats > 0:
                self._queue[scenario.unique_id] = (scenario, repeats - 1)
            return scenario
        raise StopAsyncIteration()

    def schedule(self, scenario: VirtualScenario) -> None:
        """
        Schedule a scenario for repeated execution.

        This method increments the repeat count of the scenario in both the scheduled list
        and the queue, or adds it as a new scenario if it is not already scheduled.

        :param scenario: The virtual scenario to be scheduled.
        """
        if scenario.unique_id in self._scheduled:
            scn, repeats = self._scheduled[scenario.unique_id]
            scheduled = (scn, repeats + 1)
        else:
            scheduled = (scenario, 0)
        self._scheduled[scenario.unique_id] = scheduled

        if scenario.unique_id in self._queue:
            scn, repeats = self._queue[scenario.unique_id]
            queued = (scn, repeats + 1)
        else:
            queued = (scenario, 0)
        self._queue[scenario.unique_id] = queued

    def aggregate_results(self, scenario_results: List[ScenarioResult]) -> AggregatedResult:
        """
        Aggregate the results of a scenario's executions.

        This method creates an aggregated result for the scenario. If any of the executions failed,
        the aggregated result will be marked as failed. Otherwise, the result of the first
        execution is used as the base.

        :param scenario_results: A list of scenario results to be aggregated.
        :return: An aggregated result representing the combined outcome of the executions.
        :raises AssertionError: If the list of scenario results is empty.
        """
        assert len(scenario_results) > 0

        result = scenario_results[0]
        for scenario_result in scenario_results:
            if scenario_result.is_failed():
                result = scenario_result
                break

        return AggregatedResult.from_existing(result, scenario_results)
