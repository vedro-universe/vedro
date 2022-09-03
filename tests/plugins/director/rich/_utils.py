import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Any, Optional
from unittest.mock import Mock

import pytest
from rich.console import Console

from vedro import Config, Scenario
from vedro.core import AggregatedResult, Dispatcher, ExcInfo, ScenarioResult, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorPlugin, RichReporter, RichReporterPlugin
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
def rich_reporter(dispatcher: Dispatcher,
                  director: DirectorPlugin, printer_: Mock) -> RichReporterPlugin:
    reporter = RichReporterPlugin(RichReporter, printer_factory=lambda: printer_)
    reporter.subscribe(dispatcher)
    return reporter


@pytest.fixture()
def console_() -> Mock:
    return Mock(Console)


@pytest.fixture()
def printer(console_: Mock) -> RichPrinter:
    return RichPrinter(lambda: console_, traceback_factory=TestTraceback)


@pytest.fixture()
def exc_info() -> ExcInfo:
    try:
        raise KeyError()
    except KeyError:
        _, value, traceback = sys.exc_info()
    return ExcInfo(type(value), value, traceback)


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                verbose: int = 0,
                                show_timings: bool = RichReporter.show_timings,
                                show_paths: bool = RichReporter.show_paths,
                                tb_show_internal_calls: bool = RichReporter.tb_show_internal_calls,
                                tb_show_locals: bool = RichReporter.tb_show_locals) -> None:
    await dispatcher.fire(ConfigLoadedEvent(Path(), Config))

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    namespace = Namespace(verbose=verbose,
                          show_timings=show_timings,
                          show_paths=show_paths,
                          tb_show_internal_calls=tb_show_internal_calls,
                          tb_show_locals=tb_show_locals)
    arg_parsed_event = ArgParsedEvent(namespace)
    await dispatcher.fire(arg_parsed_event)


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result(vscenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    if vscenario is None:
        vscenario = make_vscenario()
    return ScenarioResult(vscenario)


def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])


class TestTraceback:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs

    def __eq__(self, other: Any) -> bool:
        if self.__class__ != other.__class__:
            return False
        return (self._args == other._args) and (self._kwargs == other._kwargs)
