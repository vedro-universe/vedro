import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from types import TracebackType
from typing import Optional, cast

import pytest

from vedro import Scenario
from vedro.core import AggregatedResult, Dispatcher, ExcInfo, ScenarioResult, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent
from vedro.plugins.terminator import Terminator, TerminatorPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def terminator(dispatcher: Dispatcher) -> TerminatorPlugin:
    terminator = TerminatorPlugin(Terminator)
    terminator.subscribe(dispatcher)
    return terminator


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


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


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                no_scenarios_ok: Optional[bool] = False) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(no_scenarios_ok=no_scenarios_ok))
    await dispatcher.fire(arg_parsed_event)
