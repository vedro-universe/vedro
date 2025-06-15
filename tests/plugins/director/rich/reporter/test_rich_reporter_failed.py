from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioStatus, StepStatus
from vedro.events import ScenarioFailedEvent, ScenarioReportedEvent
from vedro.plugins.director import RichReporterPlugin

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_exc_info,
    make_scenario_result,
    make_step_result,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


@pytest.mark.usefixtures(rich_reporter.__name__)
@pytest.mark.parametrize("show_locals", [False, True])
@pytest.mark.parametrize("show_full_diff", [False, True])
async def test_scenario_failed(show_locals: bool, show_full_diff: bool, *,
                               dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher,
                                    tb_show_locals=show_locals,
                                    tb_show_internal_calls=True,
                                    show_full_diff=show_full_diff)

        scenario_result = make_scenario_result().mark_failed()

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        scope = {"key": "val"}
        scenario_result.set_scope(scope)

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.FAILED, elapsed=None, prefix=" "),

            call.print_step_name(step_result_passed.step_name,
                                 StepStatus.PASSED, elapsed=None, prefix=" " * 3),
            call.print_step_name(step_result_failed.step_name,
                                 StepStatus.FAILED, elapsed=None, prefix=" " * 3),

            call.print_pretty_exception(exc_info,
                                        width=100,
                                        max_frames=8,
                                        show_locals=show_locals,
                                        show_internal_calls=True,
                                        show_full_diff=show_full_diff)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_show_paths(dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True)

        scenario_result = make_scenario_result().mark_failed()

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        await dispatcher.fire(ScenarioFailedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.FAILED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details(
                [f"{scenario_result.scenario.path.name}"],
                prefix=" " * 3
            ),

            call.print_step_name(step_result_passed.step_name,
                                 StepStatus.PASSED, elapsed=None, prefix=" " * 3),
            call.print_step_name(step_result_failed.step_name,
                                 StepStatus.FAILED, elapsed=None, prefix=" " * 3),

            call.print_pretty_exception(exc_info,
                                        width=100,
                                        max_frames=8,
                                        show_locals=False,
                                        show_internal_calls=True,
                                        show_full_diff=False)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, verbose=1)

        scenario_result = make_scenario_result().mark_failed()

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        scope = {"key": "val"}
        scenario_result.set_scope(scope)

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.FAILED, elapsed=None, prefix=" "),

            call.print_step_name(step_result_passed.step_name,
                                 StepStatus.PASSED, elapsed=None, prefix=" " * 3),
            call.print_step_name(step_result_failed.step_name,
                                 StepStatus.FAILED, elapsed=None, prefix=" " * 3),

            call.print_pretty_exception(exc_info,
                                        width=100,
                                        max_frames=8,
                                        show_locals=False,
                                        show_internal_calls=True,
                                        show_full_diff=False),

            call.print_scope(scope, scope_width=-1),
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose_show_timings(dispatcher: Dispatcher,
                                                    rich_reporter: RichReporterPlugin,
                                                    printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, verbose=1, show_timings=True)

        scenario_result = make_scenario_result().set_started_at(1.0).set_ended_at(7.0)

        step_result_passed = (make_step_result().mark_passed()
                                                .set_started_at(1.0).set_ended_at(3.0))
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = (make_step_result().mark_failed()
                                                .set_exc_info(exc_info)
                                                .set_started_at(3.0).set_ended_at(6.0))
        scenario_result.add_step_result(step_result_failed)

        aggregated_result = make_aggregated_result(scenario_result.mark_failed())
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.FAILED, elapsed=6.0, prefix=" "),

            call.print_step_name(step_result_passed.step_name,
                                 StepStatus.PASSED, elapsed=2.0, prefix=" " * 3),
            call.print_step_name(step_result_failed.step_name,
                                 StepStatus.FAILED, elapsed=3.0, prefix=" " * 3),

            call.print_pretty_exception(exc_info,
                                        width=100,
                                        max_frames=8,
                                        show_locals=False,
                                        show_internal_calls=True,
                                        show_full_diff=False),
        ]
