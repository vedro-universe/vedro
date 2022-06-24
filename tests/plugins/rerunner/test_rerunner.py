from argparse import ArgumentParser, Namespace
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Report, ScenarioResult, VirtualScenario
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    StartupEvent,
)
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
def scheduler_() -> Scheduler:
    return Mock(spec=Scheduler)


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


async def fire_arg_parsed_event(dispatcher: dispatcher, reruns: int) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(reruns=reruns))
    await dispatcher.fire(arg_parsed_event)


async def fire_startup_event(dispatcher, scheudler: Scheduler) -> None:
    startup_event = StartupEvent(scheudler)
    await dispatcher.fire(startup_event)


async def fire_failed_event(dispatcher: Dispatcher) -> ScenarioFailedEvent:
    scenario_result = make_scenario_result().mark_failed()
    scenario_failed_event = ScenarioFailedEvent(scenario_result)
    await dispatcher.fire(scenario_failed_event)
    return scenario_failed_event


@pytest.mark.asyncio
@pytest.mark.parametrize("reruns", [0, 1, 3])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_rerun_failed(reruns: int, *, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_failed()
        scenario_failed_event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)] * reruns


@pytest.mark.asyncio
@pytest.mark.parametrize("reruns", [0, 1, 3])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_rerun_passed(reruns: int, *, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_passed()
        scenario_passed_event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_passed_event)

    with then:
        assert scheduler_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_rerun_rerunned(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=1)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_failed_event = await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(rerunner.__name__)
async def test_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        reruns = 3
        await fire_arg_parsed_event(dispatcher, reruns=reruns)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_failed_event(dispatcher)

        report_ = Mock(spec=Report)
        cleanup_event = CleanupEvent(report_)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report_.mock_calls == [
            call.add_summary(f"rerun 1 scenario, {reruns} times")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=0)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_failed_event(dispatcher)

        report_ = Mock(spec=Report)
        cleanup_event = CleanupEvent(report_)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report_.mock_calls == []
