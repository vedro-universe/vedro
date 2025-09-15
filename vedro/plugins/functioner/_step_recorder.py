from typing import Iterator, List, Optional, Tuple, Union

__all__ = ("StepRecorder", "get_step_recorder",)

RecordType = Tuple[str, str, float, float, Union[BaseException, None]]
"""
Type alias for step execution records: (kind, name, start_time, end_time, exception)
"""


class StepRecorder:
    """
    Records step execution details for deferred event processing.

    This class tracks the execution of given/when/then steps in function-based
    scenarios. Since function-based scenarios execute all steps within a single
    "do" step, this recorder captures step details during execution and allows
    the runner to generate appropriate step events afterward.

    The recorder maintains an ordered list of step executions, each containing:
    - Step type (Given, When, Then)
    - Step name/description
    - Execution timing (start and end timestamps)
    - Any exception raised during the step
    """

    def __init__(self) -> None:
        """
        Initialize an empty step recorder.
        """
        self._records: List[RecordType] = []

    def record(self, kind: str, name: str, start_at: float, ended_at: float,
               exc: Optional[BaseException] = None) -> None:
        """
        Record a step execution.

        :param kind: The type of step (e.g., "Given", "When", "Then").
        :param name: The descriptive name of the step.
        :param start_at: The timestamp when the step started execution.
        :param ended_at: The timestamp when the step completed execution.
        :param exc: The exception raised during step execution, if any.
        """
        self._records.append((kind, name, start_at, ended_at, exc))

    def clear(self) -> None:
        """
        Clear all recorded steps.

        This should be called before running each function-based scenario
        to ensure steps from previous scenarios don't contaminate the results.
        """
        self._records.clear()

    def __iter__(self) -> Iterator[RecordType]:
        """
        Iterate over recorded step executions.

        :return: An iterator over the recorded steps in execution order.
        """
        return iter(self._records)

    def __len__(self) -> int:
        """
        Get the number of recorded steps.

        :return: The count of recorded step executions.
        """
        return len(self._records)


_step_recorder = None


def get_step_recorder() -> StepRecorder:
    """
    Get the global singleton StepRecorder instance.

    This function implements a lazy singleton pattern to provide a global
    StepRecorder instance. This is used as the default recorder when no
    specific instance is provided.

    Note: This global singleton approach is a temporary solution to avoid
    breaking changes. It will be refactored in v2 to use proper dependency
    injection and avoid global state.

    :return: The global StepRecorder instance.
    """
    global _step_recorder
    if _step_recorder is None:
        _step_recorder = StepRecorder()
    return _step_recorder
