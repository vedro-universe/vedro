import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from argparse import Namespace
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest
from baby_steps import given, then, when

from vedro._core import Dispatcher, Lifecycle, Plugin, Report, Runner, ScenarioDiscoverer
from vedro.events import ArgParsedEvent, CleanupEvent, StartupEvent


@pytest.fixture()
def dispatcher_():
    return AsyncMock(Dispatcher)


@pytest.fixture()
def discoverer_():
    discoverer = Mock(ScenarioDiscoverer)
    return discoverer


@pytest.fixture()
def runner_(dispatcher_: Dispatcher):
    report = Report()
    return Mock(Runner(dispatcher_), run=AsyncMock(return_value=report))


def test_lifecycle_register_plugins(*, dispatcher_: Dispatcher,
                                    discoverer_: ScenarioDiscoverer, runner_: Runner):
    with given:
        lifecycle = Lifecycle(dispatcher_, discoverer_, runner_)
        plugin1 = Mock(Plugin)
        plugin2 = Mock(Plugin)

    with when:
        res = lifecycle.register_plugins([plugin1, plugin2])

    with then:
        assert res is None
        assert dispatcher_.mock_calls == [
            call.register(plugin1),
            call.register(plugin2),
        ]


@pytest.mark.asyncio
async def test_lifecycle_register_start(*, dispatcher_: Dispatcher,
                                        discoverer_: ScenarioDiscoverer, runner_: Runner):
    with given:
        scenarios = []
        discoverer_.discover = AsyncMock(return_value=scenarios)

        lifecycle = Lifecycle(dispatcher_, discoverer_, runner_)
        namespace = Namespace()

    with when, patch("argparse.ArgumentParser.parse_args", return_value=namespace):
        report = await lifecycle.start()

    with then:
        assert isinstance(report, Report)
        assert discoverer_.mock_calls == [
            call.discover(Path("scenarios"))
        ]
        assert runner_.mock_calls == [
            call.run(scenarios),
        ]
        assert dispatcher_.mock_calls[1:] == [
            call.fire(ArgParsedEvent(namespace)),
            call.fire(StartupEvent(scenarios)),
            call.fire(CleanupEvent(report)),
        ]


def test_lifecycle_repr(*, dispatcher_: Dispatcher,
                        discoverer_: ScenarioDiscoverer, runner_: Runner):
    with when:
        lifecycle = Lifecycle(dispatcher_, discoverer_, runner_)

    with then:
        assert repr(lifecycle) == f"Lifecycle({dispatcher_!r}, {discoverer_!r}, {runner_!r})"
