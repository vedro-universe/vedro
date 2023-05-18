from typing import Any, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig, VirtualScenario
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

    def _validate_tags(self, scenario: VirtualScenario, tags: Any) -> bool:
        if not isinstance(tags, (list, tuple, set)):
            raise TypeError(f"Scenario '{scenario.rel_path}' tags must be a list, tuple or set, "
                            f"got {type(tags)}")

        for tag in tags:
            if not tag.isidentifier():
                raise ValueError(
                    f"Scenario '{scenario.rel_path}' tag '{tag}' is not a valid identifier")

        return True

    async def on_startup(self, event: StartupEvent) -> None:
        if self._tags is None:
            return
        async for scenario in event.scheduler:
            tags = getattr(scenario._orig_scenario, "tags", ())
            assert self._validate_tags(scenario, tags)

            if self._tags not in tags:
                event.scheduler.ignore(scenario)


class Tagger(PluginConfig):
    plugin = TaggerPlugin
    description = "Allows scenarios to be selectively run based on user-defined tags"
