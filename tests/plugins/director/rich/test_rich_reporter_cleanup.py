from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Style

from vedro._core import Dispatcher, Report
from vedro.events import CleanupEvent
from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import (
    console_,
    dispatcher,
    make_report,
    make_scenario_result,
    reporter,
)

__all__ = ("dispatcher", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_cleanup_event(*, dispatcher: Dispatcher,
                                           reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        report = Report()
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(" "),
            call.out("# 0 scenarios, 0 passed, 0 failed, 0 skipped",
                     style=Style.parse("bold red"),
                     end=""),
            call.out(f" ({report.elapsed:.2f}s)", style=Style.parse("blue"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_cleanup_event_with_summary(*, dispatcher: Dispatcher,
                                                        reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        summaries = ["<summary1>", "<summary2>"]
        report = make_report(summaries=summaries)
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(" "),
            call.out("# " + "\n# ".join(summaries), style=Style.parse("grey70")),
            call.out("# 0 scenarios, 0 passed, 0 failed, 0 skipped",
                     style=Style.parse("bold red"),
                     end=""),
            call.out(f" ({report.elapsed:.2f}s)", style=Style.parse("blue"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_success_cleanup_event(*, dispatcher: Dispatcher,
                                                   reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        scenario_result1 = make_scenario_result().mark_passed() \
                                                 .set_started_at(1.0) \
                                                 .set_ended_at(2.0)
        scenario_result2 = make_scenario_result().mark_passed() \
                                                 .set_started_at(2.0) \
                                                 .set_ended_at(3.0)
        scenario_result3 = make_scenario_result().mark_skipped()
        report = make_report([
            scenario_result1,
            scenario_result2,
            scenario_result3,
        ])
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(" "),
            call.out("# 3 scenarios, 2 passed, 0 failed, 1 skipped",
                     style=Style.parse("bold green"),
                     end=""),
            call.out(f" ({report.elapsed:.2f}s)", style=Style.parse("blue"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_failed_cleanup_event(*, dispatcher: Dispatcher,
                                                  reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        scenario_result = make_scenario_result().mark_failed() \
                                                .set_started_at(3.145) \
                                                .set_ended_at(6.285)
        report = make_report([scenario_result])
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(" "),
            call.out("# 1 scenarios, 0 passed, 1 failed, 0 skipped",
                     style=Style.parse("bold red"),
                     end=""),
            call.out(" (3.14s)", style=Style.parse("blue"))
        ]
