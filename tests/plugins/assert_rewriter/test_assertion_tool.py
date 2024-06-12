import pytest
from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.plugins.assert_rewriter import AssertionTool
from vedro.plugins.assert_rewriter import CompareOperator as Op


@pytest.fixture
def assert_() -> AssertionTool:
    return AssertionTool()


def test_truthy_pass(*, assert_: AssertionTool):
    with given:
        actual = True

    with when:
        res = assert_.assert_truthy(actual)

    with then:
        assert res is True


def test_truthy_fail(*, assert_: AssertionTool):
    with given:
        actual = False

    with when, raises(Exception) as exc:
        assert_.assert_truthy(actual)

    with then:
        assert exc.type == AssertionError
        assert str(exc.value) == ""

        assert assert_.get_left(exc.value) == actual
        assert assert_.get_right(exc.value) == Nil
        assert assert_.get_operator(exc.value) == Nil
        assert assert_.get_message(exc.value) == Nil


def test_truthy_fail_with_message(*, assert_: AssertionTool):
    with given:
        actual = False
        message = "<message>"

    with when, raises(Exception) as exc:
        assert_.assert_truthy(actual, message)

    with then:
        assert exc.type == AssertionError
        assert str(exc.value) == message

        assert assert_.get_left(exc.value) == actual
        assert assert_.get_right(exc.value) == Nil
        assert assert_.get_operator(exc.value) == Nil
        assert assert_.get_message(exc.value) == message


@pytest.mark.parametrize(("method", "actual", "expected"), [
    (AssertionTool.assert_equal, 1, 1),
    (AssertionTool.assert_not_equal, 1, 2),

    (AssertionTool.assert_less, 1, 2),
    (AssertionTool.assert_less_equal, 1, 1),
    (AssertionTool.assert_greater, 2, 1),
    (AssertionTool.assert_greater_equal, 2, 2),

    (AssertionTool.assert_is, 1, 1),
    (AssertionTool.assert_is_not, 1, 2),

    (AssertionTool.assert_in, 1, [1]),
    (AssertionTool.assert_not_in, 1, [2]),
])
def test_compare_pass(method, actual, expected, *, assert_: AssertionTool):
    with when:
        res = getattr(assert_, method.__name__)(actual, expected)

    with then:
        assert res is True


@pytest.mark.parametrize(("method", "actual", "expected", "operator"), [
    (AssertionTool.assert_equal, 1, 2, Op.EQUAL),
    (AssertionTool.assert_not_equal, 1, 1, Op.NOT_EQUAL),

    (AssertionTool.assert_less, 2, 1, Op.LESS),
    (AssertionTool.assert_less_equal, 2, 1, Op.LESS_EQUAL),
    (AssertionTool.assert_greater, 1, 2, Op.GREATER),
    (AssertionTool.assert_greater_equal, 1, 2, Op.GREATER_EQUAL),

    (AssertionTool.assert_is, 1, 2, Op.IS),
    (AssertionTool.assert_is_not, 1, 1, Op.IS_NOT),

    (AssertionTool.assert_in, 1, [2], Op.IN),
    (AssertionTool.assert_not_in, 1, [1], Op.NOT_IN),
])
def test_compare_fail(method, actual, expected, operator, *, assert_: AssertionTool):
    with when, raises(Exception) as exc:
        getattr(assert_, method.__name__)(actual, expected)

    with then:
        assert exc.type == AssertionError
        assert str(exc.value) == ""

        assert assert_.get_left(exc.value) == actual
        assert assert_.get_right(exc.value) == expected
        assert assert_.get_operator(exc.value) == operator
        assert assert_.get_message(exc.value) == Nil


@pytest.mark.parametrize(("method", "actual", "expected", "operator"), [
    (AssertionTool.assert_equal, 1, 2, Op.EQUAL),
    (AssertionTool.assert_not_equal, 1, 1, Op.NOT_EQUAL),

    (AssertionTool.assert_less, 2, 1, Op.LESS),
    (AssertionTool.assert_less_equal, 2, 1, Op.LESS_EQUAL),
    (AssertionTool.assert_greater, 1, 2, Op.GREATER),
    (AssertionTool.assert_greater_equal, 1, 2, Op.GREATER_EQUAL),

    (AssertionTool.assert_is, 1, 2, Op.IS),
    (AssertionTool.assert_is_not, 1, 1, Op.IS_NOT),

    (AssertionTool.assert_in, 1, [2], Op.IN),
    (AssertionTool.assert_not_in, 1, [1], Op.NOT_IN),
])
def test_compare_fail_with_message(method, actual, expected, operator, *, assert_: AssertionTool):
    with given:
        message = "<message>"

    with when, raises(Exception) as exc:
        getattr(assert_, method.__name__)(actual, expected, message)

    with then:
        assert exc.type == AssertionError
        assert str(exc.value) == message

        assert assert_.get_left(exc.value) == actual
        assert assert_.get_right(exc.value) == expected
        assert assert_.get_operator(exc.value) == operator
        assert assert_.get_message(exc.value) == message
