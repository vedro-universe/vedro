from typing import Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

__all__ = ("Tagger", "TaggerPlugin",)


class TaggerPlugin(Plugin):
    def __init__(self, config: Type["Tagger"]) -> None:
        super().__init__(config)
        self._tags: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("-t", "--tags", nargs="?", help="Set tag")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._tags = event.args.tags

    async def on_startup(self, event: StartupEvent) -> None:
        if self._tags is None:
            return
        async for scenario in event.scheduler:
            tags = getattr(scenario._orig_scenario, "tags", ())
            if self._tags not in tags:
                event.scheduler.ignore(scenario)


class Tagger(PluginConfig):
    plugin = TaggerPlugin
