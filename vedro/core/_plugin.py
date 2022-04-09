from typing import Type

import cabina

from ._dispatcher import Subscriber

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    pass


class PluginConfig(cabina.Section):
    plugin: Type[Plugin] = Plugin
    enabled: bool = True
