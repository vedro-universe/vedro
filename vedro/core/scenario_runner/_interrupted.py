from .._exc_info import ExcInfo
from .._step_result import StepResult
from ..scenario_result import ScenarioResult

__all__ = ("Interrupted", "StepInterrupted", "ScenarioInterrupted", "RunInterrupted")


class Interrupted(BaseException):
    """
    Base class for interruptions during the execution process.

    This exception is raised to signal that an execution flow has been interrupted.
    Subclasses provide specific details for steps, scenarios, or the entire run.
    """
    pass


class StepInterrupted(Interrupted):
    """
    Represents an interruption that occurs during the execution of a step.

    This exception provides information about the exception that caused the interruption
    and the result of the step execution up to the point of interruption.
    """

    def __init__(self, exc_info: ExcInfo, step_result: StepResult) -> None:
        """
        Initialize the StepInterrupted exception.

        :param exc_info: The exception information that caused the interruption.
        :param step_result: The step result at the time of the interruption.
        """
        self._exc_info = exc_info
        self._step_result = step_result

    @property
    def exc_info(self) -> ExcInfo:
        """
        Get the exception information that caused the interruption.

        :return: The exception information object.
        """
        return self._exc_info

    @property
    def step_result(self) -> StepResult:
        """
        Get the step result at the time of the interruption.

        :return: The step result instance.
        """
        return self._step_result

    def __repr__(self) -> str:
        """
        Return a string representation of the exception.

        :return: A string describing the exception.
        """
        return f"{self.__class__.__name__}({self._exc_info!r}, {self._step_result!r})"


class ScenarioInterrupted(Interrupted):
    """
    Represents an interruption that occurs during the execution of a scenario.

    This exception provides information about the exception that caused the interruption
    and the result of the scenario execution up to the point of interruption.
    """

    def __init__(self, exc_info: ExcInfo, scenario_result: ScenarioResult) -> None:
        """
        Initialize the ScenarioInterrupted exception.

        :param exc_info: The exception information that caused the interruption.
        :param scenario_result: The scenario result at the time of the interruption.
        """
        self._exc_info = exc_info
        self._scenario_result = scenario_result

    @property
    def exc_info(self) -> ExcInfo:
        """
        Get the exception information that caused the interruption.

        :return: The exception information object.
        """
        return self._exc_info

    @property
    def scenario_result(self) -> ScenarioResult:
        """
        Get the scenario result at the time of the interruption.

        :return: The scenario result instance.
        """
        return self._scenario_result

    def __repr__(self) -> str:
        """
        Return a string representation of the exception.

        :return: A string describing the exception.
        """
        return f"{self.__class__.__name__}({self._exc_info!r}, {self._scenario_result!r})"


class RunInterrupted(Interrupted):
    """
    Represents an interruption that occurs during the execution of the entire run.

    This exception provides information about the exception that caused the interruption.
    """

    def __init__(self, exc_info: ExcInfo) -> None:
        """
        Initialize the RunInterrupted exception.

        :param exc_info: The exception information that caused the interruption.
        """
        self._exc_info = exc_info

    @property
    def exc_info(self) -> ExcInfo:
        """
        Get the exception information that caused the interruption.

        :return: The exception information object.
        """
        return self._exc_info

    def __repr__(self) -> str:
        """
        Return a string representation of the exception.

        :return: A string describing the exception.
        """
        return f"{self.__class__.__name__}({self._exc_info!r})"
