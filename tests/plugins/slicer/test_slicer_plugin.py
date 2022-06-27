from argparse import Namespace
from typing import Set, Union

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.core import MonotonicScenarioScheduler as Scheduler
from vedro.events import ArgParsedEvent, StartupEvent
from vedro.plugins.slicer import SlicerPlugin

from ._utils import dispatcher, fire_arg_parsed_event, make_vscenario, slicer

__all__ = ("dispatcher", "slicer",)


@pytest.mark.parametrize(("total", "index", "selected"), [
    (None, None, {0, 1, 2, 3}),
    (1, 0, {0, 2, 3}),

    (2, 0, {0, 3}),
    (2, 1, {2}),

    (3, 0, {0}),
    (3, 1, {2}),
    (3, 2, {3}),
])
@pytest.mark.asyncio
async def test_slicing(total: int, index: int, selected: Set[int], *,
                       slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, total=total, index=index)

        scenarios = [
            make_vscenario(),
            make_vscenario(is_skipped=True),
            make_vscenario(),
            make_vscenario()
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[i] for i in selected]


@pytest.mark.parametrize(("total", "index", "selected"), [
    (None, None, {0, 1}),
    (1, 0, {}),
])
@pytest.mark.asyncio
async def test_slicing_skipped(total: int, index: int, selected: Set[int], *,
                               slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, total=total, index=index)

        scenarios = [
            make_vscenario(is_skipped=True),
            make_vscenario(is_skipped=True)
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[i] for i in selected]


@pytest.mark.parametrize(("total", "index"), [
    (None, None),
    (1, 0),
])
@pytest.mark.asyncio
async def test_arg_validation(total: Union[int, None], index: Union[int, None], *,
                              slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.parametrize(("total", "index"), [
    (1, None),  # slicer_index is None
    (None, 1),  # slicer_total is None
    (0, 1),  # slicer_total <= 0
    (1, -1),  # slicer_index < 0
    (1, 1),  # slicer_index > slicer_total
])
@pytest.mark.asyncio
async def test_arg_validation_error(total: Union[int, None], index: Union[int, None], *,
                                    slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))

    with when, raises(Exception) as exc_info:
        await dispatcher.fire(event)

    with then:
        assert exc_info.type is AssertionError
