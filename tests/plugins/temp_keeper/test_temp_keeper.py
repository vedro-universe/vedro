import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.temp_keeper import TempFileManager

from ._utils import dispatcher, fire_arg_parsed_event, temp_file_manager, temp_keeper

__all__ = ("dispatcher", "temp_file_manager", "temp_keeper",)  # fixtures


@pytest.mark.usefixtures(temp_keeper.__name__)
async def test_temp_keeper_plugin(*, dispatcher: Dispatcher,
                                  temp_file_manager: TempFileManager):
    with given:
        tmp_dir = temp_file_manager.create_tmp_dir()
        tmp_file = temp_file_manager.create_tmp_file()

    with when:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert tmp_dir.exists() is False
        assert tmp_file.exists() is False

        tmp_root = temp_file_manager.get_tmp_root()
        assert tmp_root.exists() is False


@pytest.mark.usefixtures(temp_keeper.__name__)
async def test_temp_keeper_plugin_no_tmp_root(*, dispatcher: Dispatcher,
                                              temp_file_manager: TempFileManager):
    with when:
        await fire_arg_parsed_event(dispatcher)

    with then:
        tmp_root = temp_file_manager.get_tmp_root()
        assert tmp_root.exists() is False
