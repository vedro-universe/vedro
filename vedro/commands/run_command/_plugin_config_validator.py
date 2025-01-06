from collections.abc import Sequence
from inspect import isclass
from os import linesep
from typing import Any, Set, Type

from vedro.core import Plugin, PluginConfig

__all__ = ("PluginConfigValidator",)


class PluginConfigValidator:
    def __init__(self, *, validate_plugins_attrs: bool = True) -> None:
        self._validate_plugins_attrs = validate_plugins_attrs

    def validate(self, plugin_config: Type[PluginConfig],
                 available_plugins: Set[Type[PluginConfig]]) -> None:
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
                f"Attribute 'depends_on' in '{plugin_config.__name__}' plugin must be a list or"
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

            if dep not in available_plugins:
                raise ValueError(
                    f"Dependency '{dep.__name__}' in 'depends_on' of '{plugin_config.__name__}' "
                    "is not found among the configured plugins"
                )

            if plugin_config.enabled and not dep.enabled:
                raise ValueError(
                    f"Dependency '{dep.__name__}' in 'depends_on' of '{plugin_config.__name__}' "
                    "is not enabled"
                )

        if self._validate_plugins_attrs:
            self._validate_plugin_config_attrs(plugin_config)

    def _validate_plugin_config_attrs(self, plugin_config: Type[PluginConfig]) -> None:
        unknown_attrs = self._get_attrs(plugin_config) - self._get_parent_attrs(plugin_config)
        if unknown_attrs:
            attrs = ", ".join(unknown_attrs)
            raise AttributeError(
                f"{plugin_config.__name__} configuration contains unknown attributes: {attrs}"
            )

    def _is_subclass(self, cls: Any, parent: Any) -> bool:
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
