from typing import Any, List, Union

from ._scenario_result import ScenarioResult

__all__ = ("Report",)


class Report:
    def __init__(self) -> None:
        self._results: List[ScenarioResult] = []
        self._summary: List[str] = []
        self.started_at: Union[float, None] = None
        self.ended_at: Union[float, None] = None
        self.total: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.skipped: int = 0

    @property
    def summary(self) -> List[str]:
        return self._summary

    @property
    def elapsed(self) -> float:
        if (self.ended_at is None) or (self.started_at is None):
            return 0.0
        return self.ended_at - self.started_at

    def add_result(self, result: ScenarioResult) -> None:
        self._results.append(result)

        self.total += 1
        if result.is_passed():
            self.passed += 1
        elif result.is_failed():
            self.failed += 1
        elif result.is_skipped():
            self.skipped += 1

        if result.started_at:
            if self.started_at is None:
                self.started_at = result.started_at
            self.started_at = min(self.started_at, result.started_at)

        if result.ended_at:
            if self.ended_at is None:
                self.ended_at = result.ended_at
            self.ended_at = max(self.ended_at, result.ended_at)

    def add_summary(self, summary: str) -> None:
        self._summary.append(summary)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
