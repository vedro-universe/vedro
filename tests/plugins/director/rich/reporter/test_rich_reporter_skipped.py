from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioStatus
from vedro.events import ScenarioReportedEvent, ScenarioSkippedEvent
from vedro.plugins.director import RichReporterPlugin

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_scenario_result,
    make_vscenario,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_skipped()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=None, prefix=" ")
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_with_reason(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, hide_namespaces=True)

        reason = "<reason>"
        vscenario = make_vscenario()
        vscenario.skip(reason)

        scenario_result = make_scenario_result(vscenario).mark_skipped()
        await dispatcher.fire(ScenarioSkippedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details([f"{reason}"],
                                              prefix=" " * 3)
        ]


async def test_scenario_skipped_with_reason_disabled(*, dispatcher: Dispatcher,
                                                     rich_reporter: RichReporterPlugin,
                                                     printer_: Mock):
    with given:
        rich_reporter._show_skip_reason = False  # move to config
        await fire_arg_parsed_event(dispatcher)

        vscenario = make_vscenario()
        vscenario.skip("<reason>")

        scenario_result = make_scenario_result(vscenario).mark_skipped()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=None, prefix=" ")
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_show_paths(dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True, hide_namespaces=True)

        scenario_result = make_scenario_result().mark_skipped()
        await dispatcher.fire(ScenarioSkippedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details([f"{scenario_result.scenario.path.name}"],
                                              prefix=" " * 3)
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_with_reason_and_paths(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True, hide_namespaces=True)

        reason = "<reason>"
        vscenario = make_vscenario()
        vscenario.skip(reason)

        scenario_result = make_scenario_result(vscenario).mark_skipped()
        await dispatcher.fire(ScenarioSkippedEvent(scenario_result))

        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=None, prefix=" "),
            call.print_scenario_extra_details(
                [f"{reason}", f"{scenario_result.scenario.path.name}"],
                prefix=" " * 3
            )
        ]


@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_skipped_show_timings(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_timings=True)

        scenario_result = make_scenario_result().mark_skipped() \
                                                .set_started_at(1.0).set_ended_at(3.0)
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.SKIPPED, elapsed=2.0, prefix=" ")
        ]


async def test_scenario_skipped_disabled(*, dispatcher: Dispatcher,
                                         rich_reporter: RichReporterPlugin, printer_: Mock):
    with given:
        rich_reporter._show_skipped = False
        await fire_arg_parsed_event(dispatcher)

        scenario_result = make_scenario_result().mark_skipped()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert printer_.mock_calls == []
