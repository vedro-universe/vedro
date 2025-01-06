from typing import Sequence, Type

from ._dispatcher import Dispatcher, Subscriber
from .config_loader import Section as ConfigSection
from .config_loader import computed

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    def __init__(self, config: Type["PluginConfig"]) -> None:
        if not issubclass(config, PluginConfig):
            raise TypeError(f"PluginConfig {config} should be subclass of vedro.core.PluginConfig")
        self._config = config

    @property
    def config(self) -> Type["PluginConfig"]:
        return self._config

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._config.__name__})"


class PluginConfig(ConfigSection):
    plugin: Type[Plugin] = Plugin
    description: str = ""
    enabled: bool = True

    @computed
    def depends_on(cls) -> Sequence[Type["PluginConfig"]]:
        return ()
