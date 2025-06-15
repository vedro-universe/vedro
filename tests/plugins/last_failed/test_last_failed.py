from typing import Tuple

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report
from vedro.core.exp.local_storage import LocalStorage
from vedro.events import CleanupEvent, StartupEvent
from vedro.plugins.last_failed import LastFailedPlugin

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_scenario_reported_event,
    last_failed,
    last_failed_storage,
    make_scenario_result,
    make_vscenario,
)

__all__ = ("dispatcher", "last_failed", "last_failed_storage",)  # fixtures


@pytest.mark.usefixtures(last_failed.__name__)
async def test_startup_without_last_failed_file(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, last_failed=True)

        scenarios = [
            make_vscenario(),
            make_vscenario(),
        ]
        scheduler = Scheduler(scenarios)
        event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(event)

    with then:
        assert list(scheduler.scheduled) == []


async def test_startup_with_last_failed_file_enabled(
    *,
    dispatcher: Dispatcher,
    last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]
):
    with given:
        _, local_storage = last_failed_storage
        await fire_arg_parsed_event(dispatcher, last_failed=True)

        last_failed_scenario, another_scenario = make_vscenario(), make_vscenario()
        scheduler = Scheduler([last_failed_scenario, another_scenario])
        event = StartupEvent(scheduler)

        await local_storage.put("last_failed", [last_failed_scenario.unique_id])

    with when:
        await dispatcher.fire(event)

    with then:
        assert list(scheduler.scheduled) == [last_failed_scenario]


async def test_startup_with_last_failed_file_disabled(
    *,
    dispatcher: Dispatcher,
    last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]
):
    with given:
        _, local_storage = last_failed_storage
        await fire_arg_parsed_event(dispatcher, last_failed=False)

        last_failed_scenario, another_scenario = make_vscenario(), make_vscenario()
        scheduler = Scheduler([last_failed_scenario, another_scenario])
        event = StartupEvent(scheduler)

        await local_storage.put("last_failed", [last_failed_scenario.unique_id])

    with when:
        await dispatcher.fire(event)

    with then:
        assert list(scheduler.scheduled) == [last_failed_scenario, another_scenario]


async def test_cleanup_with_no_failed_scenarios_reported(
    *,
    dispatcher: Dispatcher,
    last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]
):
    with given:
        _, local_storage = last_failed_storage
        await fire_arg_parsed_event(dispatcher, last_failed=True)

        cleanup_event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert await local_storage.get("last_failed") == []


async def test_cleanup_with_one_failed_scenario_reported(
    *,
    dispatcher: Dispatcher,
    last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]
):
    with given:
        _, local_storage = last_failed_storage
        await fire_arg_parsed_event(dispatcher, last_failed=True)

        failed_scenario_result = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, failed_scenario_result)

        passed_scenario_result = make_scenario_result().mark_passed()
        await fire_scenario_reported_event(dispatcher, passed_scenario_result)

        skipped_scenario_result = make_scenario_result().mark_skipped()
        await fire_scenario_reported_event(dispatcher, skipped_scenario_result)

        cleanup_event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        assert await local_storage.get("last_failed") == [
            failed_scenario_result.scenario.unique_id
        ]


async def test_cleanup_with_multiple_failed_scenarios_reported(
    *,
    dispatcher: Dispatcher,
    last_failed_storage: Tuple[LastFailedPlugin, LocalStorage]
):
    with given:
        _, local_storage = last_failed_storage
        await fire_arg_parsed_event(dispatcher, last_failed=True)

        failed_scenario_result1 = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, failed_scenario_result1)

        failed_scenario_result2 = make_scenario_result().mark_failed()
        await fire_scenario_reported_event(dispatcher, failed_scenario_result2)

        cleanup_event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(cleanup_event)

    with then:
        last_failed_scenarios = await local_storage.get("last_failed")

        assert len(last_failed_scenarios) == 2
        assert failed_scenario_result1.scenario.unique_id in last_failed_scenarios
        assert failed_scenario_result2.scenario.unique_id in last_failed_scenarios
