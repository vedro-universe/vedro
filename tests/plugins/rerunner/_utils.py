from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import monotonic_ns
from unittest.mock import Mock

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, ScenarioResult, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, ScenarioFailedEvent, StartupEvent
from vedro.plugins.rerunner import Rerunner, RerunnerPlugin
from vedro.plugins.rerunner import RerunnerScenarioScheduler as Scheduler


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def rerunner(dispatcher: Dispatcher) -> RerunnerPlugin:
    plugin = RerunnerPlugin(Rerunner)
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


def make_scenario_result():
    return ScenarioResult(make_vscenario())


async def fire_arg_parsed_event(dispatcher: Dispatcher, reruns: int) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(reruns=reruns))
    await dispatcher.fire(arg_parsed_event)


async def fire_startup_event(dispatcher: Dispatcher, scheduler: Scheduler) -> None:
    startup_event = StartupEvent(scheduler)
    await dispatcher.fire(startup_event)


async def fire_failed_event(dispatcher: Dispatcher) -> ScenarioFailedEvent:
    scenario_result = make_scenario_result().mark_failed()
    scenario_failed_event = ScenarioFailedEvent(scenario_result)
    await dispatcher.fire(scenario_failed_event)
    return scenario_failed_event
