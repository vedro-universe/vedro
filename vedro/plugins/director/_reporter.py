from abc import abstractmethod
from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig

__all__ = ("Reporter",)


class Reporter(Plugin):
    def __init__(self, config: Type[PluginConfig]) -> None:
        super().__init__(config)
        self._dispatcher: Union[Dispatcher, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher

    @abstractmethod
    def on_chosen(self) -> None:
        raise NotImplementedError()
