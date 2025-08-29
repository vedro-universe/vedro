from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as ScenarioScheduler
from vedro.core import Report
from vedro.events import (
    CleanupEvent,
    ScenarioReportedEvent,
    ScenarioRunEvent,
    ScenarioSkippedEvent,
    StartupEvent,
)
from vedro.plugins.director import (
    DirectorInitEvent,
    DirectorPlugin,
    RichReporter,
    RichReporterPlugin,
)

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_exc_info,
    make_scenario_result,
    make_vscenario,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


async def test_subscribe(*, dispatcher: Dispatcher):
    with given:
        director_ = Mock(DirectorPlugin)

        reporter = RichReporterPlugin(RichReporter)
        reporter.subscribe(dispatcher)

    with when:
        await dispatcher.fire(DirectorInitEvent(director_))

    with then:
        assert director_.mock_calls == [
            call.register("rich", reporter)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scheduler = ScenarioScheduler([])
        event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_report_preamble(["running: 0 of 0 scenarios"]),
            call.print_header(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup_with_preamble(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario = make_vscenario()
        scheduler = ScenarioScheduler([scenario])

        report = Report()
        report.add_preamble("<preamble>")

        event = StartupEvent(scheduler, report=report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_report_preamble([
                "<preamble>",
                "running: 1 of 1 scenarios"
            ]),
            call.print_header(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup_with_preamble_skipped(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        pending_scenario = make_vscenario()
        skipped_scenario = make_vscenario()

        scheduler = ScenarioScheduler([pending_scenario, skipped_scenario])
        skipped_scenario.skip()

        report = Report()
        report.add_preamble("<preamble>")

        event = StartupEvent(scheduler, report=report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_report_preamble([
                "<preamble>",
                "running: 1 of 2 scenarios (1 skipped)"
            ]),
            call.print_header(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup_with_preamble_ignored(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        pending_scenario = make_vscenario()
        ignored_scenario = make_vscenario()

        scheduler = ScenarioScheduler([pending_scenario, ignored_scenario])
        scheduler.ignore(ignored_scenario)

        report = Report()
        report.add_preamble("<preamble>")

        event = StartupEvent(scheduler, report=report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_report_preamble([
                "<preamble>",
                "running: 1 of 2 scenarios (1 ignored)"
            ]),
            call.print_header(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_startup_with_preamble_skipped_and_ignored(*, dispatcher: Dispatcher,
                                                         printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        pending_scenario = make_vscenario()
        skipped_scenario = make_vscenario()
        ignored_scenario = make_vscenario()

        scheduler = ScenarioScheduler([pending_scenario, skipped_scenario, ignored_scenario])
        skipped_scenario.skip()
        scheduler.ignore(ignored_scenario)

        report = Report()
        report.add_preamble("<preamble>")

        event = StartupEvent(scheduler, report=report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_report_preamble([
                "<preamble>",
                "running: 1 of 3 scenarios (1 skipped, 1 ignored)"
            ]),
            call.print_header(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_run(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_called() is None
        assert len(printer_.mock_calls) == 1


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_run_same_namespace(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result1 = make_scenario_result()
        await dispatcher.fire(ScenarioRunEvent(scenario_result1))
        printer_.reset_mock()

        scenario_result2 = make_scenario_result()
        event = ScenarioRunEvent(scenario_result2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_not_called() is None
        assert len(printer_.mock_calls) == 0


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_run_show_spinner(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_scenario_spinner=True)

        scenario_result = make_scenario_result()
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        status = f" {scenario_result.scenario.subject}"
        assert printer_.print_namespace.assert_called() is None
        assert printer_.show_spinner.assert_called_with(status) is None
        assert len(printer_.mock_calls) == 2


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_unknown_status(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == []


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_called() is None
        assert len(printer_.mock_calls) == 1


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_same_namespace(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result1 = make_scenario_result()
        await dispatcher.fire(ScenarioSkippedEvent(scenario_result1))
        printer_.reset_mock()

        scenario_result2 = make_scenario_result()
        event = ScenarioSkippedEvent(scenario_result2)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.print_namespace.assert_not_called() is None
        assert len(printer_.mock_calls) == 0


async def test_scenario_skipped_disabled(*, dispatcher: Dispatcher,
                                         rich_reporter: RichReporterPlugin, printer_: Mock):
    with given:
        rich_reporter._show_skipped = False  # move to config
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(printer_.mock_calls) == 0


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_show_paths(*, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True)

        scenario_result = make_scenario_result().mark_skipped()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        rel_path = scenario_result.scenario.rel_path
        lineno = scenario_result.scenario.lineno
        assert scenario_result.extra_details == [f"{rel_path}:{lineno}"]


async def test_scenario_skipped_show_reason(*, dispatcher: Dispatcher,
                                            rich_reporter: RichReporterPlugin):
    with given:
        rich_reporter._show_skip_reason = True
        await fire_arg_parsed_event(dispatcher)

        reason = "<reason>"
        vscenario = make_vscenario()
        vscenario.skip(reason)

        scenario_result = make_scenario_result(vscenario).mark_skipped()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert scenario_result.extra_details == [reason]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_cleanup(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        report = Report()
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_empty_line(),
            call.print_report_summary(report.summary),
            call.print_report_stats(total=report.total,
                                    passed=report.passed,
                                    failed=report.failed,
                                    skipped=report.skipped,
                                    elapsed=report.elapsed,
                                    is_interrupted=False)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_cleanup_interrupted(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        report = Report()
        exc_info = make_exc_info(KeyboardInterrupt())
        report.set_interrupted(exc_info)

        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_empty_line(),
            call.print_interrupted(exc_info, show_traceback=False),
            call.print_report_summary(report.summary),
            call.print_report_stats(total=report.total,
                                    passed=report.passed,
                                    failed=report.failed,
                                    skipped=report.skipped,
                                    elapsed=report.elapsed,
                                    is_interrupted=True)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_cleanup_ring_bell(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, ring_bell=True)

        report = Report()
        event = CleanupEvent(report)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.console.mock_calls == [call.bell()]
