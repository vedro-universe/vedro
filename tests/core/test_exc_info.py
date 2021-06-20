import sys

from baby_steps import given, then, when

from vedro._core import ExcInfo


def test_exc_info():
    with given:
        try:
            raise AssertionError()
        except AssertionError:
            exc_type, exc_value, exc_tb = sys.exc_info()

    with when:
        exc_info = ExcInfo(exc_type, exc_value, exc_tb)

    with then:
        assert exc_info.type == exc_type
        assert exc_info.value == exc_value
        assert exc_info.traceback == exc_tb

        assert repr(exc_info) == f"ExcInfo(<class 'AssertionError'>, AssertionError(), {exc_tb!r})"
