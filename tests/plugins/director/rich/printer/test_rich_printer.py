from traceback import format_exception
from typing import Dict, Union
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from niltype import Nil
from rich.style import Style
from rich.traceback import Traceback

from vedro.core import ExcInfo, ScenarioStatus, StepStatus
from vedro.plugins.director.rich import RichPrinter

from ._utils import TestPretty, TestPrettyDiff, TestTraceback, console_, exc_info, printer

__all__ = ("printer", "exc_info", "console_")  # fixtures


def test_get_console(*, printer: RichPrinter, console_: Mock):
    with when:
        console = printer.console

    with then:
        assert console == console_


def test_print_header_default(*, printer: RichPrinter, console_: Mock):
    with when:
        printer.print_header()

    with then:
        assert console_.mock_calls == [call.out("Scenarios")]


def test_print_header(*, printer: RichPrinter, console_: Mock):
    with given:
        title = "<Title>"

    with when:
        printer.print_header(title)

    with then:
        assert console_.mock_calls == [call.out(title)]


def test_print_namespace(*, printer: RichPrinter, console_: Mock):
    with given:
        namespace = "register_user/by_email"

    with when:
        printer.print_namespace(namespace)

    with then:
        assert console_.mock_calls == [
            call.out("* register user / by email", style=Style(bold=True))
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (ScenarioStatus.PASSED, "✔", "green"),
    (ScenarioStatus.FAILED, "✗", "red"),
    (ScenarioStatus.SKIPPED, "○", "grey70"),
])
@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_scenario_subject(status: ScenarioStatus, symbol: str, color: str, prefix: str, *,
                                printer: RichPrinter, console_: Mock):
    with given:
        subject = "<subject>"

    with when:
        printer.print_scenario_subject(subject, status, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"{symbol} {subject}", style=Style(color=color)),
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (ScenarioStatus.PASSED, "+", "green"),
    (ScenarioStatus.FAILED, "x", "red"),
    (ScenarioStatus.SKIPPED, "o", "grey70"),
])
@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_scenario_subject_ascii_encoding(status: ScenarioStatus,
                                               symbol: str,
                                               color: str,
                                               prefix: str,
                                               *,
                                               printer: RichPrinter,
                                               console_: Mock):
    with given:
        console_.encoding = "ascii"
        subject = "<subject>"

    with when:
        printer.print_scenario_subject(subject, status, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"{symbol} {subject}", style=Style(color=color)),
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (ScenarioStatus.PASSED, "✔", "green"),
    (ScenarioStatus.FAILED, "✗", "red"),
    (ScenarioStatus.SKIPPED, "○", "grey70"),
])
@pytest.mark.parametrize(("elapsed", "elapsed_repr"), [
    (3.1, "3.10s"),
    (3.1415, "3.14s")
])
def test_print_scenario_subject_elapsed(status: ScenarioStatus, symbol: str, color: str,
                                        elapsed: Union[str, None], elapsed_repr: str, *,
                                        printer: RichPrinter, console_: Mock):
    with given:
        subject = "<subject>"

    with when:
        printer.print_scenario_subject(subject, status, elapsed=elapsed)

    with then:
        assert console_.mock_calls == [
            call.out("", end=""),
            call.out(f"{symbol} {subject}", style=Style(color=color), end=""),
            call.out(f" ({elapsed_repr})", style=Style(color="grey50")),
        ]


def test_print_scenario_subject_unknown_status(*, printer: RichPrinter, console_: Mock):
    with given:
        subject = "<subject>"

    with when:
        printer.print_scenario_subject(subject, ScenarioStatus.PENDING)

    with then:
        assert console_.mock_calls == []


@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_scenario_extra_details(prefix: str, *, printer: RichPrinter, console_: Mock):
    with given:
        extra_details = ["<extra-detail-1>", "<extra-detail-2>"]

    with when:
        printer.print_scenario_extra_details(extra_details, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"|> {extra_details[0]}", style=Style(color="grey50")),

            call.out(prefix, end=""),
            call.out(f"|> {extra_details[-1]}", style=Style(color="grey50"))
        ]


