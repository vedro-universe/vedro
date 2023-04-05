import signal
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Optional
from unittest.mock import Mock

import pytest

from vedro import Scenario
from vedro.core import AggregatedResult, Dispatcher, ScenarioResult, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioReportedEvent
from vedro.plugins.interrupter import Interrupter, InterrupterPlugin

HANDLE_SIGNAL = signal.SIGTERM


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def interrupter(dispatcher: Dispatcher) -> InterrupterPlugin:
    class _Interrupter(Interrupter):
        handle_signals = (HANDLE_SIGNAL,)

    interrupter = InterrupterPlugin(_Interrupter)
    interrupter.subscribe(dispatcher)
    return interrupter


@pytest.fixture()
def sig_handler_():
    orig_handler = signal.getsignal(HANDLE_SIGNAL)

    handler_ = Mock()
    signal.signal(HANDLE_SIGNAL, handler_)

    yield handler_

    signal.signal(HANDLE_SIGNAL, orig_handler)


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


async def fire_arg_parsed_event(dispatcher: Dispatcher, fail_fast: Optional[bool] = None) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(fail_fast=fail_fast))
    await dispatcher.fire(arg_parsed_event)


async def fire_scenario_reported_event(dispatcher: Dispatcher,
                                       aggregated_result: AggregatedResult) -> None:
    scenario_reported_event = ScenarioReportedEvent(aggregated_result)
    await dispatcher.fire(scenario_reported_event)
