import sys
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import AggregatedResult, Dispatcher, ScenarioStatus, StepStatus
from vedro.core.output_capturer import CapturedOutput
from vedro.events import ScenarioPassedEvent, ScenarioReportedEvent, ScenarioRunEvent
from vedro.plugins.director import RichReporterPlugin

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_scenario_result,
    make_step_result,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_passed()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=None, prefix=" ")
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_show_timings(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_timings=True)

        scenario_result = make_scenario_result().mark_passed() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=2.0, prefix=" ")
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_show_paths(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True)

        scenario_result = make_scenario_result().mark_passed()
        await dispatcher.fire(ScenarioPassedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        rel_path = scenario_result.scenario.rel_path
        lineno = scenario_result.scenario.lineno
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details([f"{rel_path}:{lineno}"], prefix=" " * 3)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_show_steps(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_steps=True)

        scenario_result = make_scenario_result().mark_passed()

        step1_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step1_result_passed)

        step2_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step2_result_passed)

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=None, prefix=" "),
            call.print_step_name(step1_result_passed.step_name, StepStatus.PASSED,
                                 elapsed=None, prefix=" " * 3),
            call.print_step_name(step2_result_passed.step_name, StepStatus.PASSED,
                                 elapsed=None, prefix=" " * 3),
        ]


async def test_scenario_passed_show_spinner(*, dispatcher: Dispatcher,
                                            rich_reporter: RichReporterPlugin, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_scenario_spinner=True)

        scenario_result = make_scenario_result()
        await dispatcher.fire(ScenarioRunEvent(scenario_result))
        printer_.reset_mock()

        aggregated_result = make_aggregated_result(scenario_result.mark_passed())
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.hide_spinner(),
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=None, prefix=" ")
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_aggregated_result(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_results = [
            make_scenario_result().mark_passed(),
            make_scenario_result().mark_failed(),
        ]

        aggregated_result = AggregatedResult.from_existing(scenario_results[0], scenario_results)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.PASSED, elapsed=None, prefix=" "),

            call.print_scenario_subject(aggregated_result.scenario_results[0].scenario.subject,
                                        ScenarioStatus.PASSED,
                                        elapsed=None,
                                        prefix=" │\n ├─[1/2] "),
            call.print_scenario_subject(aggregated_result.scenario_results[1].scenario.subject,
                                        ScenarioStatus.FAILED,
                                        elapsed=None,
                                        prefix=" │\n ├─[2/2] "),

            call.print_empty_line(),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_with_captured_output(*, dispatcher: Dispatcher,
                                                    rich_reporter: RichReporterPlugin,
                                                    printer_: Mock):
    with given:
        rich_reporter._show_captured_output = True
        rich_reporter._show_captured_output_limit = 10
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_passed()

        with CapturedOutput() as captured_output:
            print("Test output from scenario")
            print("Error output from scenario", file=sys.stderr)
        scenario_result.set_captured_output(captured_output)

        await dispatcher.fire(ScenarioPassedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.PASSED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details(
                [
                    "stdout: Test outpu...[15 CHARS TRUNCATED]",
                    "stderr: Error outp...[16 CHARS TRUNCATED]"
                ],
                prefix=" " * 3
            )
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_with_captured_output_and_steps(*, dispatcher: Dispatcher,
                                                              rich_reporter: RichReporterPlugin,
                                                              printer_: Mock):
    with given:
        rich_reporter._show_captured_output = True
        rich_reporter._show_captured_output_limit = 15
        await fire_arg_parsed_event(dispatcher, show_steps=True)

        scenario_result = make_scenario_result().mark_passed()

        step_result = make_step_result().mark_passed()
        with CapturedOutput() as step_captured:
            print("Step execution output")
            print("Step warning", file=sys.stderr)
        step_result.set_captured_output(step_captured)
        scenario_result.add_step_result(step_result)

        await dispatcher.fire(ScenarioPassedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.PASSED, elapsed=None, prefix=" "),
            call.print_step_name(step_result.step_name, StepStatus.PASSED,
                                 elapsed=None, prefix=" " * 3),
            call.print_step_extra_details(
                [
                    "stdout: Step execution ...[6 CHARS TRUNCATED]",
                    "stderr: Step warning"
                ],
                prefix=" " * 3
            ),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_with_captured_output_disabled(*, dispatcher: Dispatcher,
                                                             rich_reporter: RichReporterPlugin,
                                                             printer_: Mock):
    with given:
        # rich_reporter._show_captured_output = False
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_passed()

        with CapturedOutput() as captured_output:
            print("Test output from scenario")
            print("Error output from scenario", file=sys.stderr)
        scenario_result.set_captured_output(captured_output)

        await dispatcher.fire(ScenarioPassedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.PASSED, elapsed=None, prefix=" "),
        ]
