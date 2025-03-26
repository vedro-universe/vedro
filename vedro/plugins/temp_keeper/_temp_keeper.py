import shutil
from pathlib import Path
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
        self._tmp_root = config.tmp_dir

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
        Set the project and temporary root directories when configuration is loaded.

        :param event: The `ConfigLoadedEvent` containing the loaded configuration.
        """
        project_dir = event.config.project_dir
        self._tmp_file_manager.set_project_dir(project_dir)
        if not self._tmp_root.is_absolute():
            self._tmp_root = project_dir / self._tmp_root
        self._tmp_file_manager.set_tmp_root(self._tmp_root)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Remove all temporary files and directories after argument parsing is complete.

        If the temporary root directory exists, its entire contents will be deleted recursively.

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

    # Root directory for storing temporary files and directories
    # (!) This directory is deleted at the start of each run.
    tmp_dir: Path = Path(".vedro/tmp/")
