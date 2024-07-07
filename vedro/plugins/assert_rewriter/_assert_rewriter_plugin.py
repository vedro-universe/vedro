from typing import Type, final

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, ConfigLoadedEvent

from ._assert_rewriter_loader import AssertRewriterLoader
from ._legacy_assert_rewriter_loader import LegacyAssertRewriterLoader

__all__ = ("AssertRewriter", "AssertRewriterPlugin",)


@final
class AssertRewriterPlugin(Plugin):
    """
    Manages the assertion rewriting mechanism for enhanced error messages.

    This plugin subscribes to various events to configure the assertion rewriter
    based on command-line arguments and configuration settings.
    """

    def __init__(self, config: Type["AssertRewriter"]):
        """
        Initialize the AssertRewriterPlugin with the specified configuration.

        :param config: The configuration class for the AssertRewriter plugin.
        """
        super().__init__(config)
        self._legacy_assertions = config.legacy_assertions

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to relevant events to handle configuration and argument parsing.

        :param dispatcher: The event dispatcher to subscribe to.
        """
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the event when the configuration is loaded.

        :param event: The configuration loaded event containing the global config.
        """
        self._global_config: ConfigType = event.config

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the event to parse command-line arguments.

        Adds an argument to enable legacy assertion rewriting for backwards compatibility.

        :param event: The argument parse event containing the argument parser.
        """
        help_message = "Use legacy assertion rewriter for backwards compatibility"
        event.arg_parser.add_argument("--legacy-assertions", action="store_true",
                                      default=self._legacy_assertions, help=help_message)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after command-line arguments are parsed.

        Registers the appropriate assertion rewriter loader based on the parsed arguments.

        :param event: The argument parsed event containing the parsed arguments.
        """
        self._legacy_assertions = event.args.legacy_assertions
        self._global_config.Registry.ModuleLoader.register(
            LegacyAssertRewriterLoader if self._legacy_assertions else AssertRewriterLoader,
            self
        )


class AssertRewriter(PluginConfig):
    """
    Configuration for the AssertRewriterPlugin.

    This configuration allows enabling or disabling the legacy assertion rewriter.
    """

    plugin = AssertRewriterPlugin
    description = "Rewrites assert statements to provide better error messages"

    # Use legacy assertion rewriter for backwards compatibility
    legacy_assertions: bool = False