@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_step_extra_details(prefix: str, *, printer: RichPrinter, console_: Mock):
    with given:
        extra_details = ["<extra-detail-1>", "<extra-detail-2>"]

    with when:
        printer.print_step_extra_details(extra_details, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"|> {extra_details[0]}", style=Style(color="grey50")),

            call.out(prefix, end=""),
            call.out(f"|> {extra_details[-1]}", style=Style(color="grey50"))
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (StepStatus.PASSED, "✔", "green"),
    (StepStatus.FAILED, "✗", "red"),
])
@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_step_name(status: StepStatus, symbol: str, color: str, prefix: str, *,
                         printer: RichPrinter, console_: Mock):
    with given:
        name = "<step>"

    with when:
        printer.print_step_name(name, status, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"{symbol} {name}", style=Style(color=color)),
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (StepStatus.PASSED, "+", "green"),
    (StepStatus.FAILED, "x", "red"),
])
@pytest.mark.parametrize("prefix", ["", "---"])
def test_print_step_name_ascii_encoding(status: StepStatus, symbol: str, color: str, prefix: str,
                                        *, printer: RichPrinter, console_: Mock):
    with given:
        console_.encoding = "ascii"
        name = "<step>"

    with when:
        printer.print_step_name(name, status, prefix=prefix)

    with then:
        assert console_.mock_calls == [
            call.out(prefix, end=""),
            call.out(f"{symbol} {name}", style=Style(color=color)),
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (StepStatus.PASSED, "✔", "green"),
    (StepStatus.FAILED, "✗", "red"),
])
@pytest.mark.parametrize(("name", "expected_name"), [
    ("<step>", "<step>"),
    ("step_name", "step name"),
    ("step with spaces", "step with spaces"),
])
def test_step_name_format(status: StepStatus, symbol: str, color: str,
                          name: str, expected_name: str, *,
                          printer: RichPrinter, console_: Mock):
    with when:
        printer.print_step_name(name, status)

    with then:
        assert console_.mock_calls == [
            call.out("", end=""),
            call.out(f"{symbol} {expected_name}", style=Style(color=color)),
        ]


@pytest.mark.parametrize(("status", "symbol", "color"), [
    (StepStatus.PASSED, "✔", "green"),
    (StepStatus.FAILED, "✗", "red"),
])
@pytest.mark.parametrize(("elapsed", "elapsed_repr"), [
    (3.1, "3.10s"),
    (3.1415, "3.14s")
])
def test_print_step_name_elapsed(status: StepStatus, symbol: str, color: str,
                                 elapsed: Union[str, None], elapsed_repr: str, *,
                                 printer: RichPrinter, console_: Mock):
    with given:
        name = "<step>"

    with when:
        printer.print_step_name(name, status, elapsed=elapsed)

    with then:
        assert console_.mock_calls == [
            call.out("", end=""),
            call.out(f"{symbol} {name}", style=Style(color=color), end=""),
            call.out(f" ({elapsed_repr})", style=Style(color="grey50")),
        ]


def test_print_step_name_unknown_status(*, printer: RichPrinter, console_: Mock):
    with given:
        subject = "<subject>"

    with when:
        printer.print_step_name(subject, StepStatus.PENDING)

    with then:
        assert console_.mock_calls == []


def test_print_exception(*, printer: RichPrinter, exc_info: ExcInfo, console_: Mock):
    with given:
        formatted = format_exception(exc_info.type, exc_info.value, exc_info.traceback)

    with when:
        printer.print_exception(exc_info)

    with then:
        assert console_.mock_calls == [
            call.out("".join(formatted), style=Style(color="yellow")),
        ]


def test_print_pretty_exception(*, printer: RichPrinter, exc_info: ExcInfo, console_: Mock):
    with given:
        trace = Traceback.extract(exc_info.type, exc_info.value, exc_info.traceback)
        tb = TestTraceback(trace, max_frames=8, word_wrap=False, width=console_.size.width,
                           indent_guides=False)

    with when:
        printer.print_pretty_exception(exc_info)

    with then:
        assert console_.mock_calls == [
            call.print(tb),
            call.out(" "),
        ]


