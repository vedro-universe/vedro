from baby_steps import then, when
from pytest import raises

from vedro import Scenario
from vedro.plugins.skipper import only


def test_only():
    with when:
        @only
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__only__") is True


def test_only_called():
    with when:
        @only()
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__only__") is True


def test_only_not_subclass():
    with when, raises(Exception) as exc:
        @only
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
