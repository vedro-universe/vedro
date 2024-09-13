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
    with given:
        matcher = LogicTagMatcher("P0 and")

    with when, raises(ValueError) as exc:
        matcher.match(set())

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == ("Invalid tag expr 'P0 and'. "
                                  "Error: Expected end of text, found 'and'  "
                                  "(at char 3), (line:1, col:4)")


@pytest.mark.parametrize("expr", [
    "1TAG",
    "-TAG",
    "and",
    "or",
    "not",
    "AND",
    "OR",
    "NOT",
])
def test_invalid_tag(expr: str):
    with given:
        matcher = LogicTagMatcher(expr)

    with when, raises(ValueError) as exc:
        matcher.match(set())

    with then:
        assert exc.type is ValueError
        assert str(exc.value).startswith(f"Invalid tag expr {expr!r}. Error: ")
