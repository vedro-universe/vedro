from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

from ._slicing_strategy import BaseSlicingStrategy, SkipAdjustedSlicingStrategy

__all__ = ("Slicer", "SlicerPlugin",)

SlicingStrategyType = Type[BaseSlicingStrategy]


class SlicerPlugin(Plugin):
    def __init__(self, config: Type["Slicer"], *,
                 slicing_strategy: SlicingStrategyType = SkipAdjustedSlicingStrategy) -> None:
        super().__init__(config)
        self._slicing_strategy = slicing_strategy
        self._total: Union[int, None] = None
        self._index: Union[int, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        group = event.arg_parser.add_argument_group("Slicer")
        group.add_argument("--slicer-total", type=int, help="Set total workers")
        group.add_argument("--slicer-index", type=int, help="Set current worker")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
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
        if (self._total is None) or (self._index is None):
            return

        slicing_strategy = self._slicing_strategy(self._total, self._index)

        index = 0
        async for scenario in event.scheduler:
            if not slicing_strategy.should_run(scenario, index):
                event.scheduler.ignore(scenario)
            index += 1


class Slicer(PluginConfig):
    plugin = SlicerPlugin
    description = "Provides a way to distribute scenarios among multiple workers"

    slicing_strategy: SlicingStrategyType = SkipAdjustedSlicingStrategy
