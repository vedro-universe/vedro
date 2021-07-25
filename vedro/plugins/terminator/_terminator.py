import sys
from typing import Callable

from vedro.core import Dispatcher, Plugin
from vedro.events import CleanupEvent

__all__ = ("Terminator",)


class Terminator(Plugin):
    def __init__(self, exit_fn: Callable[[int], None] = sys.exit):
        super().__init__()
        self._exit_fn = exit_fn

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(CleanupEvent, self.on_cleanup, priority=sys.maxsize)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed > 0 or event.report.passed == 0:
            self._exit_fn(1)
        else:
            self._exit_fn(0)
