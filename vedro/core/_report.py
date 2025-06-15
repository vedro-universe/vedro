from typing import Any, List, Union, cast

from vedro.core._artifacts import Artifact
from vedro.core._exc_info import ExcInfo
from vedro.core._scenario_result import AggregatedResult

__all__ = ("Report",)


class Report:
    """
    Represents a report for test execution results.

    This class aggregates results from multiple test scenarios, tracks execution
    statistics such as total, passed, failed, skipped scenarios, and provides
    summary information. It also handles execution timing, artifacts, and
    interruptions.
    """

    def __init__(self) -> None:
        """
        Initialize a Report instance with default values.
        """
        self._summary: List[str] = []
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._total: int = 0
        self._passed: int = 0
        self._failed: int = 0
        self._skipped: int = 0
        self._interrupted: Union[ExcInfo, None] = None
        self._artifacts: List[Artifact] = []

    @property
    def interrupted(self) -> Union[ExcInfo, None]:
        """
        Retrieve information about any interruption that occurred.

        :return: The exception information if interrupted, otherwise None.
        """
        return self._interrupted

    @property
    def started_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the first scenario started.

        :return: The start time as a float or None if not set.
        """
        return self._started_at

    @property
    def ended_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the last scenario ended.

        :return: The end time as a float or None if not set.
        """
        return self._ended_at

    @property
    def total(self) -> int:
        """
        Retrieve the total number of scenarios executed.

        :return: The total number of scenarios.
        """
        return self._total

    @property
    def passed(self) -> int:
        """
        Retrieve the number of scenarios that passed.

        :return: The count of passed scenarios.
        """
        return self._passed

    @property
    def failed(self) -> int:
        """
        Retrieve the number of scenarios that failed.

        :return: The count of failed scenarios.
        """
        return self._failed

    @property
    def skipped(self) -> int:
        """
        Retrieve the number of scenarios that were skipped.

        :return: The count of skipped scenarios.
        """
        return self._skipped

    @property
    def summary(self) -> List[str]:
        """
        Retrieve the summary information for the report.

        :return: A shallow copy of the summary list.
        """
        return self._summary[:]

    @property
    def elapsed(self) -> float:
        """
        Calculate the total elapsed time for all scenarios.

        :return: The elapsed time in seconds, or 0.0 if timing information is not set.
        """
        if (self.ended_at is None) or (self.started_at is None):
            return 0.0
        return self.ended_at - self.started_at

    def add_result(self, result: AggregatedResult) -> None:
        """
        Add the result of a scenario to the report.

        Updates the total, passed, failed, or skipped counts based on the scenario status.
        Adjusts the overall start and end times based on the scenario's timing.

        :param result: The aggregated result of a scenario.
        """
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
        """
        Add a summary entry to the report.

        :param summary: A string containing summary information.
        """
        self._summary.append(summary)

    def attach(self, artifact: Artifact) -> None:
        """
        Attach an artifact to the report.

        :param artifact: The artifact to attach.
        :raises TypeError: If the provided artifact is not an instance of Artifact.
        """
        if not isinstance(artifact, Artifact):
            raise TypeError(
                f"Expected an instance of Artifact, got {type(artifact).__name__}"
            )
        self._artifacts.append(artifact)

    @property
    def artifacts(self) -> List[Artifact]:
        """
        Retrieve the list of attached artifacts.

        :return: A shallow copy of the artifacts list.
        """
        # In v2, this will return a tuple instead of a list
        return self._artifacts[:]

    def set_interrupted(self, exc_info: ExcInfo) -> None:
        """
        Set the exception information for an interruption.

        :param exc_info: The exception information related to the interruption.
        """
        self._interrupted = exc_info

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another Report instance.

        :param other: The object to compare.
        :return: True if the instances are equal, False otherwise.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)

    def __repr__(self) -> str:
        """
        Return a string representation of the Report instance.

        :return: A string containing the report's totals and interruption status.
        """
        interrupted = self.interrupted.type if self.interrupted else None
        return (f"<{self.__class__.__name__} "
                f"total={self._total} passed={self._passed} "
                f"failed={self._failed} skipped={self._skipped} "
                f"interrupted={interrupted}>")
