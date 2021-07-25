import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from collections import deque
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher, Plugin, ScenarioResult, VirtualScenario
from vedro.events import ScenarioFailedEvent, ScenarioPassedEvent, ScenarioRunEvent
from vedro.plugins.deferrer import Deferrer


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def queue() -> deque:
    return deque()


@pytest.fixture()
def deferrer(queue) -> Deferrer:
    return Deferrer(queue)


def test_deferrer_plugin():
    with when:
        plugin = Deferrer()

    with then:
        assert isinstance(plugin, Plugin)


@pytest.mark.asyncio
async def test_deferrer_scenario_run_event(*, dispatcher: Dispatcher,
                                           deferrer: Deferrer, queue: deque):
    with given:
        deferrer.subscribe(dispatcher)

        scenario_result = ScenarioResult(Mock(VirtualScenario))
        event = ScenarioRunEvent(scenario_result)

        queue.append((Mock(), (), {}))

    with when:
        await dispatcher.fire(event)

    with then:
        assert len(queue) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_deferrer_scenario_end_event(event_class, *, dispatcher: Dispatcher,
                                           deferrer: Deferrer, queue: deque):
    with given:
        deferrer.subscribe(dispatcher)
        scenario_result = ScenarioResult(Mock(VirtualScenario))
        event = event_class(scenario_result)

        manager = Mock()
        deferred1 = Mock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = Mock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        queue.append((deferred2, args2, kwargs2))

    with when:
        await dispatcher.fire(event)

    with then:
        assert manager.mock_calls == [
            call.deferred2(*args2, **kwargs2),
            call.deferred1(*args1, **kwargs1),
        ]
        assert len(queue) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("event_class", [ScenarioPassedEvent, ScenarioFailedEvent])
async def test_deferrer_scenario_end_event_async(event_class, *, dispatcher: Dispatcher,
                                                 deferrer: Deferrer, queue: deque):
    with given:
        deferrer.subscribe(dispatcher)
        scenario_result = ScenarioResult(Mock(VirtualScenario))
        event = event_class(scenario_result)

        manager = Mock()
        deferred1 = AsyncMock()
        manager.attach_mock(deferred1, "deferred1")
        deferred2 = AsyncMock()
        manager.attach_mock(deferred2, "deferred2")

        args1, kwargs1 = ("arg1", "arg2"), {"key1": "val1"}
        queue.append((deferred1, args1, kwargs1))
        args2, kwargs2 = ("arg3", "arg4"), {"key2": "val2"}
        queue.append((deferred2, args2, kwargs2))

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
