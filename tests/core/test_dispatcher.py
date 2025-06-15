from time import monotonic_ns
from typing import Type, cast
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher, Event, Subscriber
from vedro.core._dispatcher import EventHandler


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


async def test_dispatcher_fire_unknown_event(*, dispatcher: Dispatcher, event_type: Type[Event]):
    with given:
        event = event_type()

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


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


def test_dispatcher_listen_invalid_event_type(*, dispatcher: Dispatcher):
    with given:
        class CustomEvent:
            pass

    with when, raises(BaseException) as exc:
        dispatcher.listen(CustomEvent, lambda e: None)

    with then:
        assert type(exc.value) is TypeError
        assert str(exc.value) == "Event must be a subclass of 'vedro.events.Event'"


def test_event_handler_comparison():
    with given:
        handler1 = EventHandler(priority=0, registered_at=-1, handler=lambda e: None)
        handler2 = EventHandler(priority=1, registered_at=-1, handler=lambda e: None)

    with when:
        result = handler1 < handler2

    with then:
        assert result is True


def test_event_handler_comparison_invalid_type():
    with given:
        handler = EventHandler(priority=0, registered_at=-1, handler=lambda e: None)

    with when, raises(BaseException) as exc:
        handler < 5

    with then:
        assert type(exc.value) is TypeError
        assert str(exc.value) == "Other must be an instance of EventHandler"
