from functools import wraps
from typing import Any, Callable, Set, Type, TypeVar, cast

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ConfigLoadedEvent

T = TypeVar("T", bound=Callable[..., Any])


def require_plugin(plugin: Type[PluginConfig]) -> Callable[[T], T]:
    def decorator(fn: T) -> T:
        @wraps(fn)  # type: ignore
        def wrapper(*args, **kwargs):
            enabled_plugins = PluginEnforcerImpl.get_enabled_plugins()
            if plugin.plugin not in enabled_plugins:
                raise RuntimeError(
                    f"The required plugin '{plugin.__name__}' is not enabled.")
            return fn(*args, **kwargs)
        return cast(T, wrapper)
    return decorator


class PluginEnforcerImpl(Plugin):
    _enabled_plugins: Set[Type[Plugin]] = set()

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded)

    def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        self._enabled_plugins.clear()
        for plugin_config in event.config.Plugins.values():
            if plugin_config.enabled:
                self._enabled_plugins.add(plugin_config.plugin)

    @classmethod
    def get_enabled_plugins(cls) -> Set[Type[Plugin]]:
        return cls._enabled_plugins


class PluginEnforcer(PluginConfig):
    plugin = PluginEnforcerImpl
