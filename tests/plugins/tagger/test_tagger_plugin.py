from argparse import ArgumentParser

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.events import ArgParseEvent
from vedro.plugins.tagger import Tagger, TaggerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.mark.asyncio
async def test_tagger_plugin(*, dispatcher: Dispatcher):
    with given:
        tagger = TaggerPlugin(Tagger)
        tagger.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
