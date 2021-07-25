from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro.events import ArgParsedEvent
from vedro.plugins.director import RichReporter
from vedro.plugins.director.rich.test_utils import console_, dispatcher, make_parsed_args, reporter

__all__ = ("dispatcher", "reporter", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_arg_parsed_event(*, dispatcher: Dispatcher,
                                              reporter: RichReporter, console_: Mock):
    with given:
        reporter.subscribe(dispatcher)

        args = make_parsed_args()
        event = ArgParsedEvent(args)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []
