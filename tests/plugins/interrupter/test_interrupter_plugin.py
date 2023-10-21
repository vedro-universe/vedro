from typing import Callable, Optional

import pytest
from baby_steps import given, then, when
from pytest import raises

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
    sig_handler_,
)

__all__ = ("dispatcher", "interrupter", "sig_handler_",)  # fixtures


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
async def test_failed_count_validation(*, dispatcher: Dispatcher):
    with when, raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher, fail_fast=None, fail_after_count=0)

    with then:
        assert isinstance(exc.value, ValueError)
        assert str(exc.value) == "InterrupterPlugin: `fail_after_count` must be >= 1"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_no_fail_fast(get_event: Callable[[], Event], *, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=False, fail_after_count=None)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        event = get_event()

    with when:
        await dispatcher.fire(event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_fail_fast(get_event: Callable[[], Event], *, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, fail_fast=True, fail_after_count=None)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        event = get_event()

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == "Stop after first failed scenario"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_failed_fail_after_count1(get_event: Callable[[], Event], *, dispatcher: Dispatcher):
    with given:
        fail_after_count = 1
        await fire_arg_parsed_event(dispatcher, fail_fast=False, fail_after_count=fail_after_count)

        scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        event = get_event()

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == f"Stop after {fail_after_count} failed scenario"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_failed_no_fail_after_count2(get_event: Callable[[], Event], *,
                                           dispatcher: Dispatcher):
    with given:
        fail_after_count = 2
        await fire_arg_parsed_event(dispatcher, fail_fast=False, fail_after_count=fail_after_count)

        scenario_result1 = make_scenario_result().mark_passed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result1))

        scenario_result2 = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result2))

        event = get_event()

    with when:
        await dispatcher.fire(event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_failed_fail_after_count2(get_event: Callable[[], Event], *, dispatcher: Dispatcher):
    with given:
        fail_after_count = 2
        await fire_arg_parsed_event(dispatcher, fail_fast=False, fail_after_count=fail_after_count)

        scenario_result1 = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result1))

        scenario_result2 = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result2))

        event = get_event()

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is InterrupterPluginTriggered
        assert isinstance(exc.value, Interrupted)
        assert str(exc.value) == f"Stop after {fail_after_count} failed scenario"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize(("fail_fast", "fail_after_count"), [
    (True, None),
    (None, 1),
])
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
async def test_passed_fail_fast(get_event: Callable[[], Event],
                                fail_fast: Optional[bool], fail_after_count: Optional[int], *,
                                dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher,
                                    fail_fast=fail_fast,
                                    fail_after_count=fail_after_count)

        scenario_result = make_scenario_result().mark_passed()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        event = get_event()

    with when:
        await dispatcher.fire(event)

    with then:
        assert "no exception"


@pytest.mark.asyncio
@pytest.mark.usefixtures(interrupter.__name__)
@pytest.mark.parametrize("get_event", [
    lambda: ScenarioRunEvent(make_scenario_result()),
    lambda: ScenarioSkippedEvent(make_scenario_result()),
])
@pytest.mark.parametrize(("fail_fast", "fail_after_count"), [
    (True, None),
    (None, 1),
])
async def test_skipped_fail_fast(get_event: Callable[[], Event],
                                 fail_fast: Optional[bool], fail_after_count: Optional[int], *,
                                 dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher,
                                    fail_fast=fail_fast,
                                    fail_after_count=fail_after_count)

        scenario_result = make_scenario_result().mark_skipped()
        await fire_scenario_reported_event(dispatcher, make_aggregated_result(scenario_result))

        event = get_event()

    with when:
        await dispatcher.fire(event)

    with then:
        assert "no exception"
