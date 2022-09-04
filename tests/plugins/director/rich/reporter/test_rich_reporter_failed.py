from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioStatus, StepStatus
from vedro.events import ScenarioReportedEvent
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


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
@pytest.mark.parametrize("show_paths", [False, True])
async def test_scenario_failed_verbose0(show_paths: bool, *,
                                        dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=show_paths)

        scenario_result = make_scenario_result().mark_failed()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.FAILED, elapsed=None, prefix=" ")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose0_show_timings(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_timings=True)

        scenario_result = make_scenario_result().mark_failed() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.FAILED, elapsed=2.0, prefix=" ")
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
@pytest.mark.parametrize("show_locals", [False, True])
@pytest.mark.parametrize("show_internal_calls", [False, True])
async def test_scenario_failed_verbose2(show_locals: bool, show_internal_calls: bool, *,
                                        dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, verbose=2,
                                    tb_show_locals=show_locals,
                                    tb_show_internal_calls=show_internal_calls)

        scenario_result = make_scenario_result()

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        aggregated_result = make_aggregated_result(scenario_result.mark_failed())
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
                                        max_frames=8,
                                        show_locals=show_locals,
                                        show_internal_calls=show_internal_calls)
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose2_show_timings(dispatcher: Dispatcher,
                                                     rich_reporter: RichReporterPlugin,
                                                     printer_: Mock):
    with given:
        rich_reporter._tb_pretty = False
        await fire_arg_parsed_event(dispatcher, verbose=2, show_timings=True)

        scenario_result = make_scenario_result().set_started_at(1.0).set_ended_at(7.0)

        step_result_passed = make_step_result().mark_passed() \
                                               .set_started_at(1.0).set_ended_at(3.0)
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed() \
                                               .set_exc_info(exc_info) \
                                               .set_started_at(3.0).set_ended_at(6.0)
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

            call.print_exception(exc_info, max_frames=8, show_internal_calls=False)
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose3_without_scope(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, verbose=3)

        scenario_result = make_scenario_result()
        scenario_result.set_scope({})

        aggregated_result = make_aggregated_result(scenario_result.mark_failed())
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == [
            call.print_scenario_subject(aggregated_result.scenario.subject,
                                        ScenarioStatus.FAILED, elapsed=None, prefix=" "),
        ]


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_failed_verbose3_with_scope(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, verbose=3)

        scenario_result = make_scenario_result()

        step_result_passed = make_step_result().mark_passed()
        scenario_result.add_step_result(step_result_passed)

        exc_info = make_exc_info(AssertionError())
        step_result_failed = make_step_result().mark_failed().set_exc_info(exc_info)
        scenario_result.add_step_result(step_result_failed)

        scope = {"key": "val"}
        scenario_result.set_scope(scope)

        aggregated_result = make_aggregated_result(scenario_result.mark_failed())
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

            call.print_pretty_exception(exc_info, max_frames=8, show_locals=False,
                                        show_internal_calls=False),
            call.print_scope(scope)
        ]
