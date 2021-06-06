from argparse import Namespace
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro._events import ArgParsedEvent, StartupEvent
from vedro.plugins.director import RichReporter


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.mark.asyncio
async def test_rich_reporter_arg_parsed_event(*, dispatcher: Dispatcher):
    with given:
        console_ = Mock()
        reporter = RichReporter(console_)
        reporter.subscribe(dispatcher)
        args = Namespace(verbose=0)
        event = ArgParsedEvent(args)

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [call()]


@pytest.mark.asyncio
async def test_rich_reporter_startup_event(*, dispatcher: Dispatcher):
    with given:
        console_ = Mock()
        reporter = RichReporter(console_)
        reporter.subscribe(dispatcher)

        args = Namespace(verbose=0)
        await dispatcher.fire(ArgParsedEvent(args))

        event = StartupEvent([])
        console_.reset_mock()

    with when:
        await dispatcher.fire(event)

    with then:
        assert console_.mock_calls == [call().print('Scenarios')]
