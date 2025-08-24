from argparse import ArgumentParser, Namespace
from pathlib import Path
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

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


async def test_fires_director_init_event(*, director: DirectorPlugin, dispatcher: Dispatcher):
    with given:
        callback_ = Mock()
        dispatcher.listen(DirectorInitEvent, callback_)

        event = ConfigLoadedEvent(Path(), Config)

    with when:
        await dispatcher.fire(event)

    with then:
        assert callback_.mock_calls == [call(DirectorInitEvent(director))]


async def test_no_reporters_no_defaults(*, director: DirectorPlugin, dispatcher: Dispatcher):
    with given:
        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))
        event = ArgParseEvent(ArgumentParser())

    with when:
        await dispatcher.fire(event)

    with then:
        "no errors"


async def test_chooses_single_default_reporter(*, dispatcher: Dispatcher):
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


async def test_chooses_multiple_default_reporters(*, dispatcher: Dispatcher):
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


async def test_chooses_reporters_from_cli(*, director: DirectorPlugin, dispatcher: Dispatcher):
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


async def test_fails_if_default_reporter_missing(*, dispatcher: Dispatcher):
    with given:
        class _Director(Director):
            default_reporters = ["unknown_reporter"]
        director = DirectorPlugin(_Director)
        director.subscribe(dispatcher)

        reporter_ = Mock(Reporter)
        dispatcher.listen(DirectorInitEvent,
                          lambda e: e.director.register("reporter", reporter_))

        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))
        event = ArgParseEvent(ArgumentParser())

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == "Unknown reporter specified: 'unknown_reporter'."

        assert reporter_.mock_calls == []


async def test_fails_if_multiple_default_reporters_missing(*, dispatcher: Dispatcher):
    with given:
        class _Director(Director):
            default_reporters = ["unknown_reporter1", "unknown_reporter2"]
        director = DirectorPlugin(_Director)
        director.subscribe(dispatcher)

        await dispatcher.fire(ConfigLoadedEvent(Path(), Config))
        event = ArgParseEvent(ArgumentParser())

    with when, raises(BaseException) as exc:
        await dispatcher.fire(event)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "Default reporters are specified, but no reporters have been registered: "
            "'unknown_reporter1', 'unknown_reporter2'."
        )
