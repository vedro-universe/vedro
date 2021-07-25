from typing import List, Optional, Union

from vedro.core import Dispatcher, Plugin
from vedro.events import ArgParseEvent

from ._reporter import Reporter

__all__ = ("Director",)


class Director(Plugin):
    def __init__(self, reporters: Optional[List[Reporter]] = None) -> None:
        self._reporters = {r.name: r for r in reporters} if reporters else {}
        self._default_reporter = reporters[0].name if reporters else ""
        self._dispatcher: Union[Dispatcher, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher.listen(ArgParseEvent, self.on_arg_parse)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        if len(self._reporters) == 0:
            return
        event.arg_parser.add_argument("-r", "--reporters", nargs='*', choices=self._reporters,
                                      default=[self._default_reporter], help="Set reporter")
        args, *_ = event.arg_parser.parse_known_args()
        for reporter_name in args.reporters:
            reporter = self._reporters[reporter_name]
            assert self._dispatcher is not None
            reporter.subscribe(self._dispatcher)
