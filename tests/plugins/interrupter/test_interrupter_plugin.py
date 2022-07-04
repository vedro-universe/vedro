from typing import Callable

import pytest
from _pytest.python_api import raises
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioResult
from vedro.events import ScenarioRunEvent
from vedro.plugins.interrupter import Interrupted

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_scenario_reported_event,
    interrupter,
    make_aggregated_result,
    make_scenario_result,
)

__all__ = ("dispatcher", "interrupter")


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_scenario_result", [
    lambda: make_scenario_result().mark_passed(),
    lambda: make_scenario_result().mark_failed(),
    lambda: make_scenario_result().mark_skipped(),
])
async def test_scenario_run_no_reported(get_scenario_result: Callable[[], ScenarioResult],
                                        *, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)
        scenario_run_event = ScenarioRunEvent(get_scenario_result())

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_scenario_run_failed_fail_fast(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = ScenarioRunEvent(make_scenario_result())

    with when, raises(BaseException) as exc:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert exc.type is Interrupted


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_scenario_result", [
    lambda: make_scenario_result().mark_passed(),
    lambda: make_scenario_result().mark_failed(),
    lambda: make_scenario_result().mark_skipped(),
])
async def test_scenario_run_no_fail_fast(get_scenario_result: Callable[[], ScenarioResult],
                                         *, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=False)

        scenario_result = get_scenario_result()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = ScenarioRunEvent(make_scenario_result())

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_scenario_result", [
    lambda: make_scenario_result().mark_passed(),
    lambda: make_scenario_result().mark_skipped(),
])
async def test_scenario_run_fail_fast(get_scenario_result: Callable[[], ScenarioResult],
                                      *, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True)

        scenario_result = get_scenario_result()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        scenario_run_event = ScenarioRunEvent(make_scenario_result())

    with when:
        await dispatcher.fire(scenario_run_event)

    with then:
        assert "no exception"
