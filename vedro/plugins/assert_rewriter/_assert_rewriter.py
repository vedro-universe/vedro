from typing import Type

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

from ._assert_rewriter_module_loader import AssertRewriterModuleLoader

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
        self._global_config.Registry.ModuleLoader.register(AssertRewriterModuleLoader, self)


class AssertRewriter(PluginConfig):
    plugin = AssertRewriterPlugin
    description = "Rewrites assert statements to provide better error messages"
