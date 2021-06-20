import sys

import pytest

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from types import MethodType
from unittest.mock import Mock, call, sentinel

from baby_steps import given, then, when

from vedro._core import VirtualStep


def test_virtual_step_name():
    with given:
        method_ = Mock(MethodType)
        method_.__name__ = "<name>"
        step = VirtualStep(method_)

    with when:
        res = step.name

    with then:
        assert res == method_.__name__


def test_virtual_step_is_coro_sync():
    with given:
        method_ = Mock(MethodType, __code__=Mock(co_flags=0))  # python 3.7 specific
        step = VirtualStep(method_)

    with when:
        res = step.is_coro()

    with then:
        assert res is False


def test_virtual_step_is_coro_async():
    with given:
        method_ = AsyncMock(MethodType)
        step = VirtualStep(method_)

    with when:
        res = step.is_coro()

    with then:
        assert res is True


def test_virtual_step_call_sync():
    with given:
        method_ = Mock(MethodType, return_value=sentinel)
        step = VirtualStep(method_)

    with when:
        res = step()

    with then:
        assert res == sentinel
        assert method_.mock_calls == [call()]


@pytest.mark.asyncio
async def test_virtual_step_call_async():
    with given:
        method_ = AsyncMock(MethodType, return_value=sentinel)
        step = VirtualStep(method_)

    with when:
        res = await step()

    with then:
        assert res == sentinel
        assert method_.mock_calls == [call()]


def test_virtual_step_repr():
    with given:
        method_ = Mock(MethodType)
        step = VirtualStep(method_)

    with when:
        res = repr(step)

    with then:
        assert res == f"VirtualStep({method_!r})"


def test_virtual_step_eq():
    with given:
        method_ = Mock(MethodType)
        step1 = VirtualStep(method_)
        step2 = VirtualStep(method_)

    with when:
        res = step1 == step2

    with then:
        assert res is True


def test_virtual_step_not_eq():
    with given:
        method1_ = Mock(MethodType)
        step1 = VirtualStep(method1_)
        method2_ = Mock(MethodType)
        step2 = VirtualStep(method2_)

    with when:
        res = step1 == step2

    with then:
        assert res is False
