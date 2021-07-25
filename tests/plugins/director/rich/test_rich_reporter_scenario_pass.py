from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from rich.console import Style

from vedro._core import Dispatcher, ScenarioResult
from vedro.events import ScenarioPassedEvent
from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import console_, dispatcher, make_vscenario, reporter

__all__ = ("dispatcher", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_scenario_pass_event(*, dispatcher: Dispatcher,
                                                 reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        subject = "<subject>"
        vscenario = make_vscenario(subject=subject)
        scenario_result = ScenarioResult(vscenario).mark_passed()
        event = ScenarioPassedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out(f" ✔ {subject}", style=Style.parse("green"))
        ]
