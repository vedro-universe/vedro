import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from time import monotonic_ns
from typing import Type, cast
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro._core._dispatcher import Subscriber
from vedro.events import Event


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.fixture()
def event_type() -> Type[Event]:
    name = "CustomEvent_{}".format(monotonic_ns())
    return cast(Type[Event], type(name, (Event,), {}))


def test_dispatcher_register(*, dispatcher: Dispatcher):
    with given:
        subcriber_ = Mock(Subscriber)

    with when:
        res = dispatcher.register(subcriber_)

    with then:
        assert res is None
        assert subcriber_.mock_calls == [call.subscribe(dispatcher)]


def test_dispatcher_listen(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with when:
        res = dispatcher.listen(event_type, lambda e: None)

    with then:
        assert res == dispatcher


@pytest.mark.asyncio
async def test_dispatcher_fire_unknown_event(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_factory", (Mock, AsyncMock))
async def test_dispatcher_fire(mock_factory, *, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        subscribe_ = mock_factory()
        dispatcher.listen(event_type, subscribe_)
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert subscribe_.mock_calls == [call(event)]


@pytest.mark.asyncio
async def test_dispatcher_fire_twice(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        subscribe_ = Mock()
        dispatcher.listen(event_type, subscribe_)
        event = event_type()
        await dispatcher.fire(event)

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert subscribe_.mock_calls == [call(event), call(event)]


@pytest.mark.asyncio
async def test_dispatcher_fire_default_order(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        manager_ = Mock()
        subscribe1_, subscribe2_ = Mock(), Mock()
        manager_.attach_mock(subscribe1_, "subscribe1_")
        manager_.attach_mock(subscribe2_, "subscribe2_")

        dispatcher.listen(event_type, subscribe2_)
        dispatcher.listen(event_type, subscribe1_)
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert manager_.mock_calls == [call.subscribe2_(event), call.subscribe1_(event)]


@pytest.mark.asyncio
async def test_dispatcher_fire_priority_order(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        manager_ = Mock()
        subscribe1_, subscribe2_ = Mock(), Mock()
        manager_.attach_mock(subscribe1_, "subscribe1_")
        manager_.attach_mock(subscribe2_, "subscribe2_")

        dispatcher.listen(event_type, subscribe2_, priority=1)
        dispatcher.listen(event_type, subscribe1_)
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert manager_.mock_calls == [call.subscribe1_(event), call.subscribe2_(event)]


@pytest.mark.asyncio
async def test_dispatcher_fire_listen_default_order(*, dispatcher: Dispatcher,
                                                    event_type: Type[Event]):
    with given:
        subscribe3_ = Mock()

        def handler(e):
            dispatcher.listen(event_type, subscribe3_)
        subscribe1_, subscribe2_ = Mock(), Mock(side_effect=handler)

        manager_ = Mock()
        manager_.attach_mock(subscribe1_, "subscribe1_")
        manager_.attach_mock(subscribe2_, "subscribe2_")
        manager_.attach_mock(subscribe3_, "subscribe3_")

        dispatcher.listen(event_type, subscribe2_)
        dispatcher.listen(event_type, subscribe1_)
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert manager_.mock_calls == [
            call.subscribe2_(event),
            call.subscribe1_(event),
            call.subscribe3_(event),
        ]


@pytest.mark.asyncio
async def test_dispatcher_fire_listen_priority_order(*, dispatcher: Dispatcher,
                                                     event_type: Type[Event]):
    with given:
        subscribe3_ = Mock()

        def handler(e):
            dispatcher.listen(event_type, subscribe3_)
        subscribe1_, subscribe2_ = Mock(), Mock(side_effect=handler)

        manager_ = Mock()
        manager_.attach_mock(subscribe1_, "subscribe1_")
        manager_.attach_mock(subscribe2_, "subscribe2_")
        manager_.attach_mock(subscribe3_, "subscribe3_")

        dispatcher.listen(event_type, subscribe2_)
        dispatcher.listen(event_type, subscribe1_, priority=1)
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert manager_.mock_calls == [
            call.subscribe2_(event),
            call.subscribe3_(event),
            call.subscribe1_(event),
        ]
