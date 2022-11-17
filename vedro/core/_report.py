from typing import Any, List, Union, cast

from ._exc_info import ExcInfo
from ._scenario_result import AggregatedResult

__all__ = ("Report",)


class Report:
    def __init__(self) -> None:
        self._summary: List[str] = []
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._total: int = 0
        self._passed: int = 0
        self._failed: int = 0
        self._skipped: int = 0
        self._interrupted: Union[ExcInfo, None] = None

    @property
    def interrupted(self) -> Union[ExcInfo, None]:
        return self._interrupted

    @property
    def started_at(self) -> Union[float, None]:
        return self._started_at

    @property
    def ended_at(self) -> Union[float, None]:
        return self._ended_at

    @property
    def total(self) -> int:
        return self._total

    @property
    def passed(self) -> int:
        return self._passed

    @property
    def failed(self) -> int:
        return self._failed

    @property
    def skipped(self) -> int:
        return self._skipped

    @property
    def summary(self) -> List[str]:
        return self._summary[:]

    @property
    def elapsed(self) -> float:
        if (self.ended_at is None) or (self.started_at is None):
            return 0.0
        return self.ended_at - self.started_at

    def add_result(self, result: AggregatedResult) -> None:
        self._total += 1
        if result.is_passed():
            self._passed += 1
        elif result.is_failed():
            self._failed += 1
        elif result.is_skipped():
            self._skipped += 1

        if result.started_at:
            if self.started_at is None:
                self._started_at = result.started_at
            self._started_at = min(cast(float, self._started_at), result.started_at)

        if result.ended_at:
            if self.ended_at is None:
                self._ended_at = result.ended_at
            self._ended_at = max(cast(float, self._ended_at), result.ended_at)

    def add_summary(self, summary: str) -> None:
        self._summary.append(summary)

    def set_interrupted(self, exc_info: ExcInfo) -> None:
        self._interrupted = exc_info

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)

    def __repr__(self) -> str:
        interrupted = self.interrupted.type if self.interrupted else None
        return (f"<{self.__class__.__name__} "
                f"total={self._total} passed={self._passed} "
                f"failed={self._failed} skipped={self._skipped} "
                f"interrupted={interrupted}>")
