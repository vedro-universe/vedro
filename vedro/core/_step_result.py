from enum import Enum
from typing import Any, List, Union

from ._artifacts import Artifact
from ._exc_info import ExcInfo
from ._virtual_step import VirtualStep

__all__ = ("StepResult", "StepStatus",)


class StepStatus(Enum):
    """
    Enumeration of possible states for a `StepResult`.

    Used to indicate the current status of a test step during execution.
    """

    PENDING = "PENDING"
    """
    Indicates the step is awaiting execution.
    """

    PASSED = "PASSED"
    """
    Signifies the step has completed successfully.
    """

    FAILED = "FAILED"
    """
    Marks the step as unsuccessful due to an assertion failure or an unexpected error.
    """


class StepResult:
    """
    Represents the result of a step execution.

    This class manages the state and outcome of a test step, including its status,
    timing, associated artifacts, exceptions, and additional details.
    """

    def __init__(self, step: VirtualStep) -> None:
        """
        Initialize a StepResult instance for the given step.

        :param step: The virtual step for which the result is tracked.
        """
        self._step = step
        self._status: StepStatus = StepStatus.PENDING
        self._started_at: Union[float, None] = None
        self._ended_at: Union[float, None] = None
        self._exc_info: Union[ExcInfo, None] = None
        self._artifacts: List[Artifact] = []
        self._extra_details: List[str] = []

    @property
    def step(self) -> VirtualStep:
        """
        Retrieve the virtual step associated with this result.

        :return: The virtual step object.
        """
        return self._step

    @property
    def step_name(self) -> str:
        """
        Retrieve the name of the step.

        :return: The name of the step as a string.
        """
        return self._step.name

    @property
    def status(self) -> StepStatus:
        """
        Retrieve the current status of the step.

        :return: The current step status.
        """
        return self._status

    def is_passed(self) -> bool:
        """
        Check if the step is marked as passed.

        :return: True if the step is passed, False otherwise.
        """
        return self._status == StepStatus.PASSED

    def is_failed(self) -> bool:
        """
        Check if the step is marked as failed.

        :return: True if the step is failed, False otherwise.
        """
        return self._status == StepStatus.FAILED

    def mark_failed(self) -> "StepResult":
        """
        Mark the step as failed.

        :return: The StepResult instance for chaining.
        :raises RuntimeError: If the step status has already been set.
        """
        if self._status != StepStatus.PENDING:
            raise RuntimeError(
                "Cannot mark step as failed because its status has already been set"
            )
        self._status = StepStatus.FAILED
        return self

    def mark_passed(self) -> "StepResult":
        """
        Mark the step as passed.

        :return: The StepResult instance for chaining.
        :raises RuntimeError: If the step status has already been set.
        """
        if self._status != StepStatus.PENDING:
            raise RuntimeError(
                "Cannot mark step as passed because its status has already been set"
            )
        self._status = StepStatus.PASSED
        return self

    @property
    def started_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the step started.

        :return: The start time as a float or None if not set.
        """
        return self._started_at

    def set_started_at(self, started_at: float) -> "StepResult":
        """
        Set the start timestamp for the step.

        :param started_at: The start time as a float.
        :return: The StepResult instance for chaining.
        """
        self._started_at = started_at
        return self

    @property
    def ended_at(self) -> Union[float, None]:
        """
        Retrieve the timestamp when the step ended.

        :return: The end time as a float or None if not set.
        """
        return self._ended_at

    def set_ended_at(self, ended_at: float) -> "StepResult":
        """
        Set the end timestamp for the step.

        :param ended_at: The end time as a float.
        :return: The StepResult instance for chaining.
        """
        self._ended_at = ended_at
        return self

    @property
    def elapsed(self) -> float:
        """
        Calculate the elapsed time for the step.

        :return: The elapsed time in seconds, or 0.0 if the start or end time is not set.
        """
        if (self._started_at is None) or (self._ended_at is None):
            return 0.0
        return self._ended_at - self._started_at

    @property
    def exc_info(self) -> Union[ExcInfo, None]:
        """
        Retrieve exception information associated with the step.

        :return: The exception information object, or None if no exception occurred.
        """
        return self._exc_info

    def set_exc_info(self, exc_info: ExcInfo) -> "StepResult":
        """
        Set the exception information for the step.

        :param exc_info: The exception information object.
        :return: The StepResult instance for chaining.
        """
        self._exc_info = exc_info
        return self

    def attach(self, artifact: Artifact) -> None:
        """
        Attach an artifact to the step.

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

    def add_extra_details(self, extra: str) -> None:
        """
        Add extra details related to the step.

        :param extra: A string containing additional details.
        """
        self._extra_details.append(extra)

    @property
    def extra_details(self) -> List[str]:
        """
        Retrieve the list of extra details.

        :return: A shallow copy of the extra details list.
        """
        return self._extra_details[:]

    def __repr__(self) -> str:
        """
        Return a string representation of the StepResult instance.

        :return: A string containing the class name, step, and status.
        """
        return f"<{self.__class__.__name__} {self._step!r} {self._status.value}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another StepResult instance.

        :param other: The object to compare.
        :return: True if the instances are equal, False otherwise.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
