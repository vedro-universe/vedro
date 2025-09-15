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
    AggregatedResult,
    Dispatcher,
    ExcInfo,
    ScenarioResult,
    StepResult,
    VirtualScenario,
    VirtualStep,
)
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorPlugin
from vedro.plugins.director import RichReporter as RichReporter_
from vedro.plugins.director import RichReporterPlugin
from vedro.plugins.director.rich import RichPrinter


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def printer_() -> Mock:
    return Mock(RichPrinter)


@pytest.fixture()
def director(dispatcher: Dispatcher) -> DirectorPlugin:
    class _Director(Director):
        default_reporters = ["rich"]

    director = DirectorPlugin(_Director)
    director.subscribe(dispatcher)
    return director


@pytest.fixture()
def rich_reporter(dispatcher: Dispatcher,
                  director: DirectorPlugin, printer_: Mock) -> RichReporterPlugin:
    reporter = RichReporterPlugin(RichReporter_, printer_factory=lambda: printer_)
    reporter.subscribe(dispatcher)
    return reporter


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                verbose: int = 0,
                                show_scope: bool = RichReporter_.show_scope,
                                show_full_diff: bool = RichReporter_.show_full_diff,
                                # Override new default (True) to preserve test compatibility
                                show_timings: bool = False,
                                show_paths: bool = RichReporter_.show_paths,
                                show_ids: bool = RichReporter_.show_ids,
                                show_steps: bool = RichReporter_.show_steps,
                                show_scenario_spinner: bool = RichReporter_.show_scenario_spinner,
                                hide_namespaces: bool = RichReporter_.hide_namespaces,
                                tb_show_internal_calls: bool = True,
                                tb_show_locals: bool = RichReporter_.tb_show_locals,
                                no_color: bool = RichReporter_.no_color,
                                ring_bell: bool = RichReporter_.ring_bell) -> None:
    await dispatcher.fire(ConfigLoadedEvent(Path(), Config))

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    namespace = Namespace(verbose=verbose,
                          show_scope=show_scope,
                          show_full_diff=show_full_diff,
                          show_timings=show_timings,
                          show_paths=show_paths,
                          show_ids=show_ids,
                          show_steps=show_steps,
                          show_scenario_spinner=show_scenario_spinner,
                          hide_namespaces=hide_namespaces,
                          tb_show_internal_calls=tb_show_internal_calls,
                          tb_show_locals=tb_show_locals,
                          no_color=no_color,
                          ring_bell=ring_bell)
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


def make_step_result(vstep: Optional[VirtualStep] = None) -> StepResult:
    return StepResult(vstep or make_vstep())


def make_scenario_result(vscenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    return ScenarioResult(vscenario or make_vscenario())


def make_aggregated_result(scenario_result: Optional[ScenarioResult] = None) -> AggregatedResult:
    if scenario_result is None:
        scenario_result = make_scenario_result()
    return AggregatedResult.from_existing(scenario_result, [scenario_result])


def make_exc_info(exc_val: BaseException) -> ExcInfo:
    try:
        raise exc_val
    except type(exc_val):
        *_, traceback = sys.exc_info()
    return ExcInfo(type(exc_val), exc_val, cast(TracebackType, traceback))
