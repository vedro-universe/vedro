from pathlib import Path

import pytest

from vedro.core import Plugin, PluginConfig
from vedro.core.exp.local_storage import LocalStorage

__all__ = ("plugin", "local_storage",)


@pytest.fixture()
def plugin() -> Plugin:
    class CustomPlugin(Plugin):
        pass

    class CustomPluginConfig(PluginConfig):
        plugin = CustomPlugin

    return CustomPlugin(CustomPluginConfig)


@pytest.fixture()
def local_storage(plugin: Plugin, tmp_path: Path):
    return LocalStorage(plugin, tmp_path)