def test_print_pretty_exception_diff_left(*, printer: RichPrinter,
                                          exc_info: ExcInfo, console_: Mock):
    with given:
        left = Mock()
        setattr(exc_info.value, "__vedro_assert_left__", left)

        trace = Traceback.extract(exc_info.type, exc_info.value, exc_info.traceback)
        tb = TestTraceback(trace, max_frames=8, word_wrap=False, width=console_.size.width,
                           indent_guides=False)

        pretty = TestPrettyDiff(left, Nil, Nil,
                                max_context_lines=1,
                                max_nested_level=5,
                                max_container_length=10,
                                expand_containers=False)

    with when:
        printer.print_pretty_exception(exc_info)

    with then:
        assert console_.mock_calls == [
            call.print(tb),
            call.print(pretty, crop=True, soft_wrap=True),
            call.out(" "),
        ]


def test_print_pretty_exception_diff_left_full(*, printer: RichPrinter,
                                               exc_info: ExcInfo, console_: Mock):
    with given:
        left = Mock()
        setattr(exc_info.value, "__vedro_assert_left__", left)

        trace = Traceback.extract(exc_info.type, exc_info.value, exc_info.traceback)
        tb = TestTraceback(trace, max_frames=8, word_wrap=False, width=console_.size.width,
                           indent_guides=False)

        pretty = TestPrettyDiff(left, Nil, Nil)

    with when:
        printer.print_pretty_exception(exc_info, show_full_diff=True)

    with then:
        assert console_.mock_calls == [
            call.print(tb),
            call.print(pretty, crop=False, soft_wrap=False),
            call.out(" "),
        ]


def test_print_pretty_exception_diff_left_right(*, printer: RichPrinter,
                                                exc_info: ExcInfo, console_: Mock):
    with given:
        left, right, operator = Mock(), Mock(), "=="
        setattr(exc_info.value, "__vedro_assert_left__", left)
        setattr(exc_info.value, "__vedro_assert_right__", right)
        setattr(exc_info.value, "__vedro_assert_operator__", operator)

        trace = Traceback.extract(exc_info.type, exc_info.value, exc_info.traceback)
        tb = TestTraceback(trace, max_frames=8, word_wrap=False, width=console_.size.width,
                           indent_guides=False)

        pretty = TestPrettyDiff(left, right, operator,
                                max_context_lines=1,
                                max_nested_level=5,
                                max_container_length=10,
                                expand_containers=False)

    with when:
        printer.print_pretty_exception(exc_info)

    with then:
        assert console_.mock_calls == [
            call.print(tb),
            call.print(pretty, crop=True, soft_wrap=True),
            call.out(" "),
        ]


def test_print_pretty_exception_diff_left_right_full(*, printer: RichPrinter,
                                                     exc_info: ExcInfo, console_: Mock):
    with given:
        left, right, operator = Mock(), Mock(), "=="
        setattr(exc_info.value, "__vedro_assert_left__", left)
        setattr(exc_info.value, "__vedro_assert_right__", right)
        setattr(exc_info.value, "__vedro_assert_operator__", operator)

        trace = Traceback.extract(exc_info.type, exc_info.value, exc_info.traceback)
        tb = TestTraceback(trace, max_frames=8, word_wrap=False, width=console_.size.width,
                           indent_guides=False)

        pretty = TestPrettyDiff(left, right, operator)

    with when:
        printer.print_pretty_exception(exc_info, show_full_diff=True)

    with then:
        assert console_.mock_calls == [
            call.print(tb),
            call.print(pretty, crop=False, soft_wrap=False),
            call.out(" "),
        ]


def test_print_scope_header(*, printer: RichPrinter, console_: Mock):
    with given:
        title = "<header>"

    with when:
        printer.print_scope_header(title)

    with then:
        assert console_.mock_calls == [
            call.out(title, style=Style(color="blue", bold=True))
        ]


def test_print_scope_key(*, printer: RichPrinter, console_: Mock):
    with given:
        key = "<key>"

    with when:
        printer.print_scope_key(key)

    with then:
        assert console_.mock_calls == [
            call.out(f"{key}: ", end="", style=Style(color="blue"))
        ]


