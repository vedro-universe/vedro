from unittest.mock import Mock, call

import pytest
from baby_steps import given, then, when

from vedro import Config
from vedro.core import Dispatcher
from vedro.plugins.orderer import (
    OrdererPlugin,
    RandomOrderer,
    ReversedOrderer,
    StableScenarioOrderer,
)

from ._utils import (
    dispatcher,
    fire_arg_parse_event,
    fire_config_loaded_event,
    make_arg_parsed_event,
    orderer,
)

__all__ = ("orderer", "dispatcher")  # fixtures


@pytest.mark.asyncio
async def test_stable_orderer(*, orderer: OrdererPlugin, dispatcher: Dispatcher):
    with given:
        config_ = Mock(Config)

        await fire_config_loaded_event(dispatcher, config_)
        await fire_arg_parse_event(dispatcher)

        event = make_arg_parsed_event(order_stable=True)

    with when:
        await dispatcher.fire(event)

    with then:
        assert config_.mock_calls == [
            call.Registry.ScenarioOrderer.register(StableScenarioOrderer, orderer)
        ]


@pytest.mark.asyncio
async def test_reversed_orderer(*, orderer: OrdererPlugin, dispatcher: Dispatcher):
    with given:
        config_ = Mock(Config)

        await fire_config_loaded_event(dispatcher, config_)
        await fire_arg_parse_event(dispatcher)

        event = make_arg_parsed_event(order_reversed=True)

    with when:
        await dispatcher.fire(event)

    with then:
        assert config_.mock_calls == [
            call.Registry.ScenarioOrderer.register(ReversedOrderer, orderer)
        ]


@pytest.mark.asyncio
async def test_random_orderer(*, orderer: OrdererPlugin, dispatcher: Dispatcher):
    with given:
        config_ = Mock(Config)

        await fire_config_loaded_event(dispatcher, config_)
        await fire_arg_parse_event(dispatcher)

        event = make_arg_parsed_event(order_random=True)

    with when:
        await dispatcher.fire(event)

    with then:
        assert config_.mock_calls == [
            call.Registry.ScenarioOrderer.register(RandomOrderer, orderer)
        ]
