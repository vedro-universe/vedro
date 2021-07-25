from typing import Union

from vedro.core import Dispatcher, Plugin
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

__all__ = ("Slicer",)


class Slicer(Plugin):
    def __init__(self) -> None:
        self._total: Union[int, None] = None
        self._index: Union[int, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--slicer-total", type=int, help="Set total workers")
        event.arg_parser.add_argument("--slicer-index", type=int, help="Set current worker")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._total = event.args.slicer_total
        self._index = event.args.slicer_index
        if self._total is not None:
            assert self._index is not None
            assert self._total > 0
        if self._index is not None:
            assert self._total is not None
            assert 0 <= self._index < self._total

    def on_startup(self, event: StartupEvent) -> None:
        if (self._total is None) or (self._index is None):
            return
        index = 0
        for scenario in event.scenarios:
            if scenario.is_skipped():
                continue
            if index % self._total != self._index:
                scenario.skip()
            index += 1
