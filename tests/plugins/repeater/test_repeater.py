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
    ScenarioSkippedEvent,
    StartupEvent,
)
from vedro.plugins.repeater import Repeater, RepeaterPlugin
from vedro.plugins.repeater import RepeaterScenarioScheduler as Scheduler


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def repeater(dispatcher: Dispatcher) -> RepeaterPlugin:
    plugin = RepeaterPlugin(Repeater)
    plugin.subscribe(dispatcher)
    return plugin


@pytest.fixture()
def scheduler_() -> Scheduler:
    return Mock(spec=Scheduler)


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


async def fire_arg_parsed_event(dispatcher: dispatcher, repeats: int) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(repeats=repeats))
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
@pytest.mark.parametrize("repeats", [0, 1, 3])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_passed(repeats: int, *, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_passed()
        scenario_passed_event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_passed_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)] * repeats


@pytest.mark.asyncio
@pytest.mark.parametrize("repeats", [0, 1, 3])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_failed(repeats: int, *, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_failed()
        scenario_failed_event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)] * repeats


@pytest.mark.asyncio
@pytest.mark.parametrize("repeats", [0, 1])
@pytest.mark.usefixtures(repeater.__name__)
async def test_dont_repeat_skipped(repeats: int, *, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_skipped()
        scenario_skipped_event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_skipped_event)

    with then:
        assert scheduler_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.usefixtures(repeater.__name__)
async def test_dont_repeat_repeated(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=1)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_failed_event = await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("repeats", [1, 2])
@pytest.mark.usefixtures(repeater.__name__)
async def test_add_summary(repeats: int, *,  dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

        report_ = Mock(spec=Report)
        cleanup_event = CleanupEvent(report_)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report_.mock_calls == [
            call.add_summary(f"repeated x{repeats}")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(repeater.__name__)
async def test_dont_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=0)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

        report_ = Mock(spec=Report)
        cleanup_event = CleanupEvent(report_)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report_.mock_calls == []
