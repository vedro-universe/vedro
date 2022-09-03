from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioStatus
from vedro.events import ScenarioReportedEvent

from ._utils import (
    director,
    dispatcher,
    fire_arg_parsed_event,
    make_aggregated_result,
    make_scenario_result,
    printer_,
    rich_reporter,
)

__all__ = ("dispatcher", "rich_reporter", "director", "printer_")  # fixtures


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
@pytest.mark.usefixtures(rich_reporter.__name__)
async def test_scenario_passed_show_paths(*, dispatcher: Dispatcher, printer_: Mock):
    with given:
        await fire_arg_parsed_event(dispatcher, show_paths=True)

        scenario_result = make_scenario_result().mark_passed()
        aggregated_result = make_aggregated_result(scenario_result)
        event = ScenarioReportedEvent(aggregated_result)

    with when:
        await dispatcher.fire(event)

    with then:
        subject = aggregated_result.scenario.subject
        assert printer_.mock_calls == [
            call.print_scenario_subject(subject, ScenarioStatus.PASSED, elapsed=None, prefix=" "),
            call.print_scenario_caption(f"> {scenario_result.scenario.path.name}", prefix=" " * 3)
        ]
