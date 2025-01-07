import warnings
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from ..core._event import Event
from ..core._exc_info import ExcInfo
from ..core._report import Report
from ..core._step_result import StepResult
from ..core._virtual_scenario import VirtualScenario
from ..core.config_loader import ConfigType
from ..core.scenario_result import AggregatedResult, ScenarioResult
from ..core.scenario_scheduler import ScenarioScheduler


class ConfigLoadedEvent(Event):
    """
    Represents the event triggered when the configuration is loaded.

    This event provides access to the configuration file path and the loaded configuration object.
    """

    def __init__(self, path: Path, config: ConfigType) -> None:
        """
        Initialize the ConfigLoadedEvent.

        :param path: The path to the configuration file.
        :param config: The loaded configuration object.
        """
        self._path = path
        self._config = config

    @property
    def path(self) -> Path:
        """
        Get the path to the configuration file.

        :return: The configuration file path.
        """
        return self._path

    @property
    def config(self) -> ConfigType:
        """
        Get the loaded configuration object.

        :return: The configuration object.
        """
        return self._config

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._path!r}, <Config>)"


class ArgParseEvent(Event):
    """
    Represents the event triggered when command-line arguments are being parsed.

    This event allows plugins to modify the argument parser.
    """

    def __init__(self, arg_parser: ArgumentParser) -> None:
        """
        Initialize the ArgParseEvent.

        :param arg_parser: The argument parser used for command-line argument parsing.
        """
        self._arg_parser = arg_parser

    @property
    def arg_parser(self) -> ArgumentParser:
        """
        Get the argument parser.

        :return: The argument parser instance.
        """
        return self._arg_parser

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._arg_parser!r})"


class ArgParsedEvent(Event):
    """
    Represents the event triggered after command-line arguments have been parsed.

    This event provides access to the parsed arguments.
    """

    def __init__(self, args: Namespace) -> None:
        """
        Initialize the ArgParsedEvent.

        :param args: The parsed command-line arguments.
        """
        self._args = args

    @property
    def args(self) -> Namespace:
        """
        Get the parsed arguments.

        :return: A namespace containing the parsed arguments.
        """
        return self._args

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._args!r})"


class StartupEvent(Event):
    """
    Represents the event triggered at the beginning of the test execution.

    This event provides access to the scenario scheduler.
    """

    def __init__(self, scheduler: ScenarioScheduler) -> None:
        """
        Initialize the StartupEvent.

        :param scheduler: The scheduler used to manage scenarios.
        """
        self._scheduler = scheduler

    @property
    def scheduler(self) -> ScenarioScheduler:
        """
        Get the scenario scheduler.

        :return: The scenario scheduler instance.
        """
        return self._scheduler

    @property
    def scenarios(self) -> List[VirtualScenario]:
        """
        Get the list of discovered scenarios.

        :return: A list of virtual scenarios.
        """
        warnings.warn("Deprecated: use scheduler.discovered instead", DeprecationWarning)
        return list(self._scheduler.discovered)

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._scheduler!r})"


class _ScenarioEvent(Event):
    """
    Base class for events related to scenarios.

    This event provides access to the scenario result.
    """

    def __init__(self, scenario_result: ScenarioResult) -> None:
        """
        Initialize the _ScenarioEvent.

        :param scenario_result: The result of the scenario.
        """
        self._scenario_result = scenario_result

    @property
    def scenario_result(self) -> ScenarioResult:
        """
        Get the scenario result.

        :return: The scenario result instance.
        """
        return self._scenario_result

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._scenario_result!r})"


class ScenarioSkippedEvent(_ScenarioEvent):
    """
    Represents the event triggered when a scenario is skipped.
    """
    pass


class ScenarioFailedEvent(_ScenarioEvent):
    """
    Represents the event triggered when a scenario fails.
    """
    pass


class ScenarioRunEvent(_ScenarioEvent):
    """
    Represents the event triggered when a scenario starts running.
    """
    pass


class ScenarioPassedEvent(_ScenarioEvent):
    """
    Represents the event triggered when a scenario passes.
    """
    pass


class _StepEvent(Event):
    """
    Base class for events related to steps.

    This event provides access to the step result.
    """

    def __init__(self, step_result: StepResult) -> None:
        """
        Initialize the _StepEvent.

        :param step_result: The result of the step.
        """
        self._step_result = step_result

    @property
    def step_result(self) -> StepResult:
        """
        Get the step result.

        :return: The step result instance.
        """
        return self._step_result

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._step_result!r})"


class StepRunEvent(_StepEvent):
    """
    Represents the event triggered when a step starts running.
    """
    pass


class StepFailedEvent(_StepEvent):
    """
    Represents the event triggered when a step fails.
    """
    pass


class StepPassedEvent(_StepEvent):
    """
    Represents the event triggered when a step passes.
    """
    pass


class ExceptionRaisedEvent(Event):
    """
    Represents the event triggered when an exception is raised.

    This event provides access to exception information.
    """

    def __init__(self, exc_info: ExcInfo) -> None:
        """
        Initialize the ExceptionRaisedEvent.

        :param exc_info: The exception information object.
        """
        self._exc_info = exc_info

    @property
    def exc_info(self) -> ExcInfo:
        """
        Get the exception information.

        :return: The exception information object.
        """
        return self._exc_info

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._exc_info!r})"


class ScenarioReportedEvent(Event):
    """
    Represents the event triggered after a scenario is reported.

    This event provides access to the aggregated result of the scenario.
    """

    def __init__(self, aggregated_result: AggregatedResult) -> None:
        """
        Initialize the ScenarioReportedEvent.

        :param aggregated_result: The aggregated result of the scenario.
        """
        self._aggregated_result = aggregated_result

    @property
    def aggregated_result(self) -> AggregatedResult:
        """
        Get the aggregated result of the scenario.

        :return: The aggregated result instance.
        """
        return self._aggregated_result

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._aggregated_result!r})"


class CleanupEvent(Event):
    """
    Represents the event triggered at the end of test execution.

    This event provides access to the test execution report.
    """

    def __init__(self, report: Report) -> None:
        """
        Initialize the CleanupEvent.

        :param report: The test execution report.
        """
        self._report = report

    @property
    def report(self) -> Report:
        """
        Get the test execution report.

        :return: The report instance.
        """
        return self._report

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        :return: A string describing the event.
        """
        return f"{self.__class__.__name__}({self._report!r})"


__all__ = (
    "Event", "ConfigLoadedEvent", "ArgParseEvent", "ArgParsedEvent",
    "StartupEvent", "ScenarioRunEvent", "ScenarioSkippedEvent",
    "ScenarioFailedEvent", "ScenarioPassedEvent",
    "StepRunEvent", "StepFailedEvent", "StepPassedEvent", "ExceptionRaisedEvent",
    "ScenarioReportedEvent", "CleanupEvent",
)
