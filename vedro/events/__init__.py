import warnings
from argparse import Namespace
from pathlib import Path
from typing import List

from ..core._arg_parser import ArgumentParser
from ..core._config_loader import ConfigType
from ..core._event import Event
from ..core._exc_info import ExcInfo
from ..core._report import Report
from ..core._scenario_result import AggregatedResult, ScenarioResult
from ..core._step_result import StepResult
from ..core._virtual_scenario import VirtualScenario
from ..core.scenario_scheduler import ScenarioScheduler


class ConfigLoadedEvent(Event):
    def __init__(self, path: Path, config: ConfigType) -> None:
        self._path = path
        self._config = config

    @property
    def path(self) -> Path:
        return self._path

    @property
    def config(self) -> ConfigType:
        return self._config

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._path!r}, <Config>)"


class ArgParseEvent(Event):
    def __init__(self, arg_parser: ArgumentParser) -> None:
        self._arg_parser = arg_parser

    @property
    def arg_parser(self) -> ArgumentParser:
        return self._arg_parser

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._arg_parser!r})"


class ArgParsedEvent(Event):
    def __init__(self, args: Namespace) -> None:
        self._args = args

    @property
    def args(self) -> Namespace:
        return self._args

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._args!r})"


class StartupEvent(Event):
    def __init__(self, scheduler: ScenarioScheduler) -> None:
        self._scheduler = scheduler

    @property
    def scheduler(self) -> ScenarioScheduler:
        return self._scheduler

    @property
    def scenarios(self) -> List[VirtualScenario]:
        warnings.warn("Deprecated: use scheduler.scenarios instead", DeprecationWarning)
        return list(self._scheduler.discovered)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._scheduler!r})"


class _ScenarioEvent(Event):
    def __init__(self, scenario_result: ScenarioResult) -> None:
        self._scenario_result = scenario_result

    @property
    def scenario_result(self) -> ScenarioResult:
        return self._scenario_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._scenario_result!r})"


class ScenarioSkippedEvent(_ScenarioEvent):
    pass


class ScenarioFailedEvent(_ScenarioEvent):
    pass


class ScenarioRunEvent(_ScenarioEvent):
    pass


class ScenarioPassedEvent(_ScenarioEvent):
    pass


class _StepEvent(Event):
    def __init__(self, step_result: StepResult) -> None:
        self._step_result = step_result

    @property
    def step_result(self) -> StepResult:
        return self._step_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._step_result!r})"


class StepRunEvent(_StepEvent):
    pass


class StepFailedEvent(_StepEvent):
    pass


class StepPassedEvent(_StepEvent):
    pass


class ExceptionRaisedEvent(Event):
    def __init__(self, exc_info: ExcInfo) -> None:
        self._exc_info = exc_info

    @property
    def exc_info(self) -> ExcInfo:
        return self._exc_info

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._exc_info!r})"


class ScenarioReportedEvent(Event):
    def __init__(self, aggregated_result: AggregatedResult) -> None:
        self._aggregated_result = aggregated_result

    @property
    def aggregated_result(self) -> AggregatedResult:
        return self._aggregated_result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._aggregated_result!r}"


class CleanupEvent(Event):
    def __init__(self, report: Report) -> None:
        self._report = report

    @property
    def report(self) -> Report:
        return self._report

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._report!r})"


__all__ = ("Event", "ConfigLoadedEvent", "ArgParseEvent", "ArgParsedEvent",
           "StartupEvent", "ScenarioRunEvent", "ScenarioSkippedEvent",
           "ScenarioFailedEvent", "ScenarioPassedEvent",
           "StepRunEvent", "StepFailedEvent", "StepPassedEvent", "ExceptionRaisedEvent",
           "ScenarioReportedEvent", "CleanupEvent",)
