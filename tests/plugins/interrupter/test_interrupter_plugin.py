from argparse import ArgumentParser

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro.events import ArgParseEvent
from vedro.plugins.interrupter import Interrupter


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.mark.asyncio
async def test_interrupter_plugin(*, dispatcher: Dispatcher):
    with given:
        interrupter = Interrupter()
        interrupter.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
