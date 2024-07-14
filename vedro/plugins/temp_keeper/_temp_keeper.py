import shutil
from typing import Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

from ._temp_file_manager import TempFileManager

__all__ = ("TempKeeper", "TempKeeperPlugin", "create_tmp_dir", "create_tmp_file",)


_tmp_file_manager = TempFileManager()
create_tmp_dir = _tmp_file_manager.create_tmp_dir
create_tmp_file = _tmp_file_manager.create_tmp_file


class TempKeeperPlugin(Plugin):
    def __init__(self, config: Type["TempKeeper"], *,
                 tmp_file_manager: TempFileManager = _tmp_file_manager) -> None:
        super().__init__(config)
        self._tmp_file_manager = tmp_file_manager

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._tmp_file_manager.set_project_dir(event.config.project_dir)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        tmp_root = self._tmp_file_manager.get_tmp_root()
        if tmp_root.exists():
            shutil.rmtree(tmp_root)


class TempKeeper(PluginConfig):
    plugin = TempKeeperPlugin
    description = "Manages temporary directories and files"
