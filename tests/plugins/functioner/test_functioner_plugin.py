from pathlib import Path
from unittest.mock import Mock

import pytest
from baby_steps import given, then, when

from vedro.core import Config, Dispatcher
from vedro.events import ConfigLoadedEvent
from vedro.plugins.functioner import Functioner, FunctionerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def plugin(dispatcher: Dispatcher) -> FunctionerPlugin:
    plugin = FunctionerPlugin(Functioner)
    plugin.subscribe(dispatcher)
    return plugin


@pytest.mark.usefixtures(plugin.__name__)
async def test_register_scenario_provider(dispatcher: Dispatcher):
    with given:
        class TestConfig(Config):
            class Registry(Config.Registry):
                ScenarioCollector = Mock()

        config_loaded_event = ConfigLoadedEvent(Path(), TestConfig)

    with when:
        await dispatcher.fire(config_loaded_event)

    with then:
        mock = TestConfig.Registry.ScenarioCollector

        assert len(mock.mock_calls) == 2
        assert mock.assert_called_once_with() is None
        assert mock().register_provider.assert_called_once() is None
