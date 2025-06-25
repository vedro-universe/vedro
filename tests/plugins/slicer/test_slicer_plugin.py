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
        namespace = Namespace(slicer_total=total, slicer_index=index, slice=None)
        event = ArgParsedEvent(namespace)

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
        namespace = Namespace(slicer_total=total, slicer_index=index, slice=None)
        event = ArgParsedEvent(namespace)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == error


@pytest.mark.parametrize(("slice_val", "selected"), [
    ("1/1", {0, 1, 2, 3}),
    ("1/2", {0, 3}),
    ("2/2", {1, 2}),
    ("1/3", {0}),
    ("2/3", {2}),
    ("3/3", {1, 3}),
])
async def test_slicing_with_slice_arg(slice_val: str, selected: Set[int], *,
                                      slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, slice=slice_val)

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


@pytest.mark.parametrize(("slice_val", "selected"), [
    ("1/2", {0, 3, 4}),
    ("2/2", {1, 2, 5}),
])
async def test_slicing_skipped_with_slice_arg(slice_val: str, selected: Set[int], *,
                                              slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        await fire_arg_parsed_event(dispatcher, slice=slice_val)

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


@pytest.mark.parametrize(("slice_val", "error"), [
    ("0/1", "`<index>` in --slice must be greater than or equal to 1 and "
            "less than or equal to `<total>`"),
    ("2/1", "`<index>` in --slice must be greater than or equal to 1 and "
            "less than or equal to `<total>`"),
    ("1/0", "`<total>` in --slice must be greater than or equal to 1"),
    ("a/1", "Invalid --slice format: 'a/1'. Expected '<index>/<total>' with positive integers"),
    ("1/a", "Invalid --slice format: '1/a'. Expected '<index>/<total>' with positive integers"),
    ("1-1", "Invalid --slice format: '1-1'. Expected '<index>/<total>' with positive integers"),
    ("/1", "Invalid --slice format: '/1'. Expected '<index>/<total>' with positive integers"),
    ("1/", "Invalid --slice format: '1/'. Expected '<index>/<total>' with positive integers"),
])
async def test_slice_arg_validation_error(slice_val: str, error: str,
                                          *, slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        namespace = Namespace(slicer_total=None, slicer_index=None, slice=slice_val)
        event = ArgParsedEvent(namespace)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == error


@pytest.mark.parametrize(("slice_val", "total", "index", "error"), [
    ("1/2", 1, None,
     "`--slice` cannot be used together with `--slicer-total` or `--slicer-index`"),

    ("1/2", None, 0,
     "`--slice` cannot be used together with `--slicer-total` or `--slicer-index`"),

    ("1/2", 1, 0,
     "`--slice` cannot be used together with `--slicer-total` or `--slicer-index`"),
])
async def test_slice_mutual_exclusivity(slice_val: str, total: Union[int, None],
                                        index: Union[int, None], error: str,
                                        *, slicer: SlicerPlugin, dispatcher: Dispatcher):
    with given:
        namespace = Namespace(slicer_total=total, slicer_index=index, slice=slice_val)
        event = ArgParsedEvent(namespace)

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == error
