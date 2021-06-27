from argparse import ArgumentParser, Namespace
from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher
from vedro.events import ArgParseEvent
from vedro.plugins.director import Director, Reporter


@pytest.fixture()
def dispatcher():
    return Dispatcher()


@pytest.mark.asyncio
async def test_director_plugin(*, dispatcher: Dispatcher):
    with given:
        director = Director()
        director.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None


@pytest.mark.asyncio
async def test_director_plugin_with_default_reporter(*, dispatcher: Dispatcher):
    with given:
        reporter_ = Mock(Reporter)
        reporter_.name = "reporter"
        director = Director([reporter_])
        director.subscribe(dispatcher)
        event = ArgParseEvent(ArgumentParser())

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert reporter_.mock_calls == [call.subscribe(dispatcher)]


@pytest.mark.asyncio
async def test_director_plugin_with_reporter(*, dispatcher: Dispatcher):
    with given:
        reporter1_, reporter2_ = Mock(Reporter), Mock(Reporter)
        reporter1_.name = "reporter1"
        reporter2_.name = "reporter2"
        director = Director([reporter1_, reporter2_])
        director.subscribe(dispatcher)

        args = Namespace(reporters=[reporter2_.name])
        arg_parser = Mock(ArgumentParser, parse_known_args=Mock(return_value=(args, [])))
        event = ArgParseEvent(arg_parser)

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert reporter1_.mock_calls == []
        assert reporter2_.mock_calls == [call.subscribe(dispatcher)]


@pytest.mark.asyncio
async def test_director_plugin_with_reporters(*, dispatcher: Dispatcher):
    with given:
        reporter1_, reporter2_ = Mock(Reporter), Mock(Reporter)
        reporter1_.name = "reporter1"
        reporter2_.name = "reporter2"
        director = Director([reporter1_, reporter2_])
        director.subscribe(dispatcher)

        args = Namespace(reporters=[reporter2_.name, reporter1_.name])
        arg_parser = Mock(ArgumentParser, parse_known_args=Mock(return_value=(args, [])))
        event = ArgParseEvent(arg_parser)

    with when:
        res = await dispatcher.fire(event)

    with then:
        assert res is None
        assert reporter1_.mock_calls == [call.subscribe(dispatcher)]
        assert reporter2_.mock_calls == [call.subscribe(dispatcher)]
