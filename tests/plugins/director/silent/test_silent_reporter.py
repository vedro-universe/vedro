from unittest.mock import Mock

from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro.plugins.director import SilentReporter


def test_silent_reporter():
    with given:
        dispatcher_ = Mock(Dispatcher())
        reporter = SilentReporter()

    with when:
        res = reporter.subscribe(dispatcher_)

    with then:
        assert res is None
        assert dispatcher_.mock_calls == []
