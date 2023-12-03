from typing import Callable
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Event, Report, ScenarioResult
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioSkippedEvent,
)

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_failed_event,
    fire_passed_event,
    fire_startup_event,
    make_scenario_result,
    repeater,
    scheduler_,
    sleep_,
)

__all__ = ("dispatcher", "repeater", "scheduler_", "sleep_")  # fixtures


@pytest.mark.parametrize("repeats", [2, 3])
@pytest.mark.parametrize("get_event", [
    lambda scn_result: ScenarioPassedEvent(scn_result.mark_passed()),
    lambda scn_result: ScenarioFailedEvent(scn_result.mark_failed()),
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat(repeats: int, get_event: Callable[[ScenarioResult], Event], *,
                      dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result()
        scenario_event = get_event(scenario_result)

    with when:
        await dispatcher.fire(scenario_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)]
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("get_event", [
    lambda scn_result: ScenarioPassedEvent(scn_result.mark_passed()),
    lambda scn_result: ScenarioFailedEvent(scn_result.mark_failed()),
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_single_repeat_fired(get_event: Callable[[ScenarioResult], Event], *,
                                   dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result1 = await fire_passed_event(dispatcher)
        scenario_result2 = make_scenario_result(scenario_result1.scenario)

        scenario_event = get_event(scenario_result2)
        scheduler_.reset_mock()

    with when:
        await dispatcher.fire(scenario_event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("repeats", [3, 4])
@pytest.mark.parametrize("get_event", [
    lambda scn_result: ScenarioPassedEvent(scn_result.mark_passed()),
    lambda scn_result: ScenarioFailedEvent(scn_result.mark_failed()),
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_multiple_repeat_fired(repeats: int, get_event: Callable[[ScenarioResult], Event], *,
                                     dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result1 = await fire_passed_event(dispatcher)
        scenario_result2 = make_scenario_result(scenario_result1.scenario)

        scenario_event = get_event(scenario_result2)
        scheduler_.reset_mock()

    with when:
        await dispatcher.fire(scenario_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result2.scenario)]
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("repeats", [1, 2])
@pytest.mark.usefixtures(repeater.__name__)
async def test_dont_repeat_skipped(repeats: int, *,
                                   dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_skipped()
        scenario_skipped_event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_skipped_event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.parametrize(("repeats", "repeats_delay"), [
    (2, 0.1),
    (3, 1.0)
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_with_delay(repeats: int, repeats_delay: float, *,
                                 dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats, repeats_delay=repeats_delay)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_passed()
        scenario_passed_event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_passed_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)]
        assert sleep_.mock_calls == [call(repeats_delay)]


@pytest.mark.parametrize("repeats", [2, 3])
@pytest.mark.usefixtures(repeater.__name__)
async def test_add_summary(repeats: int, *,  dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [f"repeated x{repeats}"]


@pytest.mark.parametrize(("repeats", "repeats_delay"), [
    (2, 0.1),
    (3, 1)
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_add_summary_with_delay(repeats: int, repeats_delay: int, *,
                                      dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=repeats, repeats_delay=repeats_delay)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [f"repeated x{repeats} with delay {repeats_delay!r}s"]


@pytest.mark.usefixtures(repeater.__name__)
async def test_dont_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=1)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=0)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--repeats must be >= 1"


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_delay_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=2, repeats_delay=-0.001)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--repeats-delay must be >= 0.0"


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeat_delay_without_repeats_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=1, repeats_delay=0.1)

    with then:
        assert exc_info.type is ValueError
