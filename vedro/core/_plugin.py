from typing import Optional, Type, Union

from ._config_loader import Section
from ._dispatcher import Dispatcher, Subscriber

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    def __init__(self, config: Optional[Type["PluginConfig"]] = None) -> None:
        self._config = config
        self._dispatcher: Union[Dispatcher, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher


class PluginConfig(Section):
    plugin: Type[Plugin] = Plugin
    enabled: bool = True
