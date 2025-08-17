from types import MethodType
from typing import Callable
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ExcInfo, MemoryArtifact, StepResult, StepStatus, VirtualStep
from vedro.core.output_capturer import CapturedOutput


@pytest.fixture()
def method_():
    return Mock(MethodType)


@pytest.fixture()
def virtual_step(method_: MethodType):
    return VirtualStep(method_)


def test_step_result(*, method_: MethodType, virtual_step: VirtualStep):
    with given:
        method_.__name__ = "<name>"

    with when:
        step_result = StepResult(virtual_step)

    with then:
        assert step_result.step == virtual_step
        assert step_result.step_name == method_.__name__
        assert step_result.is_passed() is False
        assert step_result.is_failed() is False
        assert step_result.started_at is None
        assert step_result.ended_at is None
        assert step_result.exc_info is None
        assert step_result.status == StepStatus.PENDING
        assert step_result.extra_details == []
        assert repr(step_result) == f"<StepResult {virtual_step!r} {step_result.status.value}>"


def test_step_result_mark_passed(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        res = step_result.mark_passed()

    with then:
        assert res == step_result
        assert step_result.is_passed() is True


@pytest.mark.parametrize("change_status", [
    lambda step_result: step_result.mark_passed(),
    lambda step_result: step_result.mark_failed(),
])
def test_marked_step_result_mark_passed(change_status: Callable[[StepResult], StepResult], *,
                                        virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        change_status(step_result)

    with when, raises(BaseException) as exc:
        step_result.mark_passed()

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == (
            "Cannot mark step as passed because its status has already been set"
        )


def test_step_result_mark_failed(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        res = step_result.mark_failed()

    with then:
        assert res == step_result
        assert step_result.is_failed() is True


@pytest.mark.parametrize("change_status", [
    lambda step_result: step_result.mark_passed(),
    lambda step_result: step_result.mark_failed(),
])
def test_marked_step_result_mark_failed(change_status: Callable[[StepResult], StepResult], *,
                                        virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        change_status(step_result)

    with when, raises(BaseException) as exc:
        step_result.mark_failed()

    with then:
        assert exc.type is RuntimeError
        assert str(exc.value) == (
            "Cannot mark step as failed because its status has already been set"
        )


def test_step_result_set_started_at(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        started_at = 1.0

    with when:
        res = step_result.set_started_at(started_at)

    with then:
        assert res == step_result
        assert step_result.started_at == started_at
        assert step_result.elapsed == 0.0


def test_step_result_set_ended_at(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        ended_at = 1.0

    with when:
        res = step_result.set_ended_at(ended_at)

    with then:
        assert res == step_result
        assert step_result.ended_at == ended_at
        assert step_result.elapsed == 0.0


def test_step_result_elapsed(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        started_at = 3.0
        step_result.set_started_at(started_at)
        ended_at = 1.0
        step_result.set_ended_at(ended_at)

    with when:
        res = step_result.elapsed

    with then:
        assert res == ended_at - started_at


def test_step_result_set_exc_info(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        exc_info = ExcInfo(AssertionError, AssertionError(), None)

    with when:
        res = step_result.set_exc_info(exc_info)

    with then:
        assert res == step_result
        assert step_result.exc_info == exc_info


def test_step_result_eq(*, virtual_step: VirtualStep):
    with given:
        step_result1 = StepResult(virtual_step)
        step_result2 = StepResult(virtual_step)

    with when:
        res = step_result1 == step_result2

    with then:
        assert res is True


def test_step_result_not_eq():
    with given:
        virtual_step1 = VirtualStep(Mock(MethodType))
        step_result1 = StepResult(virtual_step1)
        virtual_step2 = VirtualStep(Mock(MethodType))
        step_result2 = StepResult(virtual_step2)

    with when:
        res = step_result1 == step_result2

    with then:
        assert res is False


def test_step_result_attach_artifact(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        artifact = MemoryArtifact("name", "text/plain", b"")

    with when:
        res = step_result.attach(artifact)

    with then:
        assert res is None


def test_step_result_attach_incorrect_artifact(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        artifact = {}

    with when, raises(BaseException) as exc:
        step_result.attach(artifact)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Expected an instance of Artifact, got dict"


def test_step_result_get_artifacts(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

        artifact1 = MemoryArtifact("name1", "text/plain", b"")
        step_result.attach(artifact1)

        artifact2 = MemoryArtifact("name2", "text/plain", b"")
        step_result.attach(artifact2)

    with when:
        artifacts = step_result.artifacts

    with then:
        assert artifacts == [artifact1, artifact2]


def test_step_result_add_extra_details(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        res = step_result.add_extra_details("<extra-details>")

    with then:
        assert res is None


def test_step_result_get_extra_details(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

        step_result.add_extra_details("<extra-detail-1>")
        step_result.add_extra_details("<extra-detail-2>")

    with when:
        extra_details = step_result.extra_details

    with then:
        assert extra_details == ["<extra-detail-1>", "<extra-detail-2>"]


def test_step_result_set_captured_output(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        captured_output = CapturedOutput()

    with when:
        res = step_result.set_captured_output(captured_output)

    with then:
        assert res == step_result
        assert step_result.captured_output == captured_output


def test_step_result_get_captured_output(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)
        captured_output = CapturedOutput()
        step_result.set_captured_output(captured_output)

    with when:
        result_captured_output = step_result.captured_output

    with then:
        assert result_captured_output == captured_output


def test_step_result_get_captured_output_none(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        result_captured_output = step_result.captured_output

    with then:
        assert result_captured_output is None
