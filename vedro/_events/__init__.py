from argparse import ArgumentParser, Namespace
from typing import List

from .._core._virtual_scenario import VirtualScenario
from .._core._virtual_step import VirtualStep
from ._event import Event


class ArgParseEvent(Event):
    def __init__(self, arg_parser: ArgumentParser) -> None:
        self._arg_parser = arg_parser

    @property
    def arg_parser(self) -> ArgumentParser:
        return self._arg_parser


class ArgParsedEvent(Event):
    def __init__(self, args: Namespace) -> None:
        self._args = args

    @property
    def args(self) -> Namespace:
        return self._args


class StartupEvent(Event):
    def __init__(self, scenarios: List[VirtualScenario]) -> None:
        self._scenarios = scenarios

    @property
    def scenarios(self) -> List[VirtualScenario]:
        return self._scenarios


class ScenarioSkipEvent(Event):
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario


class ScenarioRunEvent(Event):
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario


class ScenarioFailEvent(Event):
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario


class ScenarioPassEvent(Event):
    def __init__(self, scenario: VirtualScenario) -> None:
        self._scenario = scenario

    @property
    def scenario(self) -> VirtualScenario:
        return self._scenario


class StepFailEvent(Event):
    def __init__(self, step: VirtualStep) -> None:
        self._step = step

    @property
    def step(self) -> VirtualStep:
        return self._step


class StepPassEvent(Event):
    def __init__(self, step: VirtualStep) -> None:
        self._step = step

    @property
    def step(self) -> VirtualStep:
        return self._step


class CleanupEvent(Event):
    pass


__all__ = ("Event", "ArgParseEvent", "ArgParsedEvent", "StartupEvent",
           "ScenarioSkipEvent", "ScenarioRunEvent", "ScenarioFailEvent", "ScenarioPassEvent",
           "StepFailEvent", "StepPassEvent", "CleanupEvent",)
