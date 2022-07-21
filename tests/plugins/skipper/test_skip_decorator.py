from baby_steps import then, when
from pytest import raises

from vedro import Scenario
from vedro.plugins.skipper import skip


def test_skip():
    with when:
        @skip
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__skipped__") is True


def test_skip_called():
    with when:
        @skip()
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__skipped__") is True


def test_skip_not_subclass():
    with when, raises(Exception) as exc:
        @skip
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
