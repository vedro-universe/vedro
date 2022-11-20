import sys
from typing import Callable, Type

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import CleanupEvent

__all__ = ("Terminator", "TerminatorPlugin",)


class TerminatorPlugin(Plugin):
    def __init__(self, config: Type["Terminator"], *, exit_fn: Callable[[int], None] = sys.exit):
        super().__init__(config)
        self._exit_fn = exit_fn

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(CleanupEvent, self.on_cleanup, priority=sys.maxsize)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if event.report.interrupted:
            exc = event.report.interrupted.value
            if isinstance(exc, SystemExit) and (exc.code is not None):
                self._exit_fn(exc.code)
            else:
                self._exit_fn(130)
        elif event.report.failed > 0 or event.report.passed == 0:
            self._exit_fn(1)
        else:
            self._exit_fn(0)


class Terminator(PluginConfig):
    plugin = TerminatorPlugin
