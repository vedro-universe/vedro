from typing import Callable, Type, Union
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Event, Report, ScenarioResult
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
)
from vedro.plugins.repeater import RepeaterExecutionInterrupted

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_failed_event,
    fire_passed_event,
    fire_startup_event,
    make_exc_info,
    make_scenario_result,
    repeater,
    scheduler_,
    sleep_,
)

__all__ = ("dispatcher", "repeater", "scheduler_", "sleep_")  # fixtures


ScenarioExecuteFactory = Union[Type[ScenarioRunEvent], Type[ScenarioSkippedEvent]]


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=0)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--repeats must be >= 1"


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_delay_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=2, repeats_delay=-0.001)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--repeats-delay must be >= 0.0"


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_delay_without_repeats_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=1, repeats_delay=0.1)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--repeats-delay must be used with --repeats > 1"


@pytest.mark.usefixtures(repeater.__name__)
async def test_fail_fast_without_repeats_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc_info:
        await fire_arg_parsed_event(dispatcher, repeats=1, fail_fast_on_repeat=True)

    with then:
        assert exc_info.type is ValueError
        assert str(exc_info.value) == "--fail-fast-on-repeat must be used with --repeats > 1"


@pytest.mark.parametrize("repeats", [1, 2, 3])
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
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)] * (repeats - 1)
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


@pytest.mark.parametrize(("event_cls", "repeats_delay"), [
    (ScenarioRunEvent, 0.1),
    (ScenarioSkippedEvent, 1.0)
])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_delay(event_cls: ScenarioExecuteFactory, repeats_delay: float, *,
                             dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2, repeats_delay=repeats_delay)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

        event = event_cls(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == [call(repeats_delay)]


@pytest.mark.usefixtures(repeater.__name__)
async def test_no_repeats_delay(*, dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2, repeats_delay=0.1)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

        scenario_result = make_scenario_result()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("event_cls", [ScenarioRunEvent, ScenarioSkippedEvent])
@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_fail_fast(event_cls: ScenarioExecuteFactory, *, dispatcher: Dispatcher,
                                 scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2, fail_fast_on_repeat=True)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_failed_event(dispatcher)

        event = event_cls(make_scenario_result())

    with when, raises(BaseException) as exc_info:
        await dispatcher.fire(event)

    with then:
        assert exc_info.type is RepeaterExecutionInterrupted
        assert str(exc_info.value) == "Stop repeating scenarios after the first failure"


@pytest.mark.usefixtures(repeater.__name__)
async def test_repeats_no_fail_fast(*, dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2, fail_fast_on_repeat=True)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_passed_event(dispatcher)

        scenario_result = make_scenario_result().mark_failed()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        # no exception
        pass


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
async def test_dont_add_summary_no_repeats(dispatcher: Dispatcher, scheduler_: Mock):
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
async def test_dont_add_summary_interrupted(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, repeats=2)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        report.set_interrupted(make_exc_info(Exception()))
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
