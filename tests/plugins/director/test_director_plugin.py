from argparse import ArgumentParser, Namespace
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro.core import Config, Dispatcher
from vedro.events import ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.director import Director, DirectorInitEvent, DirectorPlugin, Reporter


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def director(dispatcher: Dispatcher) -> DirectorPlugin:
    director = DirectorPlugin(Director)
    director.subscribe(dispatcher)
    return director


@pytest.mark.asyncio
async def test_director_plugin_init_event(*, director: DirectorPlugin, dispatcher: Dispatcher):
    with given:
        callback_ = Mock()
        dispatcher.listen(DirectorInitEvent, callback_)

        event = ConfigLoadedEvent(Path(), Config)

    with when:
        await dispatcher.fire(event)

    with then:
        assert callback_.mock_calls == [call(DirectorInitEvent(director))]


@pytest.mark.asyncio
async def test_director_plugin_with_reporters_default(*, director: DirectorPlugin,
                                                      dispatcher: Dispatcher):
    with given:
        reporter1_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter1", reporter1_))

        reporter2_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter2", reporter2_))

        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))
        event = ArgParseEvent(ArgumentParser())

    with when:
        await dispatcher.fire(event)

    with then:
        assert reporter1_.mock_calls == [call.on_chosen()]
        assert reporter2_.mock_calls == []


@pytest.mark.asyncio
async def test_director_plugin_with_reporters_arg(*, director: DirectorPlugin,
                                                  dispatcher: Dispatcher):
    with given:
        reporter1_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter1", reporter1_))

        reporter2_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter2", reporter2_))

        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))

        args = Namespace(reporters=["reporter2", "reporter1"])
        arg_parser = Mock(ArgumentParser, parse_known_args=Mock(return_value=(args, [])))
        event = ArgParseEvent(arg_parser)

    with when:
        await dispatcher.fire(event)

    with then:
        assert reporter1_.mock_calls == [call.on_chosen()]
        assert reporter2_.mock_calls == [call.on_chosen()]
