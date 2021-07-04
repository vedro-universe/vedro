from argparse import ArgumentParser, Namespace

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro._core import Dispatcher
from vedro.events import ArgParsedEvent, ArgParseEvent
from vedro.plugins.slicer import Slicer


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.mark.asyncio
async def test_slicer_plugin(*, dispatcher: Dispatcher):
    with given:
        tagger = Slicer()
        tagger.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.parametrize(("slicer_total", "slicer_index"), [
    (None, None),
    (1, 0),
])
@pytest.mark.asyncio
async def test_slicer_plugin_arg_validation(slicer_total, slicer_index, *, dispatcher: Dispatcher):
    with given:
        tagger = Slicer()
        tagger.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(slicer_total=slicer_total, slicer_index=slicer_index))

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.parametrize(("slicer_total", "slicer_index"), [
    (1, None),  # slicer_index is None
    (None, 1),  # slicer_total is None
    (0, 1),  # slicer_total <= 0
    (1, -1),  # slicer_index < 0
    (1, 1),  # slicer_index > slicer_total
])
@pytest.mark.asyncio
async def test_slicer_plugin_arg_validation_error(slicer_total, slicer_index, *,
                                                  dispatcher: Dispatcher):
    with given:
        tagger = Slicer()
        tagger.subscribe(dispatcher)
        event = ArgParsedEvent(Namespace(slicer_total=slicer_total, slicer_index=slicer_index))

    with when, raises(Exception) as exc_info:
        await dispatcher.fire(event)

    with then:
        assert exc_info.type is AssertionError
