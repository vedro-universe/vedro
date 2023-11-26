import shutil
import tempfile
from os import getcwd
from pathlib import Path
from typing import Optional, Type, Union

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

__all__ = ("TempKeeper", "TempKeeperPlugin", "created_tmp_dir", "created_tmp_file",)


def created_tmp_dir(*, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
    """
    Create a temporary directory within a specified root directory.

    The directory is created in the '.vedro/tmp' directory within the current working directory.
    It has a unique name, which can be customized with an optional suffix and prefix.

    :param suffix: An optional suffix to append to the temporary directory's name.
    :param prefix: An optional prefix to prepend to the temporary directory's name.
    :return: A Path object representing the path to the created temporary directory.
    """
    tmp_root = _get_tmp_root()
    tmp_root.mkdir(parents=True, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(dir=str(tmp_root), suffix=suffix, prefix=prefix)
    return Path(tmp_dir)


def created_tmp_file(*, suffix: Optional[str] = None, prefix: Optional[str] = None) -> Path:
    """
    Create a temporary file within a specified root directory.

    The file is created in the '.vedro/tmp' directory within the current working directory.
    It has a unique name, which can be customized with an optional suffix and prefix.

    :param suffix: An optional suffix to append to the temporary file's name.
    :param prefix: An optional prefix to prepend to the temporary file's name.
    :return: A Path object representing the path to the created temporary file.
    """
    tmp_root = _get_tmp_root()
    tmp_root.mkdir(parents=True, exist_ok=True)
    tmp_file = tempfile.NamedTemporaryFile(dir=str(tmp_root), suffix=suffix, prefix=prefix,
                                           delete=False)
    return Path(tmp_file.name)


def _get_tmp_root() -> Path:
    return Path(getcwd()) / ".vedro" / "tmp/"


class TempKeeperPlugin(Plugin):
    def __init__(self, config: Type["TempKeeper"]) -> None:
        super().__init__(config)
        self._global_config: Union[ConfigType, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config = event.config

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        tmp_root = _get_tmp_root()
        if tmp_root.exists():
            shutil.rmtree(tmp_root, ignore_errors=True)


class TempKeeper(PluginConfig):
    plugin = TempKeeperPlugin
    description = "Manages temporary directories and files"
