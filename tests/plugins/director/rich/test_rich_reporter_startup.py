from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro.events import StartupEvent
from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import console_, dispatcher, reporter

__all__ = ("dispatcher", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_startup_event(*, dispatcher: Dispatcher,
                                           reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)
        event = StartupEvent([])

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [
            call.out("Scenarios")
        ]
