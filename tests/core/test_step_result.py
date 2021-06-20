from types import MethodType
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro._core import ExcInfo, StepResult, VirtualStep


@pytest.fixture()
def method_():
    return Mock(MethodType)


def test_step_result(*, method_: MethodType):
    with given:
        method_.__name__ = "<name>"
        step = VirtualStep(method_)

    with when:
        step_result = StepResult(step)

    with then:
        assert step_result.step_name == method_.__name__
        assert step_result.is_passed() is False
        assert step_result.is_failed() is False
        assert step_result.started_at is None
        assert step_result.ended_at is None
        assert step_result.exc_info is None
        assert repr(step_result) == f"StepResult({step!r})"


def test_step_result_mark_passed(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result = StepResult(step)

    with when:
        res = step_result.mark_passed()

    with then:
        assert res == step_result
        assert step_result.is_passed() is True


def test_step_result_mark_failed(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result = StepResult(step)

    with when:
        res = step_result.mark_failed()

    with then:
        assert res == step_result
        assert step_result.is_failed() is True


def test_step_result_set_started_at(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result = StepResult(step)
        started_at = 1.0

    with when:
        res = step_result.set_started_at(started_at)

    with then:
        assert res is None
        assert step_result.started_at == started_at


def test_step_result_set_ended_at(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result = StepResult(step)
        ended_at = 1.0

    with when:
        res = step_result.set_ended_at(ended_at)

    with then:
        assert res is None
        assert step_result.ended_at == ended_at


def test_step_result_set_exc_info(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result = StepResult(step)
        exc_info = ExcInfo(AssertionError, AssertionError(), None)

    with when:
        res = step_result.set_exc_info(exc_info)

    with then:
        assert res is None
        assert step_result.exc_info == exc_info


def test_step_result_eq(*, method_: MethodType):
    with given:
        step = VirtualStep(method_)
        step_result1 = StepResult(step)
        step_result2 = StepResult(step)

    with when:
        res = step_result1 == step_result2

    with then:
        assert res is True


def test_step_result_not_eq():
    with given:
        step1 = VirtualStep(Mock(MethodType))
        step_result1 = StepResult(step1)
        step2 = VirtualStep(Mock(MethodType))
        step_result2 = StepResult(step2)

    with when:
        res = step_result1 == step_result2

    with then:
        assert res is False
