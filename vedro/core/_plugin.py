from typing import Type

from ._config_loader import Section
from ._dispatcher import Dispatcher, Subscriber

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    def __init__(self, config: Type["PluginConfig"]) -> None:
        assert issubclass(config, PluginConfig)
        self._config = config

    @property
    def config(self) -> Type["PluginConfig"]:
        return self._config

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._config.__name__})"


class PluginConfig(Section):
    plugin: Type[Plugin] = Plugin
    enabled: bool = True
