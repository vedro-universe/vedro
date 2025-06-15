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

__all__ = ("dispatcher", "slicer",)  # fixtures


@pytest.mark.parametrize(("total", "index", "selected"), [
    (None, None, {0, 1, 2, 3}),
    (1, 0, {0, 1, 2, 3}),

    (2, 0, {0, 3}),
    (2, 1, {1, 2}),

    (3, 0, {0}),
    (3, 1, {2}),
    (3, 2, {1, 3}),
])
async def test_slicing(total: int, index: int, selected: Set[int], *,
                       slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, total=total, index=index)

        scenarios = [
            make_vscenario(),                 # 0
            make_vscenario(is_skipped=True),  # 1
            make_vscenario(),                 # 2
            make_vscenario()                  # 3
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[i] for i in selected]


@pytest.mark.parametrize(("total", "index", "selected"), [
    (2, 0, {0, 3, 4}),
    (2, 1, {1, 2, 5}),
])
async def test_slicing_skipped(total: int, index: int, selected: Set[int], *,
                               slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, total=total, index=index)

        scenarios = [
            make_vscenario(),                 # 0
            make_vscenario(is_skipped=True),  # 1
            make_vscenario(),                 # 2
            make_vscenario(is_skipped=True),  # 3
            make_vscenario(),                 # 4
            make_vscenario(),                 # 5
        ]
        scheduler = Scheduler(scenarios)

        startup_event = StartupEvent(scheduler)

    with when:
        await dispatcher.fire(startup_event)

    with then:
        assert list(scheduler.scheduled) == [scenarios[i] for i in selected]


@pytest.mark.parametrize(("total", "index", "selected"), [
    (None, None, {0, 1}),
    (1, 0, {0, 1}),
])
async def test_slicing_all_skipped(total: int, index: int, selected: Set[int], *,
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
async def test_arg_validation(total: Union[int, None], index: Union[int, None], *,
                              slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.parametrize(("total", "index", "error"), [
    (1, None, "`--slicer-index` must be specified if `--slicer-total` is specified"),
    (None, 1, "`--slicer-total` must be specified if `--slicer-index` is specified"),
    (0, 1, "`--slicer-total` must be greater than 0, 0 given"),
    (1, -1,
     "`--slicer-index` must be greater than 0 and less than `--slicer-total` (1), -1 given"),
    (1, 1, "`--slicer-index` must be greater than 0 and less than `--slicer-total` (1), 1 given"),
])
async def test_arg_validation_error(total: Union[int, None], index: Union[int, None], error: str,
                                    *, slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        event = ArgParsedEvent(Namespace(slicer_total=total, slicer_index=index))

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == error
