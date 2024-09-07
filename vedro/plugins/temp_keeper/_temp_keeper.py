import shutil
from typing import Type, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

from ._temp_file_manager import TempFileManager

__all__ = ("TempKeeper", "TempKeeperPlugin", "create_tmp_dir", "create_tmp_file",)


_tmp_file_manager = TempFileManager()
create_tmp_dir = _tmp_file_manager.create_tmp_dir
create_tmp_file = _tmp_file_manager.create_tmp_file


@final
class TempKeeperPlugin(Plugin):
    """
    Plugin that integrates with the project lifecycle to manage temporary files and directories.

    TempKeeperPlugin listens to events during the project setup and teardown phases to ensure
    that temporary directories and files are properly created and removed.
    """

    def __init__(self, config: Type["TempKeeper"], *,
                 tmp_file_manager: TempFileManager = _tmp_file_manager) -> None:
        """
        Initialize the TempKeeperPlugin with the provided configuration and file manager.

        :param config: The TempKeeper plugin configuration.
        :param tmp_file_manager: A TempFileManager instance used to manage temporary files
            and directories. Defaults to the globally instantiated _tmp_file_manager.
        """
        super().__init__(config)
        self._tmp_file_manager = tmp_file_manager

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to events in the dispatcher.

        Listens to the `ConfigLoadedEvent` to set the project directory and to the
        `ArgParsedEvent` to clean up the temporary files after the arguments are parsed.

        :param dispatcher: The dispatcher to subscribe events from.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the `ConfigLoadedEvent` by setting the project directory in the file manager.

        :param event: The `ConfigLoadedEvent` containing the loaded configuration.
        """
        self._tmp_file_manager.set_project_dir(event.config.project_dir)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the `ArgParsedEvent` by removing the temporary files.

        Deletes the temporary files and directories if they exist in the `.vedro/tmp` directory.

        :param event: The `ArgParsedEvent` containing the parsed arguments.
        """
        tmp_root = self._tmp_file_manager.get_tmp_root()
        if tmp_root.exists():
            shutil.rmtree(tmp_root)


class TempKeeper(PluginConfig):
    """
    Configuration for the TempKeeper plugin.

    This class defines the plugin and its behavior, which manages temporary directories and
    files during the project lifecycle.
    """
    plugin = TempKeeperPlugin
    description = "Manages temporary directories and files"
