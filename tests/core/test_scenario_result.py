import os
from pathlib import Path
from types import MethodType
from typing import Type
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro._core import ScenarioResult, StepResult, VirtualScenario, VirtualStep


def make_scenario_path(path: str = "", name: str = "scenario.py") -> Path:
    return Path(os.getcwd()) / "scenarios" / path / name


@pytest.fixture()
def scenario_():
    scenario = Mock(Scenario)
    scenario.__file__ = str(make_scenario_path())
    return scenario


@pytest.fixture()
def virtual_scenario(scenario_: Type[scenario_]):
    virtual_scenario = VirtualScenario(scenario_, [])
    return virtual_scenario


def test_scenario_result():
    with when:
        subject = "<subject>"
        namespace = "<namespace>"

        scenario_ = Mock(Scenario)
        scenario_.subject = subject
        scenario_.__file__ = str(make_scenario_path(namespace))
        virtual_scenario = VirtualScenario(scenario_, [])

        scenario_result = ScenarioResult(virtual_scenario)

    with then:
        assert scenario_result.scenario == virtual_scenario
        assert scenario_result.scenario_subject == subject
        assert scenario_result.scenario_namespace == scenario_result.scenario_namespace
        assert scenario_result.step_results == []
        assert scenario_result.is_passed() is False
        assert scenario_result.is_failed() is False
        assert scenario_result.is_skipped() is False
        assert scenario_result.started_at is None
        assert scenario_result.ended_at is None
        assert scenario_result.scope == {}


def test_scenario_result_mark_passed(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_passed()

    with then:
        assert res == scenario_result
        assert scenario_result.is_passed() is True


def test_scenario_result_mark_failed(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_failed()

    with then:
        assert res == scenario_result
        assert scenario_result.is_failed() is True


def test_scenario_result_mark_skipped(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_skipped()

    with then:
        assert res == scenario_result
        assert scenario_result.is_skipped() is True


def test_scenario_result_set_started_at(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        started_at = 1.0

    with when:
        res = scenario_result.set_started_at(started_at)

    with then:
        assert res == scenario_result
        assert scenario_result.started_at == started_at
        assert scenario_result.elapsed == 0.0


def test_scenario_result_set_ended_at(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        ended_at = 1.0

    with when:
        res = scenario_result.set_ended_at(ended_at)

    with then:
        assert res == scenario_result
        assert scenario_result.ended_at == ended_at
        assert scenario_result.elapsed == 0.0


def test_scenario_result_elapsed(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        started_at = 3.0
        scenario_result.set_started_at(started_at)
        ended_at = 1.0
        scenario_result.set_ended_at(ended_at)

    with when:
        res = scenario_result.elapsed

    with then:
        assert res == ended_at - started_at


def test_scenario_result_add_step_result(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        virtual_step = VirtualStep(Mock(MethodType))
        step_result = StepResult(virtual_step)

    with when:
        res = scenario_result.add_step_result(step_result)

    with then:
        assert res is None
        assert scenario_result.step_results == [step_result]


def test_scenario_result_get_step_results(*, virtual_scenario: VirtualScenario):
    with given:
        virtual_step1 = VirtualStep(Mock(MethodType))
        step_result1 = StepResult(virtual_step1)

        virtual_step2 = VirtualStep(Mock(MethodType))
        step_result2 = StepResult(virtual_step2)

        scenario_result = ScenarioResult(virtual_scenario)
        scenario_result.add_step_result(step_result1)
        scenario_result.add_step_result(step_result2)

    with when:
        step_results = scenario_result.step_results

    with then:
        assert step_results == [step_result1, step_result2]


def test_scenario_result_set_scope(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        scope = {}

    with when:
        res = scenario_result.set_scope(scope)

    with then:
        assert res is None
        assert scenario_result.scope == scope


def test_scenario_result_repr(*, virtual_scenario: VirtualScenario):
    with when:
        scenario_result = ScenarioResult(virtual_scenario)

    with then:
        assert repr(scenario_result) == f"ScenarioResult({virtual_scenario!r})"


def test_scenario_result_eq(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result1 = ScenarioResult(virtual_scenario)
        scenario_result2 = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result1 == scenario_result2

    with then:
        assert res is True


def test_scenario_result_not_eq():
    with given:
        scenario1_ = Mock(Scenario)
        scenario1_.__file__ = str(make_scenario_path())
        virtual_scenario1 = VirtualScenario(scenario1_, [])
        scenario_result1 = ScenarioResult(virtual_scenario1)

        scenario2_ = Mock(Scenario)
        scenario2_.__file__ = str(make_scenario_path())
        virtual_scenario2 = VirtualScenario(scenario2_, [])
        scenario_result2 = ScenarioResult(virtual_scenario2)

    with when:
        res = scenario_result1 == scenario_result2

    with then:
        assert res is False
