from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import MonotonicScenarioScheduler, ScenarioResult, VirtualScenario
from vedro.plugins.rerunner import RerunnerScenarioScheduler as Scheduler


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


@pytest.fixture()
def scheduler():
    return Scheduler([])


def test_scheduler(scheduler: Scheduler):
    with when:
        res = isinstance(scheduler, MonotonicScenarioScheduler)

    with then:
        assert res


def test_scheduler_no_aggregated_result(scheduler: Scheduler):
    with when, raises(BaseException) as exc:
        scheduler.aggregate_results([])

    with then:
        assert exc.type is AssertionError


def test_scheduler_not_passed_failed_aggregated_result(scheduler: Scheduler):
    with given:
        scenario_result1 = make_scenario_result().mark_skipped()
        scenario_result2 = make_scenario_result().mark_skipped()

    with when:
        aggregated_result = scheduler.aggregate_results([
            scenario_result1,
            scenario_result2,
        ])

    with then:
        assert aggregated_result == scenario_result2


@pytest.mark.parametrize("scenario_result", [
    make_scenario_result().mark_passed(),
    make_scenario_result().mark_failed(),
])
def test_scheduler_single_aggregated_result(scenario_result: ScenarioResult, *,
                                            scheduler: Scheduler):
    with when:
        aggregated_result = scheduler.aggregate_results([scenario_result])

    with then:
        assert aggregated_result == scenario_result


def test_scheduler_2passed_aggregated_result(scheduler: Scheduler):
    with given:
        passed_first = make_scenario_result().mark_passed()
        passed_last = make_scenario_result().mark_passed()

    with when:
        aggregated_result = scheduler.aggregate_results([
            passed_first,
            passed_last,
        ])

    with then:
        assert aggregated_result == passed_last


def test_scheduler_2passed_1failed_aggregated_result(scheduler: Scheduler):
    with given:
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
        assert aggregated_result == passed_last


def test_scheduler_2failed_1passed_aggregated_result(scheduler: Scheduler):
    with given:
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
        assert aggregated_result == failed_last
