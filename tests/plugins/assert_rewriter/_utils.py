import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pytest

from vedro.core import Config, ConfigType, Dispatcher, Factory, ModuleFileLoader, ModuleLoader
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.assert_rewriter import AssertRewriter, AssertRewriterPlugin

__all__ = ("tmp_scn_dir", "dispatcher", "assert_rewriter_plugin", "make_config",
           "fire_config_loaded_event", "fire_arg_parsed_event",)


@pytest.fixture()
def tmp_scn_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        scn_dir = tmp_path / "scenarios/"
        scn_dir.mkdir(exist_ok=True)
        yield scn_dir.relative_to(tmp_path)
    finally:
        os.chdir(cwd)


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def assert_rewriter_plugin(dispatcher: Dispatcher) -> AssertRewriterPlugin:
    plugin = AssertRewriterPlugin(AssertRewriter)
    plugin.subscribe(dispatcher)
    return plugin


def make_config() -> ConfigType:
    class TestConfig(Config):
        class Registry(Config.Registry):
            ModuleLoader = Factory[ModuleLoader](ModuleFileLoader)

    return TestConfig


async def fire_config_loaded_event(dispatcher: Dispatcher, config: ConfigType) -> None:
    config_loaded_event = ConfigLoadedEvent(Path(), config)
    await dispatcher.fire(config_loaded_event)


async def fire_arg_parsed_event(
        dispatcher: Dispatcher, *,
        legacy_assertions: bool = AssertRewriter.legacy_assertions
        ) -> None:
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(legacy_assertions=legacy_assertions))
    await dispatcher.fire(arg_parsed_event)
