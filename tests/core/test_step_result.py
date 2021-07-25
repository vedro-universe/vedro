from types import MethodType
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro._core import ExcInfo, StepResult, VirtualStep


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
        assert step_result.step_name == method_.__name__
        assert step_result.is_passed() is False
        assert step_result.is_failed() is False
        assert step_result.started_at is None
        assert step_result.ended_at is None
        assert step_result.exc_info is None
        assert repr(step_result) == f"StepResult({virtual_step!r})"


def test_step_result_mark_passed(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        res = step_result.mark_passed()

    with then:
        assert res == step_result
        assert step_result.is_passed() is True


def test_step_result_mark_failed(*, virtual_step: VirtualStep):
    with given:
        step_result = StepResult(virtual_step)

    with when:
        res = step_result.mark_failed()

    with then:
        assert res == step_result
        assert step_result.is_failed() is True


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
