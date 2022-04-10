from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.events import StartupEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import (
    chose_reporter,
    console_,
    director,
    dispatcher,
    reporter,
)

__all__ = ("dispatcher", "reporter", "director", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_startup_event(*, dispatcher: Dispatcher, director: DirectorPlugin,
                                           reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)
        event = StartupEvent([])

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out("Scenarios")
        ]