def test_print_scope_key_with_indent(*, printer: RichPrinter, console_: Mock):
    with given:
        key = "<key>"

    with when:
        printer.print_scope_key(key, indent=4)

    with then:
        assert console_.mock_calls == [
            call.out(f"    {key}: ", end="", style=Style(color="blue"))
        ]


def test_print_scope_key_with_line_break(*, printer: RichPrinter, console_: Mock):
    with given:
        key = "<key>"

    with when:
        printer.print_scope_key(key, line_break=True)

    with then:
        assert console_.mock_calls == [
            call.out(f"{key}: ", end="\n", style=Style(color="blue"))
        ]


def test_print_scope_val(*, printer: RichPrinter, console_: Mock):
    with given:
        val = "x" * console_.size.width * 2

    with when:
        printer.print_scope_val(val)

    with then:
        assert console_.mock_calls == [
            call.print(TestPretty(val)),
        ]


def test_print_scope_val_concrete_width(*, printer: RichPrinter, console_: Mock):
    with given:
        scope_width = 20
        val = "x" * scope_width * 2

    with when:
        printer.print_scope_val(val, scope_width=scope_width)

    with then:
        assert console_.mock_calls == [
            call.print(TestPretty(val, overflow="ellipsis", no_wrap=True), width=scope_width),
        ]


def test_print_empty_scope(*, printer: RichPrinter, console_: Mock):
    with given:
        scope = {}

    with when:
        printer.print_scope(scope)

    with then:
        assert console_.mock_calls == [
            call.out("Scope", style=Style(color="blue", bold=True)),
            call.out(" "),
        ]


def test_print_scope(*, printer: RichPrinter, console_: Mock):
    with given:
        scope = {
            "id": 1,
            "name": "Bob"
        }

    with when:
        printer.print_scope(scope)

    with then:
        assert console_.mock_calls == [
            call.out("Scope", style=Style(color="blue", bold=True)),

            call.out(" id: ", end="", style=Style(color="blue")),
            call.print(TestPretty(1)),

            call.out(" name: ", end="", style=Style(color="blue")),
            call.print(TestPretty("Bob")),

            call.out(" "),
        ]


def test_print_scope_with_width(*, printer: RichPrinter, console_: Mock):
    with given:
        scope = {
            "id": 1,
            "name": "Bob"
        }
        width = 80

    with when:
        printer.print_scope(scope, scope_width=width)

    with then:
        assert console_.mock_calls == [
            call.out("Scope", style=Style(color="blue", bold=True)),

            call.out(" id: ", end="", style=Style(color="blue")),
            call.print(TestPretty(1, overflow="ellipsis", no_wrap=True), width=width),

            call.out(" name: ", end="", style=Style(color="blue")),
            call.print(TestPretty("Bob", overflow="ellipsis", no_wrap=True), width=width),

            call.out(" "),
        ]


def test_pretty_value_print(*, printer: RichPrinter, console_: Mock):
    with given:
        val = "<value>"

    with when:
        printer.pretty_print(val)

    with then:
        assert console_.mock_calls == [
            call.print(TestPretty(val)),
        ]


def test_pretty_print_value_with_concrete_width(*, printer: RichPrinter, console_: Mock):
    with given:
        width = 20
        val = "<value>"

    with when:
        printer.pretty_print(val, width=width)

    with then:
        assert console_.mock_calls == [
            call.print(TestPretty(val, overflow="ellipsis", no_wrap=True), width=width),
        ]


def test_pretty_print_renderable(*, printer: RichPrinter, console_: Mock):
    with given:
        renderable = Mock(__rich__=lambda _: "Renderable()")

    with when:
        printer.pretty_print(renderable)

    with then:
        assert console_.mock_calls == [
            call.print(renderable, soft_wrap=False),
        ]


def test_pretty_print_renderable_with_concrete_width(*, printer: RichPrinter, console_: Mock):
    with given:
        width = 20
        renderable = Mock(__rich__=lambda _: "Renderable()")

    with when:
        printer.pretty_print(renderable, width=width)

    with then:
        assert console_.mock_calls == [
            call.print(renderable, overflow="ellipsis", no_wrap=True, width=width),
        ]


