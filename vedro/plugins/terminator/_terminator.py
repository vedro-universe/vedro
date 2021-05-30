import sys

from ..._core import Dispatcher
from ..._events import CleanupEvent
from ..plugin import Plugin

__all__ = ("Terminator",)


class Terminator(Plugin):
    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(CleanupEvent, self.on_cleanup, priority=-1)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.failed > 0 or event.report.passed == 0:
            sys.exit(1)
        else:
            sys.exit(0)
