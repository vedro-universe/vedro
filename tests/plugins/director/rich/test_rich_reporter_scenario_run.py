from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Style

from vedro.core import Dispatcher, ScenarioResult
from vedro.events import ScenarioRunEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import (
    chose_reporter,
    console_,
    director,
    dispatcher,
    make_path,
    make_scenario_result,
    make_vscenario,
    reporter,
)

__all__ = ("dispatcher", "reporter", "director", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event(*, dispatcher: Dispatcher,
                                                director: DirectorPlugin,
                                                reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        vscenario = make_vscenario(path=make_path("<namespace_1>"))
        scenario_result = ScenarioResult(vscenario)
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out("* <namespace 1>", style=Style.parse("bold"))
        ]


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event_same_namespace(*, dispatcher: Dispatcher,
                                                               director: DirectorPlugin,
                                                               reporter: RichReporterPlugin,
                                                               console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        vscenario = make_vscenario(path=make_path("<namespace_1>"))
        scenario_result = make_scenario_result(vscenario)
        event = ScenarioRunEvent(scenario_result)

        await dispatcher.fire(event)
        console_.reset_mock()

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []


@pytest.mark.asyncio
async def test_rich_reporter_scenario_run_event_diff_namespace(*, dispatcher: Dispatcher,
                                                               director: DirectorPlugin,
                                                               reporter: RichReporterPlugin,
                                                               console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        vscenario = make_vscenario(path=make_path("<namespace_1>"))
        scenario_result1 = ScenarioResult(vscenario)
        event1 = ScenarioRunEvent(scenario_result1)
        await dispatcher.fire(event1)
        console_.reset_mock()

        vscenario = make_vscenario(path=make_path("<namespace_2>"))
        scenario_result2 = ScenarioResult(vscenario)
        event2 = ScenarioRunEvent(scenario_result2)

    with when:
        await dispatcher.fire(event2)

    with then:
        assert console_.mock_calls == [
            call.out("* <namespace 2>", style=Style.parse("bold")),
        ]
