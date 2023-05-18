from baby_steps import then, when
from pytest import raises

from vedro import Scenario
from vedro.plugins.skipper import only

from ._utils import get_only_attr


def test_only():
    with when:
        @only
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_only_attr(_Scenario) is True


def test_only_called():
    with when:
        @only()
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_only_attr(_Scenario) is True


def test_only_not_subclass():
    with when, raises(BaseException) as exc:
        @only
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == ("Decorator @only can be used only with """
                                  "'vedro.Scenario' subclasses")


def test_only_called_not_subclass():
    with when, raises(BaseException) as exc:
        @only()
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == ("Decorator @only can be used only with """
                                  "'vedro.Scenario' subclasses")


def test_only_called_with_incorrect_arg():
    with when, raises(BaseException) as exc:
        @only("smth")
        class _Scenario(Scenario):
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "Usage: @only"
