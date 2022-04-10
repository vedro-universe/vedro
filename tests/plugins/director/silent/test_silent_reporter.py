from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.director import (
    DirectorInitEvent,
    DirectorPlugin,
    SilentReporter,
    SilentReporterPlugin,
)


@pytest.mark.asyncio
async def test_silent_reporter_subscribe():
    with given:
        dispatcher = Dispatcher()
        director_ = Mock(DirectorPlugin)

        reporter = SilentReporterPlugin(SilentReporter)
        reporter.subscribe(dispatcher)

    with when:
        await dispatcher.fire(DirectorInitEvent(director_))

    with then:
        assert director_.mock_calls == [
            call.register("silent", reporter)
        ]


def test_silent_reporter_on_chosen():
    with given:
        dispatcher = Dispatcher()

        reporter = SilentReporterPlugin(SilentReporter)
        reporter.subscribe(dispatcher)

    with when:
        res = reporter.on_chosen()

    with then:
        assert res is None
