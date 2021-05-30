from typing import Any, Union

from ..._core import Dispatcher
from ..._events import ArgParsedEvent, ArgParseEvent
from ..plugin import Plugin
from ._reporter import Reporter
from .reporters import RichReporter, SilentReporter


class Director(Plugin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._dispatcher: Union[Dispatcher, None] = None
        self._reporter: Union[Reporter, None] = None
        self._reporters = {
            "rich": RichReporter,
            "silent": SilentReporter,
        }
        self._default_reporter = "rich"

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)
        self._dispatcher = dispatcher

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("-r", "--reporter",
                                      choices=self._reporters, default=self._default_reporter)

        args, *_ = event.arg_parser.parse_known_args()
        self._reporter = self._reporters[args.reporter]()
        self._reporter.on_arg_parse(event)

        self._dispatcher.register(self._reporter)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        pass
