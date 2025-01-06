from typing import Sequence, Type

from ._dispatcher import Dispatcher, Subscriber
from .config_loader import Section as ConfigSection
from .config_loader import computed

__all__ = ("Plugin", "PluginConfig",)


class Plugin(Subscriber):
    """
    Represents a base class for all plugins in Vedro.

    Plugins define custom behavior by subscribing to events using the `subscribe` method.
    Each plugin is associated with a configuration class (`PluginConfig`) that specifies
    its settings and dependencies.
    """

    def __init__(self, config: Type["PluginConfig"]) -> None:
        """
        Initialize the Plugin instance with the given configuration class.

        :param config: The configuration class for the plugin, which must be a subclass
                       of `PluginConfig`.
        :raises TypeError: If the provided `config` is not a subclass of `PluginConfig`.
        """
        if not issubclass(config, PluginConfig):
            raise TypeError(f"PluginConfig {config} should be subclass of vedro.core.PluginConfig")
        self._config = config

    @property
    def config(self) -> Type["PluginConfig"]:
        """
        Retrieve the configuration class associated with the plugin.

        :return: The configuration class for the plugin.
        """
        return self._config

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe the plugin to events using the given dispatcher.

        This method is intended to be overridden by subclasses to define event listeners.

        :param dispatcher: The event dispatcher used to register event listeners.
        """
        pass

    def __repr__(self) -> str:
        """
        Return a string representation of the Plugin instance.

        :return: A string describing the plugin and its configuration class.
        """
        return f"{self.__class__.__name__}({self._config.__name__})"


class PluginConfig(ConfigSection):
    """
    Represents the configuration for a plugin.

    This class defines the settings and dependencies for a plugin, including the plugin class,
    a description, whether the plugin is enabled, and any dependencies on other plugins.
    """

    plugin: Type[Plugin] = Plugin
    """
    The plugin class associated with this configuration. Defaults to the base `Plugin` class.
    """

    description: str = ""
    """
    A brief description of the plugin.
    """

    enabled: bool = True
    """
    Specifies whether the plugin is enabled. Defaults to True.
    """

    @computed
    def depends_on(cls) -> Sequence[Type["PluginConfig"]]:
        """
        Define the dependencies of this plugin configuration.

        This method can be overridden in subclasses to specify other plugin configurations
        that this plugin depends on.

        :return: A sequence of plugin configuration classes that this plugin depends on.
        """
        return ()
