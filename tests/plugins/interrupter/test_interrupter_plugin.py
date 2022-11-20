import signal
from typing import Callable
from unittest.mock import Mock

import pytest
from _pytest.python_api import raises
from baby_steps import given, then, when

from vedro.core import Dispatcher, Event
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.core.scenario_runner import Interrupted
from vedro.events import CleanupEvent, ScenarioRunEvent, ScenarioSkippedEvent, StartupEvent
from vedro.plugins.interrupter import InterrupterPluginTriggered

from ._utils import (
    HANDLE_SIGNAL,
    dispatcher,
    fire_arg_parsed_event,
    fire_scenario_reported_event,
    interrupter,
    make_aggregated_result,
    make_scenario_result,
    sig_handler_,
)

__all__ = ("dispatcher", "interrupter", "sig_handler_",)  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result().mark_passed()),
    lambda: ScenarioRunEvent(make_scenario_result().mark_failed()),
    lambda: ScenarioSkippedEvent(make_scenario_result().mark_skipped()),
])
async def test_scenario_run_no_fail_fast(get_event: Callable[[], Event], *,
                                         dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=False)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = get_event()

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result().mark_passed()),
    lambda: ScenarioRunEvent(make_scenario_result().mark_failed()),
    lambda: ScenarioSkippedEvent(make_scenario_result().mark_skipped()),
])
async def test_scenario_run_failed_fail_fast(get_event: Callable[[], Event], *,
                                             dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = get_event()

    with when, raises(BaseException) as exc:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == "Stop after first failed scenario"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result().mark_passed()),
    lambda: ScenarioRunEvent(make_scenario_result().mark_failed()),
    lambda: ScenarioSkippedEvent(make_scenario_result().mark_skipped()),
])
async def test_scenario_run_passed_fail_fast(get_event: Callable[[], Event], *,
                                             dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scenario_result = make_scenario_result().mark_passed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = get_event()

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result().mark_passed()),
    lambda: ScenarioRunEvent(make_scenario_result().mark_failed()),
    lambda: ScenarioSkippedEvent(make_scenario_result().mark_skipped()),
])
async def test_scenario_run_skipped_fail_fast(get_event: Callable[[], Event], *,
                                              dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scenario_result = make_scenario_result().mark_skipped()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = get_event()

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_signal_handler(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

    with when, raises(BaseException) as exc:
        signal.raise_signal(HANDLE_SIGNAL)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == f"Stop after signal {HANDLE_SIGNAL!r} received"

        assert len(sig_handler_.mock_calls) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_signal_handler_no_fail_fast(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=False)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

    with when:
        signal.raise_signal(HANDLE_SIGNAL)

    with then:
        assert len(sig_handler_.mock_calls) == 1


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_signal_handler_cleanup(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scheduler = Scheduler([])
        await dispatcher.fire(StartupEvent(scheduler))

        event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert signal.getsignal(HANDLE_SIGNAL) == sig_handler_


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_cleanup(sig_handler_: Mock, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=False)

        event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert signal.getsignal(HANDLE_SIGNAL) == sig_handler_
