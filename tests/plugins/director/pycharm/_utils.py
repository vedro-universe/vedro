import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from types import TracebackType
from typing import Optional, cast
from unittest.mock import Mock

import pytest

from vedro import Config, Scenario
from vedro.core import (
    Dispatcher,
    ExcInfo,
    ScenarioResult,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorPlugin, PyCharmReporter, PyCharmReporterPlugin
from vedro.plugins.director.rich import RichPrinter


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def printer_() -> Mock:
    return Mock(RichPrinter)


@pytest.fixture()
def director(dispatcher: Dispatcher) -> DirectorPlugin:
    director = DirectorPlugin(Director)
    director.subscribe(dispatcher)
    return director


@pytest.fixture()
def pycharm_reporter(dispatcher: Dispatcher, director: DirectorPlugin,
                     printer_: Mock) -> PyCharmReporterPlugin:
    reporter = PyCharmReporterPlugin(PyCharmReporter, printer_factory=lambda: printer_)
    reporter.subscribe(dispatcher)
    return reporter


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                show_internal_calls: bool = PyCharmReporter.show_internal_calls,
                                show_skipped: bool = PyCharmReporter.show_skipped) -> None:
    await dispatcher.fire(ConfigLoadedEvent(Path(), Config))

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    namespace = Namespace(pycharm_show_internal_calls=show_internal_calls,
                          pycharm_show_skipped=show_skipped)
    arg_parsed_event = ArgParsedEvent(namespace)
    await dispatcher.fire(arg_parsed_event)


def make_vstep(name: Optional[str] = None) -> VirtualStep:
    def step(self):
        pass
    step.__name__ = name or f"step_{monotonic_ns()}"
    return VirtualStep(step)


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result(vscenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    if vscenario is None:
        vscenario = make_vscenario()
    return ScenarioResult(vscenario)


def make_step_result(vstep: Optional[VirtualStep] = None) -> StepResult:
    return StepResult(vstep or make_vstep())


def make_exc_info(exc_val: Exception) -> ExcInfo:
    try:
        raise exc_val
    except type(exc_val):
        *_, traceback = sys.exc_info()
    return ExcInfo(type(exc_val), exc_val, cast(TracebackType, traceback))
