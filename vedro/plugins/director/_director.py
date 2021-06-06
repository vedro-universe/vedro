from typing import Callable, Dict, Optional, Union

from ..._core import Dispatcher
from ..._events import ArgParseEvent
from ..plugin import Plugin
from ._reporter import Reporter

__all__ = ("Director",)


class Director(Plugin):
    def __init__(self, reporters: Optional[Dict[str, Callable[[], Reporter]]] = None,
                 default_reporter: Optional[str] = None) -> None:
        self._reporters = reporters if reporters else {}
        self._default_reporter = default_reporter
        self._dispatcher: Union[Dispatcher, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher.listen(ArgParseEvent, self.on_arg_parse)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        if len(self._reporters) == 0:
            return
        event.arg_parser.add_argument("-r", "--reporters", nargs='*',
                                      choices=self._reporters, default=[self._default_reporter])
        args, *_ = event.arg_parser.parse_known_args()
        for reporter_name in args.reporters:
            reporter = self._reporters[reporter_name]()
            assert self._dispatcher is not None
            reporter.subscribe(self._dispatcher)
