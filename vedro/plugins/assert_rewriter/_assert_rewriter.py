from typing import Type

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

from ._assert_rewriter_module_loader import AssertRewriterModuleLoader
from ._legacy_assert_rewriter import LegacyAssertRewriter

__all__ = ("AssertRewriter", "AssertRewriterPlugin",)


class AssertRewriterPlugin(Plugin):
    def __init__(self, config: Type["AssertRewriter"]):
        super().__init__(config)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                  .listen(ArgParsedEvent, self.on_arg_parsed)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._global_config: ConfigType = event.config

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        exp_pretty_diff = getattr(event.args, "exp_pretty_diff", False)
        module_loader = AssertRewriterModuleLoader if exp_pretty_diff else LegacyAssertRewriter
        self._global_config.Registry.ModuleLoader.register(module_loader, self)


class AssertRewriter(PluginConfig):
    plugin = AssertRewriterPlugin
    description = "Rewrites assert statements to provide better error messages"
