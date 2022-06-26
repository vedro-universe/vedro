from types import GeneratorType
from typing import Any, AsyncIterable, Iterator, List
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import MonotonicScenarioScheduler, ScenarioResult, VirtualScenario


def make_virtual_scenario() -> Mock:
    return Mock(spec=VirtualScenario)


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


async def aenumerate(iterable: AsyncIterable, start: int = 0) -> Iterator[Any]:
    idx = start
    async for x in iterable:
        yield idx, x
        idx += 1


@pytest.mark.parametrize("scenarios", [
    [],
    [make_virtual_scenario(), make_virtual_scenario()]
])
@pytest.mark.asyncio
async def test_iterator(scenarios: List[VirtualScenario]):
    with given:
        scheduler = MonotonicScenarioScheduler(scenarios)
        result = []

    with when:
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios


@pytest.mark.parametrize("scenarios", [
    [],
    [make_virtual_scenario(), make_virtual_scenario()]
])
def test_get_scenarios(scenarios: List[VirtualScenario]):
    with given:
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = scheduler.scenarios

    with then:
        assert isinstance(result, GeneratorType)
        assert list(result) == scenarios


@pytest.mark.asyncio
async def test_ignore_nonexisting():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        nonexisting_scenario = make_virtual_scenario()
        scheduler = MonotonicScenarioScheduler(scenarios)

        scheduler.ignore(nonexisting_scenario)

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_ignore_scenario():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

        scheduler.ignore(scenarios[0])

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == scenarios[1:]
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_ignore_repeated_scenario():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)
        scheduler.schedule(scenarios[0])

        scheduler.ignore(scenarios[0])

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == [scenarios[-1]]
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_ignore_repeated_scenario_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario(), make_virtual_scenario()]
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


@pytest.mark.asyncio
async def test_ignore_repeated_next_scenario_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario(), make_virtual_scenario()]
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


@pytest.mark.asyncio
async def test_ignore_scenario_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario(), make_virtual_scenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.ignore(scenarios[1])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[2]]


@pytest.mark.asyncio
async def test_schedule_new():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        new_scenario = make_virtual_scenario()
        scheduler = MonotonicScenarioScheduler(scenarios)

        scheduler.schedule(new_scenario)

    with when:
        result = []
        async for scenario in scheduler:
            result.append(scenario)

    with then:
        assert result == [new_scenario] + scenarios
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_schedule_new_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        new_scenario = make_virtual_scenario()
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(new_scenario)
            result.append(scenario)

    with then:
        assert result == [scenarios[0], new_scenario, scenarios[1]]
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_schedule_iterated_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[0])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[0], scenarios[1]]
        assert list(scheduler.scenarios) == scenarios


@pytest.mark.asyncio
async def test_schedule_not_iterated_while_iterating():
    with given:
        scenarios = [make_virtual_scenario(), make_virtual_scenario()]
        scheduler = MonotonicScenarioScheduler(scenarios)

    with when:
        result = []
        async for idx, scenario in aenumerate(scheduler):
            if idx == 0:
                scheduler.schedule(scenarios[1])
            result.append(scenario)

    with then:
        assert result == [scenarios[0], scenarios[1], scenarios[1]]
        assert list(scheduler.scenarios) == scenarios


def test_aggregate_nothing():
    with given:
        scheduler = MonotonicScenarioScheduler([])

    with when, raises(BaseException) as exc:
        scheduler.aggregate_results([])

    with then:
        assert exc.type is AssertionError


@pytest.mark.parametrize("scenario_results", [
    (make_scenario_result().mark_passed(), make_scenario_result().mark_passed()),
    (make_scenario_result().mark_failed(), make_scenario_result().mark_failed()),
    (make_scenario_result().mark_skipped(), make_scenario_result().mark_skipped()),
])
def test_aggreate_results(scenario_results: List[ScenarioResult]):
    with given:
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
