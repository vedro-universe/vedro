import asyncio
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from typing import Optional
from unittest.mock import AsyncMock, Mock

import pytest

from vedro import Scenario
from vedro.core import (
    Config,
    ConfigType,
    Dispatcher,
    Factory,
    MonotonicScenarioScheduler,
    ScenarioResult,
    ScenarioScheduler,
    VirtualScenario,
)
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    ConfigLoadedEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StartupEvent,
)
from vedro.plugins.repeater import Repeater, RepeaterPlugin
from vedro.plugins.repeater import RepeaterScenarioScheduler as Scheduler
from vedro.plugins.repeater._repeater import SleepType


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def sleep_() -> SleepType:
    return AsyncMock(spec=asyncio.sleep)


@pytest.fixture()
def repeater(dispatcher: Dispatcher, sleep_: SleepType) -> RepeaterPlugin:
    plugin = RepeaterPlugin(Repeater, sleep=sleep_)
    plugin.subscribe(dispatcher)
    return plugin


@pytest.fixture()
def scheduler() -> Scheduler:
    return Scheduler([])


@pytest.fixture()
def scheduler_() -> Scheduler:
    return Mock(spec=Scheduler)


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result(scenario: Optional[VirtualScenario] = None) -> ScenarioResult:
    if scenario is None:
        scenario = make_vscenario()
    return ScenarioResult(scenario)


def make_config() -> ConfigType:
    class TestConfig(Config):
        class Registry(Config.Registry):
            ScenarioScheduler = Factory[ScenarioScheduler](MonotonicScenarioScheduler)

    return TestConfig


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                repeats: int,
                                repeats_delay: float = 0.0,
                                fail_fast_on_repeat: bool = False) -> None:
    config_loaded_event = ConfigLoadedEvent(Path(), make_config())
    await dispatcher.fire(config_loaded_event)

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(
        repeats=repeats,
        repeats_delay=repeats_delay,
        fail_fast_on_repeat=fail_fast_on_repeat,
    ))
    await dispatcher.fire(arg_parsed_event)


async def fire_startup_event(dispatcher: Dispatcher, scheduler: Scheduler) -> None:
    startup_event = StartupEvent(scheduler)
    await dispatcher.fire(startup_event)


async def fire_passed_event(dispatcher: Dispatcher) -> ScenarioResult:
    scenario_result = make_scenario_result().mark_passed()
    scenario_passed_event = ScenarioPassedEvent(scenario_result)
    await dispatcher.fire(scenario_passed_event)
    return scenario_result


async def fire_failed_event(dispatcher: Dispatcher) -> ScenarioResult:
    scenario_result = make_scenario_result().mark_failed()
    scenario_failed_event = ScenarioFailedEvent(scenario_result)
    await dispatcher.fire(scenario_failed_event)
    return scenario_result
