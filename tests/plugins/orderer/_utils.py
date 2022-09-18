from argparse import Namespace
from pathlib import Path

import pytest

from vedro.core import ArgumentParser, ConfigType, Dispatcher
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.orderer import Orderer, OrdererPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def orderer(dispatcher: Dispatcher) -> OrdererPlugin:
    orderer = OrdererPlugin(Orderer)
    orderer.subscribe(dispatcher)
    return orderer


async def fire_config_loaded_event(dispatcher: Dispatcher, config: ConfigType) -> None:
    config_loaded_event = ConfigLoadedEvent(Path(), config)
    await dispatcher.fire(config_loaded_event)


async def fire_arg_parse_event(dispatcher: Dispatcher) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)


def make_arg_parsed_event(*, order_stable: bool = False,
                          order_reversed: bool = False,
                          order_random: bool = False) -> ArgParsedEvent:
    return ArgParsedEvent(
        Namespace(order_stable=order_stable,
                  order_reversed=order_reversed,
                  order_random=order_random))
