import shutil
from pathlib import Path
from typing import Type, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

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
        self._tmp_dir = Path(config.tmp_dir)
        self._cleanup_tmp = config.cleanup_tmp

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to events in the dispatcher.

        :param dispatcher: The dispatcher to subscribe events from.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the ConfigLoadedEvent to set the project directory in the TempFileManager.

        :param event: The configuration loaded event containing the project directory.
        """
        project_dir = event.config.project_dir
        self._tmp_file_manager.set_project_dir(project_dir)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the ArgParseEvent to add CLI arguments for temp directory and cleanup options.

        :param event: The argument parser event to which CLI arguments will be added.
        """
        group = event.arg_parser.add_argument_group("TempKeeper")
        group.add_argument("--tmp-dir", type=Path, default=self._tmp_dir,
                           help="Temporary directory for storing files")
        group.add_argument("--no-tmp-cleanup", action="store_true", default=not self._cleanup_tmp,
                           help="Do not clean up temporary directory before run")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the ArgParsedEvent to apply CLI arguments and clean up the temporary directory.

        :param event: The parsed CLI arguments event.
        """
        self._tmp_dir = event.args.tmp_dir
        if not self._tmp_dir.is_absolute():
            project_dir = self._tmp_file_manager.get_project_dir()
            self._tmp_dir = project_dir / self._tmp_dir
        self._tmp_file_manager.set_tmp_root(self._tmp_dir)

        # CLI flag is `no_tmp_cleanup`, so negate it
        self._cleanup_tmp = not event.args.no_tmp_cleanup
        if self._cleanup_tmp and self._tmp_dir.exists():
            shutil.rmtree(self._tmp_dir)


class TempKeeper(PluginConfig):
    """
    Configuration for the TempKeeper plugin.

    This class defines the plugin and its behavior, which manages temporary directories and
    files during the project lifecycle.
    """
    plugin = TempKeeperPlugin
    description = "Manages temporary directories and files"

    # Root directory for storing temporary files and directories.
    # (!) This directory is deleted at the start of each run.
    tmp_dir: Path = Path(".vedro/tmp/")

    # Whether to clean up the temporary directory at the start of each run.
    # Can be overridden via CLI using `--no-tmp-cleanup`.
    cleanup_tmp: bool = True
