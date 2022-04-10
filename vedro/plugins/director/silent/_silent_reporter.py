from typing import Optional

from vedro.core import Dispatcher, PluginConfig

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter

__all__ = ("SilentReporter", "SilentReporterPlugin",)


class SilentReporterPlugin(Reporter):
    def __init__(self, config: Optional["SilentReporter"] = None) -> None:
        super().__init__()

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher.listen(DirectorInitEvent,
                                             lambda e: e.director.register("silent", self))

    def on_chosen(self) -> None:
        pass


class SilentReporter(PluginConfig):
    plugin = SilentReporterPlugin
