from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro import Scenario
from vedro.plugins.skipper import skip_if

from ._utils import get_skip_attr, get_skip_reason_attr


def test_skip_if_truthy():
    with when:
        @skip_if(lambda: True)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) is Nil


def test_skip_if_falsy():
    with when:
        @skip_if(lambda: False)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is False
        assert get_skip_reason_attr(_Scenario) is Nil


def test_skip_if_with_reason():
    with given:
        reason = "<reason>"

    with when:
        @skip_if(lambda: True, reason)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) == reason


def test_skip_if_not_subclass():
    with when, raises(BaseException) as exc:
        @skip_if(lambda: True)
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == ("Decorator @skip_if can be used only with "
                                  "'vedro.Scenario' subclasses")


def test_skip_if():
    with when, raises(BaseException) as exc:
        @skip_if
        class _Scenario(Scenario):
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == 'Usage: @skip_if(<condition>, "reason?")'


def test_skip_if_not_callable():
    with when, raises(BaseException) as exc:
        @skip_if("not callable")
        class _Scenario(Scenario):
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == 'Usage: @skip_if(<condition>, "reason?")'
