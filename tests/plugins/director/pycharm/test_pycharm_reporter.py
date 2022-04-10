from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.director import (
    DirectorInitEvent,
    DirectorPlugin,
    PyCharmReporter,
    PyCharmReporterPlugin,
)


@pytest.mark.asyncio
async def test_pycharm_reporter_subscribe():
    with given:
        dispatcher = Dispatcher()
        director_ = Mock(DirectorPlugin)

        reporter = PyCharmReporterPlugin(PyCharmReporter)
        reporter.subscribe(dispatcher)

    with when:
        await dispatcher.fire(DirectorInitEvent(director_))

    with then:
        assert director_.mock_calls == [
            call.register("pycharm", reporter)
        ]


def test_pycharm_reporter_on_chosen():
    with given:
        dispatcher = Dispatcher()

        reporter = PyCharmReporterPlugin(PyCharmReporter)
        reporter.subscribe(dispatcher)

    with when:
        res = reporter.on_chosen()

    with then:
        assert res is None
