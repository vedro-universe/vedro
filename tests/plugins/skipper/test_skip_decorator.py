from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro import Scenario
from vedro.plugins.skipper import skip

from ._utils import get_skip_attr, get_skip_reason_attr


def test_skip():
    with when:
        @skip
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) is Nil


def test_skip_called():
    with when:
        @skip()
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) is Nil


def test_skip_called_with_reason():
    with given:
        reason = "<reason>"

    with when:
        @skip(reason)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) == reason


def test_skip_called_with_reason_kwarg():
    with given:
        reason = "<reason>"

    with when:
        @skip(reason=reason)
        class _Scenario(Scenario):
            pass

    with then:
        assert issubclass(_Scenario, Scenario)
        assert get_skip_attr(_Scenario) is True
        assert get_skip_reason_attr(_Scenario) == reason


def test_skip_not_subclass():
    with when, raises(BaseException) as exc:
        @skip
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value).startswith("Decorator @skip can be used only with Vedro scenarios:")


def test_skip_not_subclass_with_reason():
    with when, raises(BaseException) as exc:
        @skip("<reason>")
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value).startswith("Decorator @skip can be used only with Vedro scenarios:")


def test_skip_called_not_subclass():
    with when, raises(BaseException) as exc:
        @skip()
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value).startswith("Decorator @skip can be used only with Vedro scenarios:")


def test_skip_called_with_incorrect_arg():
    with when, raises(BaseException) as exc:
        @skip(1)
        class _Scenario:
            pass

    with then:
        assert exc.type is TypeError
        assert str(exc.value).startswith("Decorator @skip can be used only with Vedro scenarios:")
