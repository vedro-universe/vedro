from ..._core import Dispatcher
from ..plugin import Plugin

__all__ = ("Reporter",)


class Reporter(Plugin):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
