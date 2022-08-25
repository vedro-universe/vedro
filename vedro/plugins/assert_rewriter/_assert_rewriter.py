from typing import Type

from vedro.core import ConfigType, Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ConfigLoadedEvent

from ._scenario_assert_rewriter_loader import ScenarioAssertRewriterLoader

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
        try:
            from dessert import AssertionRewritingHook  # type: ignore
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Package 'dessert' is not found, install it via 'pip install dessert'")

        self._global_config.Registry.ScenarioLoader.register(
            lambda: ScenarioAssertRewriterLoader(AssertionRewritingHook()), self)


class AssertRewriter(PluginConfig):
    plugin = AssertRewriterPlugin