def test_print_report_preamble(*, printer: RichPrinter, console_: Mock):
    with given:
        summary = ["line1", "line2"]

    with when:
        printer.print_report_preamble(summary)

    with then:
        assert console_.mock_calls == [
            call.out(": line1\n: line2", style=Style(color="grey70"))
        ]


def test_print_report_preamble_empty(*, printer: RichPrinter, console_: Mock):
    with given:
        summary = []

    with when:
        printer.print_report_preamble(summary)

    with then:
        assert console_.mock_calls == []


def test_print_report_summary(*, printer: RichPrinter, console_: Mock):
    with given:
        summary = ["line1", "line2"]

    with when:
        printer.print_report_summary(summary)

    with then:
        assert console_.mock_calls == [
            call.out("# line1\n# line2", style=Style(color="grey70"))
        ]


def test_print_report_summary_empty(*, printer: RichPrinter, console_: Mock):
    with given:
        summary = []

    with when:
        printer.print_report_summary(summary)

    with then:
        assert console_.mock_calls == []


@pytest.mark.parametrize(("elapsed", "formatted"), [
    # hours
    (25 * 3600 + 0 * 60 + 5.0, "25h 0m 5s"),
    (3 * 3600 + 15 * 60 + 0.0, "3h 15m 0s"),
    # minutes
    (9 * 60 + 30.0, "9m 30s"),
    (1 * 60 + 0.0, "1m 0s"),
    # seconds
    (59.99, "59.99s"),
    (0.1, "0.10s"),
    (0.01, "0.01s"),
    (0.001, "0.00s"),
    (0.0001, "0.00s"),
])
def test_elapsed_formatter(elapsed: float, formatted: str, *, printer: RichPrinter):
    with when:
        result = printer.format_elapsed(elapsed)

    with then:
        assert result == formatted


@pytest.mark.parametrize(("stats", "color"), [
    ({"total": 4, "passed": 3, "failed": 0, "skipped": 1}, "green"),
    ({"total": 5, "passed": 3, "failed": 1, "skipped": 1}, "red"),
    ({"total": 0, "passed": 0, "failed": 0, "skipped": 0}, "red"),
])
def test_print_report_stats(stats: Dict[str, int], color: str, *,
                            printer: RichPrinter, console_: Mock):
    with given:
        message = ("# {total} scenarios, {passed} passed,"
                   " {failed} failed, {skipped} skipped").format(**stats)

    with when:
        printer.print_report_stats(**stats, elapsed=0.0)

    with then:
        assert console_.mock_calls == [
            call.out(message, style=Style(color=color, bold=True), end=""),
            call.out(" (0.00s)", style=Style(color="blue")),
        ]


def test_print_report_stats_interrupted(printer: RichPrinter, console_: Mock):
    with given:
        stats = {
            "total": 0,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
        }
        message = ("# {total} scenarios, {passed} passed,"
                   " {failed} failed, {skipped} skipped").format(**stats)

    with when:
        printer.print_report_stats(**stats, is_interrupted=True, elapsed=0.0)

    with then:
        assert console_.mock_calls == [
            call.out(message, style=Style(color="red", bold=True), end=""),
            call.out(" (0.00s)", style=Style(color="blue")),
        ]


def test_print_interrupted(printer: RichPrinter, console_: Mock):
    with given:
        exc_info = ExcInfo(KeyboardInterrupt, KeyboardInterrupt("msg"), None)
        message = "\n".join([
            "!!!                                           !!!",
            "!!! Interrupted by “KeyboardInterrupt('msg')“ !!!",
            "!!!                                           !!!",
        ])

    with when:
        printer.print_interrupted(exc_info)

    with then:
        assert console_.mock_calls == [
            call.out(message, style=Style(color="yellow")),
        ]


