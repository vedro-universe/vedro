import os
from pathlib import Path
from types import MethodType
from typing import Callable, Type
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import Scenario
from vedro.core import (
    MemoryArtifact,
    ScenarioResult,
    ScenarioStatus,
    StepResult,
    VirtualScenario,
    VirtualStep,
)


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


ChangeStatusType = Callable[[ScenarioResult], ScenarioResult]


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
        assert scenario_result.step_results == []
        assert scenario_result.is_passed() is False
        assert scenario_result.is_failed() is False
        assert scenario_result.is_skipped() is False
        assert scenario_result.started_at is None
        assert scenario_result.ended_at is None
        assert scenario_result.scope == {}
        assert scenario_result.status == ScenarioStatus.PENDING
        assert scenario_result.extra_details == []


def test_scenario_result_mark_passed(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_passed()

    with then:
        assert res == scenario_result
        assert scenario_result.is_passed() is True


@pytest.mark.parametrize("change_status", [
    lambda scn_result: scn_result.mark_passed(),
    lambda scn_result: scn_result.mark_failed(),
    lambda scn_result: scn_result.mark_skipped(),
])
def test_marked_scenario_result_mark_passed(change_status: ChangeStatusType, *,
                                            virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        change_status(scenario_result)

    with when, raises(BaseException) as exc:
        scenario_result.mark_passed()

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == (
            "Cannot mark scenario as passed because its status has already been set"
        )


def test_scenario_result_mark_failed(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_failed()

    with then:
        assert res == scenario_result
        assert scenario_result.is_failed() is True


@pytest.mark.parametrize("change_status", [
    lambda scn_result: scn_result.mark_passed(),
    lambda scn_result: scn_result.mark_failed(),
    lambda scn_result: scn_result.mark_skipped(),
])
def test_marked_scenario_result_mark_failed(change_status: ChangeStatusType, *,
                                            virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        change_status(scenario_result)

    with when, raises(BaseException) as exc:
        scenario_result.mark_failed()

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == (
            "Cannot mark scenario as failed because its status has already been set"
        )


def test_scenario_result_mark_skipped(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.mark_skipped()

    with then:
        assert res == scenario_result
        assert scenario_result.is_skipped() is True


@pytest.mark.parametrize("change_status", [
    lambda scn_result: scn_result.mark_passed(),
    lambda scn_result: scn_result.mark_failed(),
    lambda scn_result: scn_result.mark_skipped(),
])
def test_marked_scenario_result_mark_skipped(change_status: ChangeStatusType, *,
                                             virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        change_status(scenario_result)

    with when, raises(BaseException) as exc:
        scenario_result.mark_skipped()

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == (
            "Cannot mark scenario as skipped because its status has already been set"
        )


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
        assert repr(scenario_result) == (
            f"<ScenarioResult {virtual_scenario!r} {scenario_result.status.value}>")


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


def test_scenario_result_attach_artifact(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        artifact = MemoryArtifact("name", "text/plain", b"")

    with when:
        res = scenario_result.attach(artifact)

    with then:
        assert res is None


def test_scenario_result_attach_incorrect_artifact(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)
        artifact = {}

    with when, raises(BaseException) as exc:
        scenario_result.attach(artifact)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Expected an instance of Artifact, got dict"


def test_scenario_result_get_artifacts(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

        artifact1 = MemoryArtifact("name1", "text/plain", b"")
        scenario_result.attach(artifact1)

        artifact2 = MemoryArtifact("name2", "text/plain", b"")
        scenario_result.attach(artifact2)

    with when:
        artifacts = scenario_result.artifacts

    with then:
        assert artifacts == [artifact1, artifact2]


def test_scenario_result_add_extra_details(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

    with when:
        res = scenario_result.add_extra_details("<extra-details>")

    with then:
        assert res is None


def test_scenario_result_get_extra_details(*, virtual_scenario: VirtualScenario):
    with given:
        scenario_result = ScenarioResult(virtual_scenario)

        scenario_result.add_extra_details("<extra-detail-1>")
        scenario_result.add_extra_details("<extra-detail-2>")

    with when:
        extra_details = scenario_result.extra_details

    with then:
        assert extra_details == ["<extra-detail-1>", "<extra-detail-2>"]
