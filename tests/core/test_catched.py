from types import TracebackType

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro import catched


def test_catched_with_expected_exception():
    with given:
        exc = ValueError("msg")

    with when:
        with catched(ValueError) as exc_info:
            raise exc

    with then:
        assert exc_info.type is ValueError
        assert exc_info.value == exc
        assert isinstance(exc_info.traceback, TracebackType)

        assert repr(exc_info) == f"<catched exception={exc!r}>"


def test_catched_with_no_exception():
    with when:
        with catched(ValueError) as exc_info:
            pass

    with then:
        assert exc_info.type is None
        assert exc_info.value is None
        assert exc_info.traceback is None

        assert repr(exc_info) == "<catched exception=None>"


def test_catched_with_unexpected_exception():
    with when, raises(KeyError) as excinfo:
        with catched(ValueError) as exc_info:
            raise KeyError("msg")

    with then:
        assert excinfo.type is KeyError
        assert str(excinfo.value) == "'msg'"

        assert exc_info.type is None
        assert exc_info.value is None
        assert exc_info.traceback is None


@pytest.mark.parametrize("exc", [ValueError("msg"), KeyError("msg")])
def test_catched_with_multiple_exception_types(exc: Exception):
    with when:
        with catched((ValueError, KeyError)) as exc_info:
            raise exc

    with then:
        assert exc_info.type is type(exc)
        assert exc_info.value == exc
        assert isinstance(exc_info.traceback, TracebackType)


@pytest.mark.asyncio
async def test_async_catched_with_expected_exception():
    with given:
        exc = ValueError("msg")

    with when:
        async with catched(ValueError) as exc_info:
            raise exc

    with then:
        assert exc_info.type is ValueError
        assert exc_info.value == exc
        assert isinstance(exc_info.traceback, TracebackType)

        assert repr(exc_info) == f"<catched exception={exc!r}>"


async def test_async_catched_with_no_exception():
    with when:
        async with catched(ValueError) as exc_info:
            pass

    with then:
        assert exc_info.type is None
        assert exc_info.value is None
        assert exc_info.traceback is None

        assert repr(exc_info) == "<catched exception=None>"


async def test_async_catched_with_unexpected_exception():
    with when, raises(KeyError) as excinfo:
        async with catched(ValueError) as exc_info:
            raise KeyError("msg")

    with then:
        assert excinfo.type is KeyError
        assert str(excinfo.value) == "'msg'"

        assert exc_info.type is None
        assert exc_info.value is None
        assert exc_info.traceback is None


@pytest.mark.asyncio
@pytest.mark.parametrize("exc", [ValueError("msg"), KeyError("msg")])
async def test_async_catched_with_multiple_exception_types(exc: Exception):
    with when:
        async with catched((ValueError, KeyError)) as exc_info:
            raise exc

    with then:
        assert exc_info.type is type(exc)
        assert exc_info.value == exc
        assert isinstance(exc_info.traceback, TracebackType)
