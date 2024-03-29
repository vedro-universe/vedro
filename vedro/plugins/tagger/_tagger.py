from enum import Enum
from typing import Any, Callable, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

from ._tag_matcher import TagMatcher
from .logic_tag_matcher import LogicTagMatcher

__all__ = ("Tagger", "TaggerPlugin",)


class TaggerPlugin(Plugin):
    def __init__(self, config: Type["Tagger"], *,
                 tag_matcher_factory: Callable[[str], TagMatcher] = LogicTagMatcher) -> None:
        super().__init__(config)
        self._matcher_factory = tag_matcher_factory
        self._matcher: Union[TagMatcher, None] = None
        self._tags_expr: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed) \
            .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("-t", "--tags",
                                      help="Specify tags to selectively run scenarios")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._tags_expr = event.args.tags

    def _get_tags(self, scenario: VirtualScenario, validate: Callable[[str], bool]) -> Any:
        orig_tags = getattr(scenario._orig_scenario, "tags", ())
        if not isinstance(orig_tags, (list, tuple, set)):
            raise TypeError(f"Scenario '{scenario.unique_id}' tags must be a list, tuple or set, "
                            f"got {type(orig_tags)}")
        tags = []
        for tag in orig_tags:
            if isinstance(tag, Enum):
                tag = tag.value
            try:
                validate(tag)
            except Exception as e:
                raise ValueError(f"Scenario '{scenario.unique_id}' tag '{tag}' is not valid ({e})")
            else:
                tags.append(tag)
        return tags

    async def on_startup(self, event: StartupEvent) -> None:
        self._matcher = self._matcher_factory(str(self._tags_expr))

        async for scenario in event.scheduler:
            tags = self._get_tags(scenario, self._matcher.validate)
            if self._tags_expr and not self._matcher.match(set(tags)):
                event.scheduler.ignore(scenario)


class Tagger(PluginConfig):
    plugin = TaggerPlugin
    description = "Allows scenarios to be selectively run based on user-defined tags"