def test_print_interrupted_with_traceback(printer: RichPrinter, exc_info: ExcInfo, console_: Mock):
    with given:
        message = "\n".join([
            "!!!                             !!!",
            "!!! Interrupted by “KeyError()“ !!!",
            "!!!                             !!!",
        ])
        formatted = format_exception(exc_info.type, exc_info.value, exc_info.traceback)

    with when:
        printer.print_interrupted(exc_info, show_traceback=True)

    with then:
        assert console_.mock_calls == [
            call.out(message, style=Style(color="yellow")),
            call.out("".join(formatted), style=Style(color="yellow")),
        ]


def test_print_empty_line(*, printer: RichPrinter, console_: Mock):
    with when:
        printer.print_empty_line()

    with then:
        assert console_.mock_calls == [call.out(" ")]


def test_print(*, printer: RichPrinter, console_: Mock):
    with given:
        value = "<smth>"

    with when:
        printer.print(value)

    with then:
        assert console_.mock_calls == [call.out(value, end="\n")]


def test_print_end(*, printer: RichPrinter, console_: Mock):
    with given:
        value = "<smth>"
        end = ""

    with when:
        printer.print(value, end="")

    with then:
        assert console_.mock_calls == [call.out(value, end=end)]


def test_pretty_format(*, printer: RichPrinter):
    with given:
        value = [
            {
                "id": 1,
                "name": "Bob",
                "balance": 3.14,
                "is_deleted": False,
                "email": None,
            }
        ]

    with when:
        res = printer.pretty_format(value)

    with then:
        assert res == "\n".join([
            '[',
            '    {',
            '        "id": 1,',
            '        "name": "Bob",',
            '        "balance": 3.14,',
            '        "is_deleted": false,',
            '        "email": null',
            '    }',
            ']'
        ])


def test_pretty_format_unknown_type(*, printer: RichPrinter):
    with given:
        class User:
            pass
        user = User()

    with when:
        res = printer.pretty_format(user)

    with then:
        assert isinstance(res, str)
        assert res == repr(user)


def test_pretty_format_unknown_type_with_repr(*, printer: RichPrinter):
    with given:
        class User:
            def __repr__(self):
                return "<User>"

        user = User()

    with when:
        res = printer.pretty_format(user)

    with then:
        assert isinstance(res, str)
        assert res == "<User>"


def test_pretty_format_unknown_type_with_rich(*, printer: RichPrinter):
    with given:
        class User:
            def __rich__(self):
                pass

        user = User()

    with when:
        res = printer.pretty_format(user)

    with then:
        assert isinstance(res, User)
        assert res == user


def test_pretty_format_unknown_type_with_rich_console(*, printer: RichPrinter):
    with given:
        class User:
            def __rich_console__(self, console, options):
                pass

        user = User()

    with when:
        res = printer.pretty_format(user)

    with then:
        assert isinstance(res, User)
        assert res == user


def test_show_spinner(*, printer: RichPrinter, console_: Mock):
    with given:
        status = "..."
        spinner_ = Mock()
        console_.status = Mock(return_value=spinner_)

    with when:
        printer.show_spinner(status)

    with then:
        assert console_.mock_calls == [call.status(status)]
        assert spinner_.mock_calls == [call.start()]


def test_show_shown_spinner(*, printer: RichPrinter, console_: Mock):
    with given:
        status = "..."
        spinner_ = Mock()
        console_.status = Mock(return_value=spinner_)

        printer.show_spinner(status)
        console_.reset_mock()

    with when:
        printer.show_spinner(status)

    with then:
        assert console_.mock_calls == [call.status(status)]
        assert spinner_.mock_calls == [call.stop(), call.start()]


def test_hide_spinner(*, printer: RichPrinter, console_: Mock):
    with given:
        spinner_ = Mock()
        console_.status = Mock(return_value=spinner_)

    with when:
        printer.hide_spinner()

    with then:
        assert console_.mock_calls == []
        assert spinner_.mock_calls == []


def test_hide_shown_spinner(*, printer: RichPrinter, console_: Mock):
    with given:
        status = "..."
        spinner_ = Mock()
        console_.status = Mock(return_value=spinner_)

        printer.show_spinner(status)
        console_.reset_mock()

    with when:
        printer.hide_spinner()

    with then:
        assert console_.mock_calls == []
        assert spinner_.mock_calls == [call.stop()]
