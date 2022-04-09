from argparse import ArgumentParser, Namespace
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.events import ArgParseEvent
from vedro.plugins.director import DirectorInitEvent, DirectorPlugin, Reporter


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.mark.asyncio
async def test_director_plugin(*, dispatcher: Dispatcher):
    with given:
        director = DirectorPlugin()
        director.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.asyncio
async def test_director_plugin_init_event(*, dispatcher: Dispatcher):
    with given:
        director = DirectorPlugin()
        director.subscribe(dispatcher)

        mock_ = Mock()
        dispatcher.listen(DirectorInitEvent, mock_)

        event = ArgParseEvent(ArgumentParser())

    with when:
        await dispatcher.fire(event)

    with then:
        assert mock_.mock_calls == [call(DirectorInitEvent(director))]


@pytest.mark.asyncio
async def test_director_plugin_with_reporters_default(*, dispatcher: Dispatcher):
    with given:
        director = DirectorPlugin()
        director.subscribe(dispatcher)

        reporter1_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter1", reporter1_))

        reporter2_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter2", reporter2_))

        event = ArgParseEvent(ArgumentParser())

    with when:
        await dispatcher.fire(event)

    with then:
        assert reporter1_.mock_calls == [call.on_chosen()]
        assert reporter2_.mock_calls == []


@pytest.mark.asyncio
async def test_director_plugin_with_reporters_arg(*, dispatcher: Dispatcher):
    with given:
        director = DirectorPlugin()
        director.subscribe(dispatcher)

        reporter1_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter1", reporter1_))

        reporter2_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter2", reporter2_))

        args = Namespace(reporters=["reporter2", "reporter1"])
        arg_parser = Mock(ArgumentParser, parse_known_args=Mock(return_value=(args, [])))
        event = ArgParseEvent(arg_parser)

    with when:
        await dispatcher.fire(event)

    with then:
        assert reporter1_.mock_calls == [call.on_chosen()]
        assert reporter2_.mock_calls == [call.on_chosen()]
