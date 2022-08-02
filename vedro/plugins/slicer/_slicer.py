from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

__all__ = ("Slicer", "SlicerPlugin",)


class SlicerPlugin(Plugin):
    def __init__(self, config: Type["Slicer"]) -> None:
        super().__init__(config)
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
            assert self._index is not None
            assert self._total > 0
        if self._index is not None:
            assert self._total is not None
            assert 0 <= self._index < self._total

    async def on_startup(self, event: StartupEvent) -> None:
        if (self._total is None) or (self._index is None):
            return
        index = 0
        skipped_index = 0
        async for scenario in event.scheduler:
            if scenario.is_skipped():
                if (skipped_index % self._total) != (self._total - self._index - 1):
                    event.scheduler.ignore(scenario)
                skipped_index += 1
            else:
                if (index % self._total) != self._index:
                    event.scheduler.ignore(scenario)
                index += 1


class Slicer(PluginConfig):
    plugin = SlicerPlugin
