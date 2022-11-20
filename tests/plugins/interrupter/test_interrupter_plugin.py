from typing import Callable

import pytest
from _pytest.python_api import raises
from baby_steps import given, then, when

from vedro.core import Dispatcher, Event
from vedro.core.scenario_runner import Interrupted
from vedro.events import ScenarioRunEvent, ScenarioSkippedEvent
from vedro.plugins.interrupter import InterrupterPluginTriggered

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_scenario_reported_event,
    interrupter,
    make_aggregated_result,
    make_scenario_result,
)

__all__ = ("dispatcher", "interrupter",)  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result().mark_passed()),
    lambda: ScenarioRunEvent(make_scenario_result().mark_failed()),
    lambda: ScenarioSkippedEvent(make_scenario_result().mark_skipped()),
])
async def test_scenario_run_no_fail_fast(get_event: Callable[[], Event], *, dispatcher: Dispatcher):
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
