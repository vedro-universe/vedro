from typing import Type

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from ._assert_rewriter_loader import AssertRewriterLoader
from ._legacy_assert_rewriter_loader import LegacyAssertRewriterLoader

__all__ = ("AssertRewriter", "AssertRewriterPlugin",)


class AssertRewriterPlugin(Plugin):
    def __init__(self, config: Type["AssertRewriter"]):
        super().__init__(config)
        self._legacy_assertions = config.legacy_assertions

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        help_message = "Use legacy assertion rewriter for backwards compatibility"
        event.arg_parser.add_argument("--legacy-assertions", action="store_true",
                                      default=self._legacy_assertions, help=help_message)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._legacy_assertions = event.args.legacy_assertions
        self._global_config.Registry.ModuleLoader.register(
            LegacyAssertRewriterLoader if self._legacy_assertions else AssertRewriterLoader,
            self
        )


class AssertRewriter(PluginConfig):
    plugin = AssertRewriterPlugin
    description = "Rewrites assert statements to provide better error messages"

    # Use legacy assertion rewriter for backwards compatibility
    legacy_assertions: bool = False
