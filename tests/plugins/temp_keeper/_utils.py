from argparse import ArgumentParser, Namespace
from pathlib import Path

import pytest

from vedro.core import Config, Dispatcher
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent
from vedro.plugins.temp_keeper import TempFileManager, TempKeeper, TempKeeperPlugin

__all__ = ("dispatcher", "temp_file_manager", "temp_keeper", "fire_arg_parsed_event",
           "fire_config_loaded_event",)


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def temp_file_manager(tmp_path: Path) -> TempFileManager:
    return TempFileManager(project_dir=tmp_path)


@pytest.fixture()
def temp_keeper(dispatcher: Dispatcher, temp_file_manager: TempFileManager) -> TempKeeperPlugin:
    plugin = TempKeeperPlugin(TempKeeper, tmp_file_manager=temp_file_manager)
    plugin.subscribe(dispatcher)
    return plugin


async def fire_config_loaded_event(dispatcher: Dispatcher, project_directory: Path):
    class CustomConfig(Config):
        project_dir = project_directory

    config_loaded_event = ConfigLoadedEvent(Path(), CustomConfig)
    await dispatcher.fire(config_loaded_event)


async def fire_arg_parsed_event(dispatcher: Dispatcher, *,
                                tmp_dir: Path = TempKeeper.tmp_dir,
                                no_tmp_cleanup: bool = not TempKeeper.cleanup_tmp):
    arg_parse_event = ArgParseEvent(ArgumentParser())
    await dispatcher.fire(arg_parse_event)

    arg_parsed_event = ArgParsedEvent(Namespace(tmp_dir=tmp_dir, no_tmp_cleanup=no_tmp_cleanup))
    await dispatcher.fire(arg_parsed_event)
