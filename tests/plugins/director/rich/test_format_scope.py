from unittest.mock import sentinel

from baby_steps import given, then, when

from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import console_, dispatcher, reporter

__all__ = ("dispatcher", "reporter", "console_",)


def test_rich_reporter_format_scope_without_values(*, reporter: RichReporter):
    with given:
        scope = {}

    with when:
        res = list(reporter._format_scope(scope))

    with then:
        assert res == []


def test_rich_reporter_format_scope_with_values(*, reporter: RichReporter):
    with given:
        scope = {"key_int": 1, "key_str": "val"}

    with when:
        res = list(reporter._format_scope(scope))

    with then:
        assert res == [
            ("key_int", "1"),
            ("key_str", '"val"'),
        ]


def test_rich_reporter_format_scope_with_unserializable_value(*, reporter: RichReporter):
    with given:
        unserializable = sentinel
        scope = {"key_int": 1, "key_unserializable": unserializable}

    with when:
        res = list(reporter._format_scope(scope))

    with then:
        assert res == [
            ("key_int", "1"),
            ("key_unserializable", repr(unserializable)),
        ]
