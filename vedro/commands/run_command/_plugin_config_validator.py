from collections.abc import Sequence
from inspect import isclass
from os import linesep
from typing import Any, Set, Type

from vedro.core import Plugin, PluginConfig

__all__ = ("PluginConfigValidator",)


class PluginConfigValidator:
    """
    Validates plugin configuration classes in Vedro.

    This class ensures that plugin configurations and their dependencies meet the
    expected criteria, including type checks, dependency checks, and attribute validation.
    """

    def __init__(self, *, validate_plugins_attrs: bool = True) -> None:
        """
        Initialize the PluginConfigValidator.

        :param validate_plugins_attrs: Whether to validate unknown attributes in the plugin
                                       configuration class. Default is True.
        """
        self._validate_plugins_attrs = validate_plugins_attrs

    def validate(self, plugin_config: Type[PluginConfig]) -> None:
        """
        Validate a plugin configuration class and its dependencies.

        This method checks the following:
        - The plugin configuration class is a subclass of `PluginConfig`.
        - The `plugin` attribute in the configuration is a subclass of `Plugin`.
        - The `depends_on` attribute is a sequence of valid plugin configuration classes.
        - Enabled dependencies are also enabled when the current plugin is enabled.
        - Optionally, unknown attributes in the plugin configuration class.

        :param plugin_config: The plugin configuration class to validate.
        :raises TypeError: If the plugin configuration or its attributes are invalid.
        :raises ValueError: If dependencies are not enabled when the current plugin is enabled.
        :raises AttributeError: If unknown attributes are found in the plugin configuration.
        """
        if not self._is_subclass(plugin_config, PluginConfig):
            raise TypeError(
                f"PluginConfig '{plugin_config}' must be a subclass of 'vedro.core.PluginConfig'"
            )

        if not self._is_subclass(plugin_config.plugin, Plugin) or (plugin_config.plugin is Plugin):
            raise TypeError(
                f"Attribute 'plugin' in '{plugin_config.__name__}' must be a subclass of "
                "'vedro.core.Plugin'"
            )

        if not isinstance(plugin_config.depends_on, Sequence):
            raise TypeError(
                f"Attribute 'depends_on' in '{plugin_config.__name__}' plugin must be a list or "
                f"another sequence type ({type(plugin_config.depends_on)} provided). "
                + linesep.join([
                    "Example:",
                    "  @computed",
                    "  def depends_on(cls):",
                    "    return [Config.Plugins.Tagger]"
                ])
            )

        for dep in plugin_config.depends_on:
            if not self._is_subclass(dep, PluginConfig):
                raise TypeError(
                    f"Dependency '{dep}' in 'depends_on' of '{plugin_config.__name__}' "
                    "must be a subclass of 'vedro.core.PluginConfig'"
                )

        if self._validate_plugins_attrs:
            self._validate_plugin_config_attrs(plugin_config)

    def _validate_plugin_config_attrs(self, plugin_config: Type[PluginConfig]) -> None:
        """
        Validate the attributes of a plugin configuration class.

        Ensures that no unknown attributes are defined in the plugin configuration.

        :param plugin_config: The plugin configuration class to validate.
        :raises AttributeError: If unknown attributes are found in the plugin configuration.
        """
        unknown_attrs = self._get_attrs(plugin_config) - self._get_parent_attrs(plugin_config)
        if unknown_attrs:
            attrs = ", ".join(unknown_attrs)
            raise AttributeError(
                f"{plugin_config.__name__} configuration contains unknown attributes: {attrs}"
            )

    def _is_subclass(self, cls: Any, parent: Any) -> bool:
        """
        Check if the given class is a subclass of a specified parent class.

        :param cls: The class to check.
        :param parent: The parent class to check against.
        :return: True if `cls` is a subclass of `parent`, False otherwise.
        """
        return isclass(cls) and issubclass(cls, parent)

    def _get_attrs(self, cls: type) -> Set[str]:
        """
        Retrieve the set of attributes for a class.

        :param cls: The class to retrieve attributes for.
        :return: A set of attribute names for the class.
        """
        return set(vars(cls))

    def _get_parent_attrs(self, cls: type) -> Set[str]:
        """
        Recursively retrieve attributes from parent classes.

        :param cls: The class to retrieve parent attributes for.
        :return: A set of attribute names for the parent classes.
        """
        attrs = set()
        # `object` (the base for all classes) has no __bases__
        for base in cls.__bases__:
            attrs |= self._get_attrs(base)
            attrs |= self._get_parent_attrs(base)
        return attrs
