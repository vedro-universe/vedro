from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.events import ArgParsedEvent
from vedro.plugins.director import DirectorPlugin, RichReporterPlugin
from vedro.plugins.director.rich.test_utils import (
    chose_reporter,
    console_,
    director,
    dispatcher,
    make_parsed_args,
    reporter,
)

__all__ = ("dispatcher", "reporter", "director", "console_",)


@pytest.mark.asyncio
async def test_rich_reporter_arg_parsed_event(*, dispatcher: Dispatcher, director: DirectorPlugin,
                                              reporter: RichReporterPlugin, console_: Mock):
    with given:
        await chose_reporter(dispatcher, director, reporter)

        args = make_parsed_args()
        event = ArgParsedEvent(args)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == []
