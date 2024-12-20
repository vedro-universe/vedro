from typing import Callable, List

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import AggregatedResult, MonotonicScenarioScheduler, ScenarioResult
from vedro.plugins.rerunner import RerunnerScenarioScheduler as Scheduler

from ._utils import make_scenario_result, scheduler

__all__ = ("scheduler",)  # fixtures


def test_inheritance(scheduler: Scheduler):
    with when:
        res = isinstance(scheduler, MonotonicScenarioScheduler)

    with then:
        assert res


def test_aggregate_nothing(scheduler: Scheduler):
    with when, raises(BaseException) as exc:
        scheduler.aggregate_results([])

    with then:
        assert exc.type is AssertionError


@pytest.mark.parametrize("get_scenario_results", [
    lambda: [make_scenario_result().mark_passed(), make_scenario_result().mark_passed()],
    lambda: [make_scenario_result().mark_failed(), make_scenario_result().mark_failed()],
    lambda: [make_scenario_result().mark_skipped(), make_scenario_result().mark_skipped()],
])
def test_aggregate_results(get_scenario_results: Callable[[], List[ScenarioResult]], *,
                           scheduler: Scheduler):
    with when:
        scenario_results = get_scenario_results()
        aggregated_result = scheduler.aggregate_results(scenario_results)

    with then:
        expected = AggregatedResult.from_existing(scenario_results[-1], scenario_results)
        assert aggregated_result == expected


def test_aggregate_2passed_1_failed(scheduler: Scheduler):
    with given:
        passed_first = make_scenario_result().mark_passed()
        failed_single = make_scenario_result().mark_failed()
        passed_last = make_scenario_result().mark_passed()

        scenario_results = [passed_first, failed_single, passed_last]

    with when:
        aggregated_result = scheduler.aggregate_results(scenario_results)

    with then:
        expected = AggregatedResult.from_existing(passed_last, scenario_results)
        assert aggregated_result == expected


def test_aggregate_2failed_1passed(scheduler: Scheduler):
    with given:
        failed_first = make_scenario_result().mark_failed()
        passed_single = make_scenario_result().mark_passed()
        failed_last = make_scenario_result().mark_failed()

        scenario_results = [failed_first, passed_single, failed_last]

    with when:
        aggregated_result = scheduler.aggregate_results(scenario_results)

    with then:
        expected = AggregatedResult.from_existing(failed_last, scenario_results)
        assert aggregated_result == expected
