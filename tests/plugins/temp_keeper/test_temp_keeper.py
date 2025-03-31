from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.temp_keeper import TempFileManager, TempKeeper, TempKeeperPlugin

from ._utils import (
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    temp_file_manager,
    temp_keeper,
)

__all__ = ("dispatcher", "temp_file_manager", "temp_keeper",)  # fixtures


@pytest.mark.usefixtures(temp_keeper.__name__)
async def test_temp_keeper_plugin(*, dispatcher: Dispatcher, tmp_path: Path,
                                  temp_file_manager: TempFileManager):
    with given:
        tmp_dir = temp_file_manager.create_tmp_dir()
        tmp_file = temp_file_manager.create_tmp_file()

    with when:
        await fire_arg_parsed_event(dispatcher, tmp_dir=tmp_path)

    with then:
        assert tmp_dir.exists() is False
        assert tmp_file.exists() is False

        tmp_root = temp_file_manager.get_tmp_root()
        assert tmp_root.exists() is False


@pytest.mark.usefixtures(temp_keeper.__name__)
async def test_temp_keeper_plugin_no_tmp_root(*, dispatcher: Dispatcher, tmp_path: Path,
                                              temp_file_manager: TempFileManager):
    with when:
        await fire_arg_parsed_event(dispatcher, tmp_dir=tmp_path)

    with then:
        tmp_root = temp_file_manager.get_tmp_root()
        assert tmp_root.exists() is False


async def test_rel_tmp_dir_default(*, dispatcher: Dispatcher, tmp_path: Path,
                                   temp_file_manager: TempFileManager):
    with given:
        class TempKeeperConfig(TempKeeper):
            pass

        plugin = TempKeeperPlugin(TempKeeperConfig, tmp_file_manager=temp_file_manager)
        plugin.subscribe(dispatcher)

    with when:
        await fire_config_loaded_event(dispatcher, project_directory=tmp_path)

    with then:
        assert temp_file_manager.get_project_dir() == tmp_path
        assert temp_file_manager.get_tmp_root() == tmp_path / ".vedro/tmp/"


async def test_abs_tmp_dir_custom(*, dispatcher: Dispatcher, tmp_path: Path,
                                  temp_file_manager: TempFileManager):
    with given:
        class TempKeeperConfig(TempKeeper):
            tmp_dir = tmp_path / ".tmp/"

        plugin = TempKeeperPlugin(TempKeeperConfig, tmp_file_manager=temp_file_manager)
        plugin.subscribe(dispatcher)

    with when:
        await fire_config_loaded_event(dispatcher, project_directory=tmp_path)

        await fire_arg_parsed_event(dispatcher, tmp_dir=TempKeeperConfig.tmp_dir)

    with then:
        assert temp_file_manager.get_project_dir() == tmp_path
        assert temp_file_manager.get_tmp_root() == tmp_path / ".tmp/"
