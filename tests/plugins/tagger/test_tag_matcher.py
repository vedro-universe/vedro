from baby_steps import then, when
from pytest import raises

from vedro.plugins.tagger import TagMatcher


def test_tag_matcher():
    with when, raises(BaseException) as exc:
        TagMatcher("expr")

    with then:
        assert exc.type is TypeError
