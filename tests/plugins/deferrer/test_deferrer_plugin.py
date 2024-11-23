from collections import deque
from unittest.mock import AsyncMock, Mock, call

import pytest
from baby_steps import given, then, when

from vedro import defer
from vedro.core import Dispatcher, Report, ScenarioResult
from vedro.core.scenario_scheduler import MonotonicScenarioScheduler as ScenarioScheduler
from vedro.events import (
    CleanupEvent,
    ScenarioFailedEvent,
    ScenarioPassedEvent,
    ScenarioRunEvent,
    StartupEvent,
)
from vedro.plugins.deferrer import Deferrer, DeferrerPlugin

from ._utils import deferrer, dispatcher, global_queue, make_vscenario, queue

__all__ = ("dispatcher", "deferrer", "queue", "global_queue",)  # fixtures


@pytest.mark.usefixtures(deferrer.__name__)
async def test_scenario_startup_event(*, dispatcher: Dispatcher, global_queue: deque):
    with given:
        global_queue.append((Mock(), (), {}))

        event = StartupEvent(ScenarioScheduler(scenarios=[]))

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(global_queue) == 0


@pytest.mark.usefixtures(deferrer.__name__)
async def test_scenario_run_event(*, dispatcher: Dispatcher, queue: deque):
    with given:
        queue.append((Mock(), (), {}))

        scenario_result = ScenarioResult(make_vscenario())
        event = ScenarioRunEvent(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(queue) == 0


@pytest.mark.usefixtures(deferrer.__name__)
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_scenario_end_event(event_class, *, dispatcher: Dispatcher, queue: deque):
    with given:
        manager = Mock()
        deferred1 = Mock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = Mock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        queue.append((deferred2, args2, kwargs2))

        scenario_result = ScenarioResult(make_vscenario())
        event = event_class(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        assert len(queue) == 0


@pytest.mark.usefixtures(deferrer.__name__)
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_scenario_end_event_async(event_class, *, dispatcher: Dispatcher, queue: deque):
    with given:
        manager = Mock()
        deferred1 = AsyncMock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = AsyncMock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        queue.append((deferred2, args2, kwargs2))

        scenario_result = ScenarioResult(make_vscenario())
        event = event_class(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        deferred1.assert_awaited_once()
        deferred2.assert_awaited_once()
        assert len(queue) == 0


@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_scenario_end_event_sync_async(event_class, *, dispatcher: Dispatcher):
    with given:
        deferrer = DeferrerPlugin(Deferrer)
        deferrer.subscribe(dispatcher)

        manager = Mock()
        deferred1 = AsyncMock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = Mock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        defer(deferred1, *args1, **kwargs1)
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        defer(deferred2, *args2, **kwargs2)

        scenario_result = ScenarioResult(make_vscenario())
        event = event_class(scenario_result)

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        deferred1.assert_awaited_once()


@pytest.mark.usefixtures(deferrer.__name__)
async def test_global_deferral(*, dispatcher: Dispatcher, global_queue: deque):
    with given:
        manager = Mock()
        deferred1 = Mock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = Mock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        global_queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        global_queue.append((deferred2, args2, kwargs2))

        event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        assert len(global_queue) == 0


@pytest.mark.usefixtures(deferrer.__name__)
async def test_global_deferral_async(*, dispatcher: Dispatcher, global_queue: deque):
    with given:
        manager = Mock()
        deferred1 = AsyncMock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = AsyncMock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        global_queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        global_queue.append((deferred2, args2, kwargs2))

        event = CleanupEvent(Report())

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        deferred1.assert_awaited_once()
        deferred2.assert_awaited_once()
        assert len(global_queue) == 0
