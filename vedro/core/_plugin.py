from typing import Type

from ._config_loader import Section
from ._dispatcher import Subscriber

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    pass


class PluginConfig(Section):
    plugin: Type[Plugin] = Plugin
    enabled: bool = True
