from baby_steps import given, then, when
from niltype import Nil
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
        assert getattr(_Scenario, "__vedro__skip_reason__", Nil) is Nil


def test_skip_called():
    with when:
        @skip()
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__skipped__") is True
        assert getattr(_Scenario, "__vedro__skip_reason__", Nil) is Nil


def test_skip_called_with_reason():
    with given:
        reason = "<reason>"

    with when:
        @skip(reason)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert getattr(_Scenario, "__vedro__skipped__") is True
        assert getattr(_Scenario, "__vedro__skip_reason__") == reason


def test_skip_not_subclass():
    with when, raises(BaseException) as exc:
        @skip
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == ("Decorator @skip can be used only with """
                                  "'vedro.Scenario' subclasses")


def test_skip_called_not_subclass():
    with when, raises(BaseException) as exc:
        @skip()
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == ("Decorator @skip can be used only with """
                                  "'vedro.Scenario' subclasses")


def test_skip_called_with_incorrect_arg():
    with when, raises(BaseException) as exc:
        @skip(1)
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == 'Usage: @skip or @skip("reason")'
