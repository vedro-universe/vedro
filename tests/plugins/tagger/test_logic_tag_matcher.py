import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.tagger.logic_tag_matcher import LogicTagMatcher


def test_match():
    with given:
        matcher = LogicTagMatcher("P0")

    with when:
        res = matcher.match({"P0"})

    with then:
        assert res is True


def test_not_match():
    with given:
        matcher = LogicTagMatcher("P0")

    with when:
        res = matcher.match({"API"})

    with then:
        assert res is False


def test_invalid_expr():
    with when, raises(ValueError) as exc:
        LogicTagMatcher("P0 and")

    with then:
        assert exc.type is ValueError


@pytest.mark.parametrize("expr", [
    "1TAG",
    "-TAG",
    "and",
    "or",
    "not",
])
def test_invalid_tag(expr: str):
    with when, raises(ValueError) as exc:
        LogicTagMatcher(expr)

    with then:
        assert exc.type is ValueError
