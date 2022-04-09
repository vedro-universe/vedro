from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.director import Reporter


def test_reporter_on_chosen():
    with given:
        reporter = Reporter()

    with when, raises(BaseException) as exception:
        reporter.on_chosen()

    with then:
        assert exception.type is NotImplementedError
