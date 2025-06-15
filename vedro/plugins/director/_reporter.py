from abc import abstractmethod
from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig

__all__ = ("Reporter",)


class Reporter(Plugin):
    """
    Defines the base interface for all scenario reporters.

    Reporters are responsible for outputting scenario results and can
    respond to various events during the execution lifecycle to provide
    customized reporting behavior.
    """

    def __init__(self, config: Type[PluginConfig]) -> None:
        """
        Initialize the Reporter with the given configuration.

        :param config: The configuration used to initialize the reporter.
        """
        super().__init__(config)
        self._dispatcher: Union[Dispatcher, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe the reporter to the event dispatcher.

        :param dispatcher: The dispatcher to bind event handlers to.
        """
        self._dispatcher = dispatcher

    @abstractmethod
    def on_chosen(self) -> None:
        """
        Triggered when the reporter is selected by the Director.

        :raises NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()
