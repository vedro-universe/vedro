import asyncio
from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
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
    StartupEvent,
)
from vedro.plugins.rerunner import Rerunner, RerunnerPlugin
from vedro.plugins.rerunner import RerunnerScenarioScheduler as Scheduler
from vedro.plugins.rerunner._rerunner import SleepType


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def sleep_() -> SleepType:
    return AsyncMock(spec=asyncio.sleep)


@pytest.fixture()
def rerunner(dispatcher: Dispatcher, sleep_: SleepType) -> RerunnerPlugin:
    plugin = RerunnerPlugin(Rerunner, sleep=sleep_)
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


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


def make_config() -> ConfigType:
    class TestConfig(Config):
        class Registry(Config.Registry):
            ScenarioScheduler = Factory[ScenarioScheduler](MonotonicScenarioScheduler)

    return TestConfig


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                reruns: int, reruns_delay: float = 0.0) -> None:
    config_loaded_event = ConfigLoadedEvent(Path(), make_config())
    await dispatcher.fire(config_loaded_event)

    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(reruns=reruns, reruns_delay=reruns_delay))
    await dispatcher.fire(arg_parsed_event)


async def fire_startup_event(dispatcher: Dispatcher, scheduler: Scheduler) -> None:
    startup_event = StartupEvent(scheduler)
    await dispatcher.fire(startup_event)


async def fire_failed_event(dispatcher: Dispatcher) -> ScenarioFailedEvent:
    scenario_result = make_scenario_result().mark_failed()
    scenario_failed_event = ScenarioFailedEvent(scenario_result)
    await dispatcher.fire(scenario_failed_event)
    return scenario_failed_event
