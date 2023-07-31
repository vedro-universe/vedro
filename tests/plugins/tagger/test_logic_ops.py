from typing import Set

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.tagger.logic_tag_matcher._logic_ops import And, Expr, Not, Operand, Operator, Or


def test_tag_expr():
    with when, raises(BaseException) as exc:
        Expr()

    with then:
        assert exc.type is TypeError


def test_tag_operator():
    with when, raises(BaseException) as exc:
        Operator()

    with then:
        assert exc.type is TypeError


def test_tag_operand():
    with when:
        operand = Operand("API")

    with then:
        assert isinstance(operand, Expr)
        assert repr(operand) == "Tag(API)"


@pytest.mark.parametrize(("tags", "result"), [
    ({"API"}, True),
    ({"P0"}, False),
])
def test_tag_operand_expr(tags: Set[str], result: bool):
    with given:
        operand = Operand("API")

    with when:
        res = operand(tags)

    with then:
        assert res is result


def test_not_operator():
    with given:
        operand = Operand("API")

    with when:
        operator = Not(operand)

    with then:
        assert isinstance(operator, Expr)
        assert repr(operator) == "Not(Tag(API))"


@pytest.mark.parametrize(("tags", "result"), [
    ({"API"}, False),
    ({"P0"}, True),
])
def test_not_operator_expr(tags: Set[str], result: bool):
    with given:
        operand = Operand("API")
        operator = Not(operand)

    with when:
        res = operator(tags)

    with then:
        assert res is result


def test_and_operator():
    with given:
        left_operand = Operand("API")
        right_operand = Operand("P0")

    with when:
        operator = And(left_operand, right_operand)

    with then:
        assert isinstance(operator, Expr)
        assert repr(operator) == "And(Tag(API), Tag(P0))"


@pytest.mark.parametrize(("tags", "result"), [
    ({"API", "P0"}, True),
    ({"P0"}, False),
    ({"API"}, False),
    ({"CLI"}, False),
])
def test_and_operator_expr(tags: Set[str], result: bool):
    with given:
        left_operand = Operand("API")
        right_operand = Operand("P0")
        operator = And(left_operand, right_operand)

    with when:
        res = operator(tags)

    with then:
        assert res is result


def test_or_operator():
    with given:
        left_operand = Operand("API")
        right_operand = Operand("P0")

    with when:
        operator = Or(left_operand, right_operand)

    with then:
        assert isinstance(operator, Expr)
        assert repr(operator) == "Or(Tag(API), Tag(P0))"


@pytest.mark.parametrize(("tags", "result"), [
    ({"API", "P0"}, True),
    ({"P0"}, True),
    ({"API"}, True),
    ({"CLI"}, False),
])
def test_or_operator_expr(tags: Set[str], result: bool):
    with given:
        left_operand = Operand("API")
        right_operand = Operand("P0")
        operator = Or(left_operand, right_operand)

    with when:
        res = operator(tags)

    with then:
        assert res is result
