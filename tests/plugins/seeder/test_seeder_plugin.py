from typing import Callable, List
from unittest.mock import Mock, call, patch
from uuid import uuid4

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.core import Report, ScenarioResult
from vedro.events import CleanupEvent, StartupEvent
from vedro.plugins.seeder import Seeder, SeederPlugin, StandardRandomGenerator

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_startup_event,
    make_scenario_result,
    make_vscenario,
    run_scenarios,
    seeder,
)

__all__ = ("dispatcher", "seeder")  # fixtures


SEED_INITIAL = "17b81c91"
RAND_DISCOVERED = [
    [18047, 912055, 192748],
    [167430, 692919, 345483],
    [429020, 174720, 28870],
]
RAND_SCHEDULED = [
    [18047, 912055, 192748],
    [167430, 692919, 345483],
    [429020, 174720, 28870],
]


async def test_no_seed(*, dispatcher: Dispatcher):
    with given:
        random_ = Mock(wraps=StandardRandomGenerator())
        seeder = SeederPlugin(Seeder, random=random_)
        seeder.subscribe(dispatcher)

        with patch("uuid.uuid4", return_value=uuid4()) as patched:
            await fire_arg_parsed_event(dispatcher)

        startup_event = StartupEvent(Scheduler([]))

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert random_.mock_calls == [
            call.set_seed(str(patched.return_value))
        ]


async def test_seed(*, dispatcher: Dispatcher):
    with given:
        random_ = Mock(wraps=StandardRandomGenerator())
        seeder = SeederPlugin(Seeder, random=random_)
        seeder.subscribe(dispatcher)

        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        startup_event = StartupEvent(Scheduler([]))

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert random_.mock_calls == [
            call.set_seed(SEED_INITIAL)
        ]


async def test_run_discovered(*, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenarios = [
            make_vscenario("scenario-1.py"),
            make_vscenario("scenario-2.py"),
        ]
        scheduler = Scheduler(scenarios=scenarios)
        await fire_startup_event(dispatcher, scheduler)

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_DISCOVERED[0][0], RAND_DISCOVERED[1][0]]


@pytest.mark.parametrize("index", [0, 1])
async def test_run_discovered_subset(index: int, *, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenarios = [
            make_vscenario("scenario-1.py"),
            make_vscenario("scenario-2.py")
        ]
        await fire_startup_event(dispatcher, Scheduler(scenarios))
        scheduler = Scheduler([scenarios[index]])

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_DISCOVERED[index][0]]


async def test_run_discovered_and_rescheduled(*, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenarios = [
            make_vscenario("scenario-1.py"),
            make_vscenario("scenario-2.py"),
        ]
        scheduler = Scheduler(scenarios)
        await fire_startup_event(dispatcher, scheduler)

        scheduler.schedule(scenarios[0])

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_DISCOVERED[0][0], RAND_DISCOVERED[0][1], RAND_DISCOVERED[1][0]]


async def test_run_scheduled(*, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenarios = []
        scheduler = Scheduler(scenarios)
        await fire_startup_event(dispatcher, scheduler)

        new_scenario1 = make_vscenario("scenario-1.py")
        scheduler.schedule(new_scenario1)

        new_scenario2 = make_vscenario("scenario-2.py")
        scheduler.schedule(new_scenario2)

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_SCHEDULED[1][0], RAND_SCHEDULED[0][0]]


async def test_run_rescheduled(*, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenarios = []
        scheduler = Scheduler(scenarios)
        await fire_startup_event(dispatcher, scheduler)

        new_scenario = make_vscenario("scenario-1.py")
        scheduler.schedule(new_scenario)
        scheduler.schedule(new_scenario)

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_SCHEDULED[0][0], RAND_SCHEDULED[0][1]]


async def test_run_discovered_and_scheduled(*, seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        scenario = make_vscenario("scenario-1.py")
        scheduler = Scheduler([scenario])
        await fire_startup_event(dispatcher, scheduler)

        new_scenario = make_vscenario("scenario-2.py")
        scheduler.schedule(new_scenario)

        scheduler.schedule(scenario)
        scheduler.schedule(new_scenario)

    with when:
        generated = await run_scenarios(dispatcher, scheduler)

    with then:
        assert generated == [RAND_SCHEDULED[1][0], RAND_SCHEDULED[1][1],
                             RAND_DISCOVERED[0][0], RAND_DISCOVERED[0][1]]


@pytest.mark.parametrize("get_scenario_results", [
    lambda: [make_scenario_result().mark_passed()],
    lambda: [make_scenario_result().mark_failed()],
])
async def test_show_summary(get_scenario_results: Callable[[], List[ScenarioResult]], *,
                            seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        report = Report()
        for scenario_result in get_scenario_results():
            report.add_result(scenario_result)

        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert report.summary == [f"--seed {SEED_INITIAL}"]


@pytest.mark.parametrize("get_scenario_results", [
    lambda: [],
    lambda: [make_scenario_result()],
    lambda: [make_scenario_result().mark_skipped()],
])
async def test_dont_show_summary(get_scenario_results: Callable[[], List[ScenarioResult]], *,
                                 seeder: SeederPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, seed=SEED_INITIAL)

        report = Report()
        for scenario_result in get_scenario_results():
            report.add_result(scenario_result)

        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert report.summary == []
