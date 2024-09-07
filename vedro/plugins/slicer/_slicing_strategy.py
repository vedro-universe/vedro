from abc import ABC, abstractmethod

from vedro.core import VirtualScenario

__all__ = ("SkipAdjustedSlicingStrategy", "RoundRobinSlicingStrategy", "BaseSlicingStrategy",)


class BaseSlicingStrategy(ABC):
    def __init__(self, total: int, index: int) -> None:
        self._total = total
        self._index = index

    @abstractmethod
    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        pass


class RoundRobinSlicingStrategy(BaseSlicingStrategy):
    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        return (current_index % self._total) == self._index


class SkipAdjustedSlicingStrategy(BaseSlicingStrategy):
    def __init__(self, total: int, index: int) -> None:
        super().__init__(total, index)
        self._skipped_index = 0

    def should_run(self, scenario: VirtualScenario, current_index: int) -> bool:
        if scenario.is_skipped():
            should_run = (self._skipped_index % self._total) == (self._total - self._index - 1)
            self._skipped_index += 1
            return should_run
        else:
            effective_index = current_index - self._skipped_index
            return (effective_index % self._total) == self._index
