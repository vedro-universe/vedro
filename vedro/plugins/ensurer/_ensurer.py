from typing import Type

from vedro.core import Dispatcher, Plugin, PluginConfig

__all__ = ("Ensurer", "EnsurerPlugin",)


class EnsurerPlugin(Plugin):
    def __init__(self, config: Type["Ensurer"]) -> None:
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        pass


class Ensurer(PluginConfig):
    plugin = EnsurerPlugin
    description = "<description>"
