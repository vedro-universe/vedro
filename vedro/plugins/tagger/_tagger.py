from typing import Union

from vedro.core import Dispatcher, Plugin
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

__all__ = ("Tagger",)


class Tagger(Plugin):
    def __init__(self) -> None:
        self._tags: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("-t", "--tags", nargs="?", help="Set tag")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._tags = event.args.tags

    def on_startup(self, event: StartupEvent) -> None:
        if self._tags is None:
            return
        for scenario in event.scenarios:
            tags = getattr(scenario._orig_scenario, "tags", ())
            if self._tags not in tags:
                scenario.skip()
