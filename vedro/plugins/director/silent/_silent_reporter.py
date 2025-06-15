from typing import Type, final

from vedro.core import Dispatcher, PluginConfig

from .._director_init_event import DirectorInitEvent
from .._reporter import Reporter

__all__ = ("SilentReporter", "SilentReporterPlugin",)


@final
class SilentReporterPlugin(Reporter):
    """
    Provides a reporter that produces no output during scenario execution.

    This reporter is useful for suppressing all console, allowing scenarios to run
    silently without any printed results or progress information.
    """

    def __init__(self, config: Type["SilentReporter"]) -> None:
        """
        Initialize the SilentReporterPlugin with the given configuration.

        :param config: The configuration used to initialize the reporter.
        """
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to DirectorInitEvent to register as 'silent' reporter.

        :param dispatcher: The event dispatcher.
        """
        super().subscribe(dispatcher)
        dispatcher.listen(DirectorInitEvent, lambda e: e.director.register("silent", self))

    def on_chosen(self) -> None:
        """
        Handle reporter selection. Produces no output.
        """
        pass


class SilentReporter(PluginConfig):
    """
    Configuration for SilentReporterPlugin.

    This reporter does not produce any output during scenario execution.
    It is intended for cases where silent execution is desired.
    """
    plugin = SilentReporterPlugin
    description = "Does not produce any output during scenario execution"
