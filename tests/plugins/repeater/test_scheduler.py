from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import MonotonicScenarioScheduler, ScenarioResult, VirtualScenario
from vedro.plugins.repeater import RepeaterScenarioScheduler


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


def test_scheduler():
    with given:
        scheduler = RepeaterScenarioScheduler([])

    with when:
        res = isinstance(scheduler, MonotonicScenarioScheduler)

    with then:
        assert res


def test_scheduler_no_aggregated_result():
    with given:
        scheduler = RepeaterScenarioScheduler([])

    with when, raises(Exception) as exc:
        scheduler.aggregate_results([])

    with then:
        assert exc.type is AssertionError


def test_scheduler_not_passed_failed_aggregated_result():
    with given:
        scenario_result1 = make_scenario_result().mark_skipped()
        scenario_result2 = make_scenario_result().mark_skipped()

        scheduler = RepeaterScenarioScheduler([])

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
def test_scheduler_single_aggregated_result(scenario_result: ScenarioResult):
    with given:
        scheduler = RepeaterScenarioScheduler([])

    with when:
        aggregated_result = scheduler.aggregate_results([scenario_result])

    with then:
        assert aggregated_result == scenario_result


def test_scheduler_passed_aggregated_result():
    with given:
        passed_first = make_scenario_result().mark_passed()
        passed_last = make_scenario_result().mark_passed()

        scheduler = RepeaterScenarioScheduler([])

    with when:
        aggregated_result = scheduler.aggregate_results([
            passed_first,
            passed_last,
        ])

    with then:
        assert aggregated_result == passed_last


def test_scheduler_failed_aggregated_result():
    with given:
        failed_first = make_scenario_result().mark_failed()
        passed_single = make_scenario_result().mark_passed()
        failed_last = make_scenario_result().mark_failed()

        scheduler = RepeaterScenarioScheduler([])

    with when:
        aggregated_result = scheduler.aggregate_results([
            failed_first,
            passed_single,
            failed_last,
        ])

    with then:
        assert aggregated_result == failed_last
