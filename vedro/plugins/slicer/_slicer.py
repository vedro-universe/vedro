from typing import Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

from ._slicing_strategy import BaseSlicingStrategy, SkipAdjustedSlicingStrategy

__all__ = ("Slicer", "SlicerPlugin",)

SlicingStrategyType = Type[BaseSlicingStrategy]


@final
class SlicerPlugin(Plugin):
    """
    Plugin to distribute scenarios among multiple workers.

    The `SlicerPlugin` allows for the division of scenarios into slices to be executed
    by different workers, based on a defined slicing strategy. This is useful for parallelizing
    test runs across multiple machines or processes.
    """

    def __init__(self, config: Type["Slicer"]) -> None:
        """
        Initialize the SlicerPlugin with the provided configuration.

        :param config: The Slicer configuration class.
        """
        super().__init__(config)
        self._slicing_strategy = config.slicing_strategy
        self._total: Union[int, None] = None
        self._index: Union[int, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events to handle argument parsing and test startup.

        :param dispatcher: The dispatcher to listen to events.
        """
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Add command-line arguments for scenario slicing.

        :param event: The ArgParseEvent instance used to add arguments.
        """
        group = event.arg_parser.add_argument_group("Slicer")
        group.add_argument("--slicer-total", type=int, help="Set total workers")
        group.add_argument("--slicer-index", type=int, help="Set current worker")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle parsed arguments and validate slicing options.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        :raises ValueError: If slicing arguments are missing or invalid.
        """
        self._total = event.args.slicer_total
        self._index = event.args.slicer_index

        if self._total is not None:
            if self._index is None:
                raise ValueError(
                    "`--slicer-index` must be specified if `--slicer-total` is specified")
            if self._total <= 0:
                raise ValueError(
                    f"`--slicer-total` must be greater than 0, {self._total} given")

        if self._index is not None:
            if self._total is None:
                raise ValueError(
                    "`--slicer-total` must be specified if `--slicer-index` is specified")
            if not (0 <= self._index < self._total):
                raise ValueError(
                    "`--slicer-index` must be greater than 0 and "
                    f"less than `--slicer-total` ({self._total}), {self._index} given"
                )

    async def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event to apply the slicing strategy.

        The plugin uses the specified slicing strategy to determine which scenarios
        should be executed by the current worker.

        :param event: The StartupEvent instance containing the test scheduler.
        """
        if (self._total is None) or (self._index is None):
            return

        slicing_strategy = self._slicing_strategy(self._total, self._index)

        index = 0
        async for scenario in event.scheduler:
            if not slicing_strategy.should_run(scenario, index):
                event.scheduler.ignore(scenario)
            index += 1


class Slicer(PluginConfig):
    """
    Configuration class for the SlicerPlugin.

    Provides settings to configure the scenario slicing strategy for distributing
    scenarios among multiple workers.
    """

    plugin = SlicerPlugin
    description = "Provides a way to distribute scenarios among multiple workers"

    # The slicing strategy used to distribute scenarios
    slicing_strategy: SlicingStrategyType = SkipAdjustedSlicingStrategy
