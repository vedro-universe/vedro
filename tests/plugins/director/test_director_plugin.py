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


async def test_init_event(*, director: DirectorPlugin, dispatcher: Dispatcher):
    with given:
        callback_ = Mock()
        dispatcher.listen(DirectorInitEvent, callback_)

        event = ConfigLoadedEvent(Path(), Config)

    with when:
        await dispatcher.fire(event)

    with then:
        assert callback_.mock_calls == [call(DirectorInitEvent(director))]


async def test_no_reporters(*, director: DirectorPlugin, dispatcher: Dispatcher):
    with given:
        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))
        event = ArgParseEvent(ArgumentParser())

    with when:
        await dispatcher.fire(event)

    with then:
        "no errors"


async def test_default_reporter(*, dispatcher: Dispatcher):
    with given:
        class _Director(Director):
            default_reporters = ["reporter1"]
        director = DirectorPlugin(_Director)
        director.subscribe(dispatcher)

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


async def test_default_reporters(*, dispatcher: Dispatcher):
    with given:
        class _Director(Director):
            default_reporters = ["reporter1", "reporter2"]
        director = DirectorPlugin(_Director)
        director.subscribe(dispatcher)

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
        assert reporter2_.mock_calls == [call.on_chosen()]


async def test_passed_reporters(*, director: DirectorPlugin, dispatcher: Dispatcher):
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
