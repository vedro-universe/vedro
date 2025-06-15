from typing import Type, final

from vedro.core import Dispatcher, PluginConfig

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter

__all__ = ("SilentReporter", "SilentReporterPlugin",)


@final
class SilentReporterPlugin(Reporter):
    def __init__(self, config: Type["SilentReporter"]) -> None:
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("silent", self))

    def on_chosen(self) -> None:
        pass


class SilentReporter(PluginConfig):
    plugin = SilentReporterPlugin
    description = "Minimizes output during scenario execution"
