from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Style

from vedro.core import Dispatcher, ScenarioResult
from vedro.events import ArgParsedEvent, ScenarioFailedEvent, ScenarioPassedEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import (
    chose_reporter,
    console_,
    director,
    dispatcher,
    make_parsed_args,
    make_vscenario,
    reporter,
)

__all__ = ("dispatcher", "director", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter(*, dispatcher: Dispatcher, director: DirectorPlugin,
                             reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        event = ArgParsedEvent(make_parsed_args(reruns=1))
        await dispatcher.fire(event)

        vscenario = make_vscenario()
        scenario_result = ScenarioResult(vscenario, rerun=0).mark_failed()
        event = ScenarioFailedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_failed(*, dispatcher: Dispatcher, director: DirectorPlugin,
                                    reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        event = ArgParsedEvent(make_parsed_args(reruns=1))
        await dispatcher.fire(event)

        subject = "<subject>"
        vscenario = make_vscenario(subject=subject)

        scenario_result1 = ScenarioResult(vscenario, rerun=0).mark_failed()
        event1 = ScenarioFailedEvent(scenario_result1)
        await dispatcher.fire(event1)

        scenario_result2 = ScenarioResult(vscenario, rerun=1).mark_failed()
        event2 = ScenarioFailedEvent(scenario_result2)

    with when:
        await dispatcher.fire(event2)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✗ {subject}", style=Style.parse("red")),

            call.out(" │"),
            call.out(" ├─[1/2]", end=""),
            call.out(f" ✗ {subject}", style=Style.parse("red")),

            call.out(" │"),
            call.out(" ├─[2/2]", end=""),
            call.out(f" ✗ {subject}", style=Style.parse("red")),

            call.out(" ")
        ]


@pytest.mark.asyncio
async def test_rich_reporter_passed(*, dispatcher: Dispatcher, director: DirectorPlugin,
                                    reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        event = ArgParsedEvent(make_parsed_args(reruns=2))
        await dispatcher.fire(event)

        subject = "<subject>"
        vscenario = make_vscenario(subject=subject)

        scenario_result1 = ScenarioResult(vscenario, rerun=0).mark_failed()
        event1 = ScenarioFailedEvent(scenario_result1)
        await dispatcher.fire(event1)

        scenario_result2 = ScenarioResult(vscenario, rerun=1).mark_passed()
        event2 = ScenarioPassedEvent(scenario_result2)
        await dispatcher.fire(event2)

        scenario_result3 = ScenarioResult(vscenario, rerun=2).mark_passed()
        event3 = ScenarioPassedEvent(scenario_result3)

    with when:
        await dispatcher.fire(event3)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✔ {subject}", style=Style.parse("green")),

            call.out(" │"),
            call.out(" ├─[1/3]", end=""),
            call.out(f" ✗ {subject}", style=Style.parse("red")),

            call.out(" │"),
            call.out(" ├─[2/3]", end=""),
            call.out(f" ✔ {subject}", style=Style.parse("green")),

            call.out(" │"),
            call.out(" ├─[3/3]", end=""),
            call.out(f" ✔ {subject}", style=Style.parse("green")),

            call.out(" ")
        ]
