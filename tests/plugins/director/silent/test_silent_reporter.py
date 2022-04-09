from unittest.mock import Mock

from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.director import SilentReporterPlugin


def test_silent_reporter():
    with given:
        dispatcher_ = Mock(Dispatcher())
        reporter = SilentReporterPlugin()

    with when:
        res = reporter.subscribe(dispatcher_)

    with then:
        assert res is None
        assert dispatcher_.mock_calls == []
