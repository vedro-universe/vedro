from types import MethodType
from unittest.mock import AsyncMock, Mock, call, sentinel

from baby_steps import given, then, when

from vedro.core import VirtualStep


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
        method_ = Mock(MethodType)
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
        name = "step"
        method_ = Mock(MethodType, __name__=name)
        step = VirtualStep(method_)

    with when:
        res = repr(step)

    with then:
        assert res == f"<VirtualStep {name!r}>"


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


def test_virtual_step_doc():
    with given:
        async def my_step():  # could be sync too – doesn’t matter here
            """Adds a product to the basket"""
        step = VirtualStep(my_step)

    with when:
        doc = step.doc

    with then:
        assert doc == "Adds a product to the basket"


def test_virtual_step_doc_multiline():
    with given:
        def my_step():
            """
            Step first line
            Step second line
            """
        step = VirtualStep(my_step)

    with when:
        doc = step.doc

    with then:
        assert doc == "Step first line\nStep second line"


def test_virtual_step_doc_when_absent():
    with given:
        def my_step():
            pass  # no docstring
        step = VirtualStep(my_step)

    with when:
        doc = step.doc

    with then:
        assert doc is None
