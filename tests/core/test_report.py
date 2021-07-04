from math import isclose
from unittest.mock import Mock

from baby_steps import given, then, when

from vedro._core import Report, ScenarioResult, VirtualScenario


def make_scenario_result() -> ScenarioResult:
    scenario_ = Mock(VirtualScenario)
    return ScenarioResult(scenario_)


def test_report_defaults():
    with when:
        report = Report()

    with then:
        assert report.total == 0
        assert report.passed == 0
        assert report.failed == 0
        assert report.skipped == 0
        assert report.elapsed == 0.0


def test_report_passed():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_passed()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 1
        assert report.failed == 0
        assert report.skipped == 0


def test_report_failed():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_failed()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 0
        assert report.failed == 1
        assert report.skipped == 0


def test_report_skipped():
    with given:
        report = Report()
        scenario_result = make_scenario_result().mark_skipped()

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert report.total == 1
        assert report.passed == 0
        assert report.failed == 0
        assert report.skipped == 1


def test_report_elapsed():
    with given:
        report = Report()
        scenario_result = make_scenario_result()
        scenario_result.set_started_at(1.0)
        scenario_result.set_ended_at(3.0)

    with when:
        res = report.add_result(scenario_result)

    with then:
        assert res is None
        assert isclose(report.elapsed, 2.0)


def test_report_eq():
    with given:
        report1 = Report()
        report2 = Report()

    with when:
        res = report1 == report2

    with then:
        assert res is True


def test_report_eq_with_same_results():
    with given:
        scenario_result1 = make_scenario_result().mark_passed()
        scenario_result2 = make_scenario_result().mark_failed()

        report1 = Report()
        report1.add_result(scenario_result1)
        report1.add_result(scenario_result2)

        report2 = Report()
        report2.add_result(scenario_result1)
        report2.add_result(scenario_result2)

    with when:
        res = report1 == report2

    with then:
        assert res is True


def test_report_eq_with_diff_results():
    with given:
        scenario_result1 = make_scenario_result().mark_passed()
        scenario_result2 = make_scenario_result().mark_failed()
        scenario_result3 = make_scenario_result().mark_failed()

        report1 = Report()
        report1.add_result(scenario_result1)
        report1.add_result(scenario_result2)

        report2 = Report()
        report2.add_result(scenario_result1)
        report2.add_result(scenario_result3)

    with when:
        res = report1 == report2

    with then:
        assert res is False


def test_report_summary_default():
    with given:
        report = Report()

    with when:
        res = report.summary

    with then:
        assert res == []


def test_report_add_summary():
    with given:
        report = Report()

    with when:
        res = report.add_summary("summary")

    with then:
        assert res is None


def test_report_get_summary():
    with given:
        report = Report()
        summary = "<summary>"
        report.add_summary(summary)

    with when:
        res = report.summary

    with then:
        assert res == [summary]
