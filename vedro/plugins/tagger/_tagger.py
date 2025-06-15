from enum import Enum
from typing import Any, Callable, Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig, VirtualScenario
from vedro.events import ArgParsedEvent, ArgParseEvent, StartupEvent

from ._tag_matcher import TagMatcher
from .logic_tag_matcher import LogicTagMatcher

__all__ = ("Tagger", "TaggerPlugin",)


@final
class TaggerPlugin(Plugin):
    """
    Implements a plugin that allows selective scenario execution based on tags.

    The plugin subscribes to various events during the lifecycle of a test run, parses
    user-specified tag expressions, and filters scenarios accordingly. The logical
    expressions are evaluated using a `TagMatcher` instance, which determines if
    a scenario should be executed based on its associated tags.
    """

    def __init__(self, config: Type["Tagger"], *,
                 tag_matcher_factory: Callable[[str], TagMatcher] = LogicTagMatcher) -> None:
        """
        Initialize the TaggerPlugin with a configuration and a tag matcher factory.

        :param config: The configuration class for the TaggerPlugin.
        :param tag_matcher_factory: A callable that creates a TagMatcher instance given a tag
                                    expression. Defaults to `LogicTagMatcher`.
        """
        super().__init__(config)
        self._matcher_factory = tag_matcher_factory
        self._matcher: Union[TagMatcher, None] = None
        self._tags_expr: Union[str, None] = None

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe the plugin to relevant events in the dispatcher's event lifecycle.

        :param dispatcher: The event dispatcher to which the plugin subscribes.
        """
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
            .listen(ArgParsedEvent, self.on_arg_parsed) \
            .listen(StartupEvent, self.on_startup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the `ArgParseEvent` by adding the tag argument to the argument parser.

        :param event: The event containing the argument parser.
        """
        help_message = ("Specify tags to selectively run scenarios. "
                        "More info: vedro.io/docs/features/tags")
        event.arg_parser.add_argument("-t", "--tags", help=help_message)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the `ArgParsedEvent` by storing the parsed tags expression.

        :param event: The event containing parsed arguments.
        :raises ValueError: If the provided tags argument is an empty string.
        """
        self._tags_expr = event.args.tags
        if isinstance(self._tags_expr, str) and self._tags_expr.strip() == "":
            raise ValueError("Tags cannot be an empty string. Please specify valid tags")

    def _get_tags(self, scenario: VirtualScenario, validate: Callable[[str], bool]) -> Any:
        """
        Retrieve and validate the tags associated with a scenario.

        :param scenario: The scenario from which to extract tags.
        :param validate: A callable to validate each tag.
        :return: A list of validated tags.
        :raises TypeError: If the scenario's tags are not a list, tuple, or set.
        :raises ValueError: If any tag is not valid.
        """

        # TODO: In v2, consider moving the 'tags' attribute directly into the Scenario class
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
        """
        Handle the `StartupEvent` by filtering scenarios based on the provided tags expression.

        :param event: The startup event containing the scenario scheduler.
        """
        self._matcher = self._matcher_factory(str(self._tags_expr))

        async for scenario in event.scheduler:
            tags = self._get_tags(scenario, self._matcher.validate)
            if self._tags_expr and not self._matcher.match(set(tags)):
                event.scheduler.ignore(scenario)


class Tagger(PluginConfig):
    """
    Configuration class for the TaggerPlugin.
    """

    plugin = TaggerPlugin
    description = "Allows scenarios to be selectively run based on user-defined tags"
