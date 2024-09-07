from abc import ABC, abstractmethod

from vedro.core import VirtualScenario

__all__ = ("SkipAdjustedSlicingStrategy", "RoundRobinSlicingStrategy", "BaseSlicingStrategy",)


class BaseSlicingStrategy(ABC):
    """
    Abstract base class for slicing strategies.

    Slicing strategies determine which scenarios should be run by the current worker
    in a distributed testing setup.
    """

    def __init__(self, total: int, index: int) -> None:
        """
        Initialize the slicing strategy with total workers and current worker index.

        :param total: The total number of workers.
        :param index: The index of the current worker (0-based).
        """
        self._total = total
        self._index = index

    @abstractmethod
    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        """
        Determine whether the current scenario should be run by this worker.

        :param scenario: The scenario to be evaluated.
        :param current_index: The current index of the scenario in the execution order.
        :return: True if the scenario should be run by this worker, False otherwise.
        """
        pass


class RoundRobinSlicingStrategy(BaseSlicingStrategy):
    """
    Slicing strategy that assigns scenarios to workers in a round-robin fashion.

    Each scenario is assigned to a worker based on its index modulo the total number of workers.
    """

    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        """
        Check if the current worker should run the given scenario based on round-robin logic.

        :param scenario: The scenario to be evaluated.
        :param current_index: The current index of the scenario in the execution order.
        :return: True if the current worker should run the scenario, False otherwise.
        """
        return (current_index % self._total) == self._index


class SkipAdjustedSlicingStrategy(BaseSlicingStrategy):
    """
    Slicing strategy that adjusts for skipped scenarios.

    This strategy ensures that skipped scenarios are taken into account when slicing,
    because skipped scenarios "run" at 0 time and are effectively ignored in terms of workload.
    By considering skipped scenarios, the strategy ensures that all workers receive an equal
    load of non-skipped scenarios.
    """

    def __init__(self, total: int, index: int) -> None:
        """
        Initialize the slicing strategy with total workers and current worker index.

        :param total: The total number of workers.
        :param index: The index of the current worker (0-based).
        """
        super().__init__(total, index)
        self._skipped_index = 0

    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        """
        Check if the current worker should run the given scenario, accounting for skips.

        If a scenario is skipped, it is handled separately so that the load of non-skipped
        scenarios is distributed evenly across workers.

        :param scenario: The scenario to be evaluated.
        :param current_index: The current index of the scenario in the execution order.
        :return: True if the current worker should run the scenario, False otherwise.
        """
        if scenario.is_skipped():
            should_run = (self._skipped_index % self._total) == (self._total - self._index - 1)
            self._skipped_index += 1
            return should_run
        else:
            effective_index = current_index - self._skipped_index
            return (effective_index % self._total) == self._index
