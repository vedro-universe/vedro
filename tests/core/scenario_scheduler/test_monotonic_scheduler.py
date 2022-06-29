from types import GeneratorType
from typing import Callable, List

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import MonotonicScenarioScheduler, ScenarioResult, VirtualScenario

from ._utils import aenumerate, make_scenario_result, make_vscenario


@pytest.mark.parametrize("get_scenarios", [
    lambda: [],
    lambda: [make_vscenario(), make_vscenario()]
])
@pytest.mark.asyncio
async def test_iterator(get_scenarios: Callable[[], List[VirtualScenario]]):
    with given:
        scenarios = get_scenarios()
        scheduler = MonotonicScenarioScheduler(scenarios)
        result = []

    with when:
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios


@pytest.mark.parametrize("get_scenarios", [
    lambda: [],
    lambda: [make_vscenario(), make_vscenario()]
])
def test_get_discovered(get_scenarios: Callable[[], List[VirtualScenario]]):
    with given:
        scenarios = get_scenarios()
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = scheduler.discovered

    with then:
        assert isinstance(result, GeneratorType)
        assert list(result) == scenarios


@pytest.mark.asyncio
async def test_ignore_nonexisting():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

        nonexisting_scenario = make_vscenario()
        scheduler.ignore(nonexisting_scenario)

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios
        assert list(scheduler.scheduled) == scenarios
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_ignore_scenario():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

        scheduler.ignore(scenarios[0])

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios[1:]
        assert list(scheduler.scheduled) == scenarios[1:]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_ignore_repeated_scenario():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)
        scheduler.schedule(scenarios[0])

        scheduler.ignore(scenarios[0])

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == [scenarios[-1]]
        assert list(scheduler.scheduled) == [scenarios[-1]]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_ignore_repeated_scenario_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[2])
                scheduler.ignore(scenarios[2])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[1]]
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1]]


@pytest.mark.asyncio
async def test_ignore_repeated_next_scenario_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[0])
                scheduler.schedule(scenarios[0])
            if idx == 1:
                scheduler.ignore(scenarios[0])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[0], scenarios[1], scenarios[2]]
        assert list(scheduler.scheduled) == [scenarios[1], scenarios[2]]


@pytest.mark.asyncio
async def test_ignore_scenario_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.ignore(scenarios[1])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[2]]
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[2]]


@pytest.mark.asyncio
async def test_schedule_new():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

        new_scenario = make_vscenario()
        scheduler.schedule(new_scenario)

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == [new_scenario] + scenarios
        assert list(scheduler.discovered) == scenarios
        assert list(scheduler.scheduled) == [new_scenario] + scenarios


@pytest.mark.asyncio
async def test_schedule_new_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)
        new_scenario = make_vscenario()

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(new_scenario)
            result.append(scenario)

    with then:
        assert result == [scenarios[0], new_scenario, scenarios[1]]
        assert list(scheduler.scheduled) == [new_scenario, scenarios[0], scenarios[1]]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_schedule_iterated_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[0])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[0], scenarios[1]]
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[0], scenarios[1]]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_schedule_not_iterated_while_iterating():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[1])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[1], scenarios[1]]
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1], scenarios[1]]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_schedule_while_iterating_scheduled():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        for idx, scenario in enumerate(scheduler.scheduled):
            if idx == 0:
                scheduler.schedule(scenarios[-1])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[1], scenarios[1]]
        assert list(scheduler.scheduled) == [scenarios[0], scenarios[1], scenarios[1]]
        assert list(scheduler.discovered) == scenarios


@pytest.mark.asyncio
async def test_ignore_while_iterating_scheduled():
    with given:
        scenarios = [make_vscenario(), make_vscenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when, raises(BaseException) as exc:
        for idx, scenario in enumerate(scheduler.scheduled):
            if idx == 0:
                scheduler.ignore(scenarios[-1])

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == "OrderedDict mutated during iteration"

        assert list(scheduler.scheduled) == [scenarios[0]]
        assert list(scheduler.discovered) == scenarios


def test_aggregate_nothing():
    with given:
        scheduler = MonotonicScenarioScheduler([])

    with when, raises(BaseException) as exc:
        scheduler.aggregate_results([])

    with then:
        assert exc.type is AssertionError


@pytest.mark.parametrize("get_scenario_results", [
    lambda: [make_scenario_result().mark_passed(), make_scenario_result().mark_passed()],
    lambda: [make_scenario_result().mark_failed(), make_scenario_result().mark_failed()],
    lambda: [make_scenario_result().mark_skipped(), make_scenario_result().mark_skipped()],
])
def test_aggreate_results(get_scenario_results: Callable[[], List[ScenarioResult]]):
    with given:
        scenario_results = get_scenario_results()
        scheduler = MonotonicScenarioScheduler([])

    with when:
        aggregated_result = scheduler.aggregate_results(scenario_results)

    with then:
        assert aggregated_result == scenario_results[0]


def test_aggregate_2passed_1_failed():
    with given:
        scheduler = MonotonicScenarioScheduler([])

        passed_first = make_scenario_result().mark_passed()
        failed_single = make_scenario_result().mark_failed()
        passed_last = make_scenario_result().mark_passed()

    with when:
        aggregated_result = scheduler.aggregate_results([
            passed_first,
            failed_single,
            passed_last,
        ])

    with then:
        assert aggregated_result == failed_single


def test_aggregate_2failed_1passed():
    with given:
        scheduler = MonotonicScenarioScheduler([])

        failed_first = make_scenario_result().mark_failed()
        passed_single = make_scenario_result().mark_passed()
        failed_last = make_scenario_result().mark_failed()

    with when:
        aggregated_result = scheduler.aggregate_results([
            failed_first,
            passed_single,
            failed_last,
        ])

    with then:
        assert aggregated_result == failed_first


def test_repr():
    with given:
        scheduler = MonotonicScenarioScheduler([])

    with when:
        res = repr(scheduler)

    with then:
        assert res == "<MonotonicScenarioScheduler>"
