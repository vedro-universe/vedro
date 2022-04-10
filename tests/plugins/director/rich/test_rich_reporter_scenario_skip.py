from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.events import ScenarioSkippedEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import (
    chose_reporter,
    console_,
    director,
    dispatcher,
    make_scenario_result,
    reporter,
)

__all__ = ("dispatcher", "reporter", "director", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_scenario_skip_event(*, dispatcher: Dispatcher,
                                                 director: DirectorPlugin,
                                                 reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        scenario_result = make_scenario_result()
        event = ScenarioSkippedEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []
