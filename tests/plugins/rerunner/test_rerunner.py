from typing import Type, Union
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Report
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
)

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_failed_event,
    fire_startup_event,
    make_scenario_result,
    rerunner,
    scheduler_,
    sleep_,
)

__all__ = ("rerunner", "scheduler_", "dispatcher", "sleep_")  # fixtures


@pytest.mark.usefixtures(rerunner.__name__)
async def test_reruns_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, reruns=-1)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "--reruns must be >= 0"


@pytest.mark.usefixtures(rerunner.__name__)
async def test_reruns_delay_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, reruns=1, reruns_delay=-0.1)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "--reruns-delay must be >= 0.0"


@pytest.mark.usefixtures(rerunner.__name__)
async def test_reruns_delay_without_reruns_validation(dispatcher: Dispatcher):
    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, reruns=0, reruns_delay=0.1)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "--reruns-delay must be used with --reruns > 0"


@pytest.mark.parametrize("reruns", [0, 1, 3])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_rerun_failed(reruns: int, *,
                            dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=reruns)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_failed()
        scenario_failed_event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == [call.schedule(scenario_result.scenario)] * reruns
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("reruns", [0, 1, 3])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_rerun_passed(reruns: int, *,
                                 dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=reruns)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_passed()
        scenario_passed_event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_passed_event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.parametrize("reruns", [0, 1])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_rerun_skipped(reruns: int, *,
                                  dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=reruns)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_result = make_scenario_result().mark_skipped()
        scenario_skipped_event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(scenario_skipped_event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.usefixtures(rerunner.__name__)
async def test_no_additional_reruns_after_failure(dispatcher: Dispatcher,
                                                  scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=1)
        await fire_startup_event(dispatcher, scheduler_)

        scenario_failed_event = await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

    with when:
        await dispatcher.fire(scenario_failed_event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == []


@pytest.mark.parametrize(("event_cls", "reruns_delay"), [
    (ScenarioRunEvent, 0.1),
    (ScenarioSkippedEvent, 1.0)
])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_reruns_delay(event_cls: Union[Type[ScenarioRunEvent], Type[ScenarioSkippedEvent]],
                            reruns_delay: float, *, dispatcher: Dispatcher, scheduler_: Mock,
                            sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=2, reruns_delay=reruns_delay)
        await fire_startup_event(dispatcher, scheduler_)
        scenario_failed_event = await fire_failed_event(dispatcher)
        scheduler_.reset_mock()

        event = event_cls(scenario_failed_event.scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scheduler_.mock_calls == []
        assert sleep_.mock_calls == [call(reruns_delay)]


@pytest.mark.usefixtures(rerunner.__name__)
async def test_no_reruns_delay(*, dispatcher: Dispatcher, scheduler_: Mock, sleep_: AsyncMock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=2, reruns_delay=0.1)
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


@pytest.mark.usefixtures(rerunner.__name__)
async def test_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        reruns = 3
        await fire_arg_parsed_event(dispatcher, reruns=reruns)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [f"rerun 1 scenario, {reruns} times"]


@pytest.mark.parametrize(("reruns", "reruns_delay"), [
    (2, 0.1),
    (3, 1.0)
])
@pytest.mark.usefixtures(rerunner.__name__)
async def test_add_summary_with_delay(reruns: int, reruns_delay: int, *,
                                      dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=reruns, reruns_delay=reruns_delay)
        await fire_startup_event(dispatcher, scheduler_)

        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == [
            f"rerun 1 scenario, {reruns} times, with delay {reruns_delay!r}s"
        ]


@pytest.mark.usefixtures(rerunner.__name__)
async def test_dont_add_summary(dispatcher: Dispatcher, scheduler_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, reruns=0)
        await fire_startup_event(dispatcher, scheduler_)
        await fire_failed_event(dispatcher)

        report = Report()
        cleanup_event = CleanupEvent(report)

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert report.summary == []
