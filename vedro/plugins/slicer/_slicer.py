import re
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
        self._slice_raw: Union[str, None] = None

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
        group.add_argument("--slicer-total", type=int, help="Total number of workers")
        group.add_argument("--slicer-index", type=int,
                           help="Index of the current worker (zero based)")
        group.add_argument("--slice", dest="slice", metavar="N/M",
                           help="Specify slice as <index>/<total> (index starts at 1). "
                                "Mutually exclusive with --slicer-total and --slicer-index")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle parsed arguments and validate slicing options.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        :raises ValueError: If slicing arguments are missing or invalid.
        """
        self._slice_raw = event.args.slice
        self._total = event.args.slicer_total
        self._index = event.args.slicer_index

        # Mutually exclusive validation
        if self._slice_raw is not None and (self._total is not None or self._index is not None):
            raise ValueError(
                "`--slice` cannot be used together with `--slicer-total` or `--slicer-index`")

        # Handle --slice
        if self._slice_raw is not None:
            self._total, self._index = self._parse_slice(self._slice_raw)
            return

        # Handle legacy pair --slicer-total / --slicer-index
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

    def _parse_slice(self, raw: str) -> tuple[int, int]:
        """
        Parse and validate the slice string in the format "<index>/<total>".

        Converts the 1-based index to a 0-based index internally. Ensures both values
        are valid positive integers and within expected ranges.

        :param raw: The slice string input in the format "<index>/<total>".
        :return: A tuple containing total workers and zero-based index of current worker.
        :raises ValueError: If the input format is invalid or values are out of range.
        """
        pattern = re.compile(r"^(?P<index>\d+)(?:\s)*/(?:\s)*(?P<total>\d+)$")

        match = pattern.match(raw.strip())
        if not match:
            raise ValueError(f"Invalid --slice format: '{raw}'. "
                             "Expected '<index>/<total>' with positive integers")
        index = int(match.group("index"))
        total = int(match.group("total"))

        if total < 1:
            raise ValueError("`<total>` in --slice must be greater than or equal to 1")
        if not (1 <= index <= total):
            raise ValueError("`<index>` in --slice must be greater than or equal to 1 and "
                             "less than or equal to `<total>`")

        # Convert index to zero based for internal use
        return total, index - 1

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
