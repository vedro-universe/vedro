from typing import Any, List

from ._scenario_result import ScenarioResult

__all__ = ("Report",)


class Report:
    def __init__(self) -> None:
        self._results: List[ScenarioResult] = []
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def add_result(self, result: ScenarioResult) -> None:
        self._results.append(result)
        if result.is_passed():
            self.total += 1
            self.passed += 1
        elif result.is_failed():
            self.total += 1
            self.failed += 1
        elif result.is_skipped():
            self.skipped += 1

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
