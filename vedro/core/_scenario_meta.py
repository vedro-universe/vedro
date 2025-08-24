from inspect import isclass
from keyword import iskeyword
from typing import Any, Optional, Type, TypeVar, Union, cast, overload

from niltype import Nil, Nilable, NilType

from .._scenario import Scenario
from ._plugin import Plugin

__all__ = ("get_scenario_meta", "set_scenario_meta",)


PluginType = Union[Plugin, Type[Plugin]]
T = TypeVar("T")


def set_scenario_meta(scenario: Type[Scenario], key: str, value: Any, *,
                      plugin: PluginType, fallback_key: Optional[str] = None) -> None:
    """
    Set a metadata key-value pair on a scenario class.

    This function associates a metadata value with a key for a specific plugin
    and attaches it to the given scenario class. Optionally, a fallback key can
    be used for backward compatibility.

    :param scenario: The scenario class on which the metadata will be set.
    :param key: The key for the metadata, which must be a valid Python identifier.
    :param value: The value to be associated with the specified key.
    :param plugin: The plugin or plugin class to namespace the metadata.
    :param fallback_key: An optional fallback key to set the value as an attribute
                         on the scenario class for backward compatibility.
                         Defaults to None.

    :raises TypeError: If `scenario` is not a subclass of `Scenario`.
    :raises ValueError: If `key` is not a valid Python identifier or is a reserved keyword.
    :raises TypeError: If `plugin` is not a `Plugin` instance or subclass of `Plugin`.
    """
    _validate_scenario(scenario) and _validate_key(key) and _validate_plugin(plugin)

    meta_key = _get_meta_key(plugin, key)

    # Do not use _set directly
    scenario.__vedro__meta__._set(meta_key, value)  # type: ignore

    # For backward compatibility, also set the older attribute.
    if fallback_key is not None:
        setattr(scenario, fallback_key, value)


@overload
def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: T,
                      fallback_key: Optional[str] = None) -> T:  # pragma: no cover
    ...  # When default is provided, return T


@overload
def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: NilType = Nil,
                      fallback_key: Optional[str] = None) -> NilType:  # pragma: no cover
    ...  # When default is not provided, return NilType


def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: Nilable[T] = Nil,
                      fallback_key: Optional[str] = None) -> Union[T, NilType]:
    """
    Retrieve a metadata value associated with a scenario class.

    This function retrieves the value of a metadata key set for a specific plugin
    on a scenario class. If the metadata is not found, it falls back to a default
    value or legacy attribute if specified.

    :param scenario: The scenario class from which the metadata will be retrieved.
    :param key: The key for the metadata, which must be a valid Python identifier.
    :param plugin: The plugin or plugin class to namespace the metadata.
    :param default: The default value to return if the key is not found.
                    Defaults to `Nil`.
    :param fallback_key: An optional fallback key to look up the value as an attribute
                         on the scenario class. Defaults to None.

    :return: The value of the metadata key if found. If the key is not found,
             returns the default value.

    :raises TypeError: If `scenario` is not a subclass of `Scenario`.
    :raises ValueError: If `key` is not a valid Python identifier or is a reserved keyword.
    :raises TypeError: If `plugin` is not a `Plugin` instance or subclass of `Plugin`.
    """
    _validate_scenario(scenario) and _validate_key(key) and _validate_plugin(plugin)

    meta_key = _get_meta_key(plugin, key)

    # Attempt to retrieve meta from the scenario
    meta_val = scenario.__vedro__meta__.get(meta_key)  # type: ignore
    if meta_val is not Nil:
        return cast(T, meta_val)

    # Fallback to template if it exists
    scenario_template = getattr(scenario, "__vedro__template__", None)
    if scenario_template is not None:
        tmpl_meta_val = scenario_template.__vedro__meta__.get(meta_key)
        if tmpl_meta_val is not Nil:
            return cast(T, tmpl_meta_val)

    # Fallback to legacy attribute if provided
    if fallback_key is not None:
        legacy_val = getattr(scenario, fallback_key, default)
        return cast(Union[T, NilType], legacy_val)

    # Otherwise return default
    return default


def _validate_scenario(scenario: Type[Scenario]) -> bool:
    """
    Validate that the input is a valid scenario class.

    :param scenario: The scenario class to validate.
    :return: True if the scenario is valid.
    :raises TypeError: If the input is not a subclass of `Scenario`.
    """
    if not (isclass(scenario) and issubclass(scenario, Scenario) and scenario != Scenario):
        raise TypeError("`scenario` must be a subclass of `Scenario`")
    return True


def _validate_key(key: str) -> bool:
    """
    Validate that the key is a valid Python identifier and not a reserved keyword.

    :param key: The key to validate.
    :return: True if the key is valid.
    :raises ValueError: If the key is not a valid identifier or is a reserved keyword.
    """
    if not (isinstance(key, str) and key.isidentifier() and not iskeyword(key)):
        raise ValueError("`key` must be a valid Python identifier and not a reserved keyword")
    return True


def _validate_plugin(plugin: PluginType) -> bool:
    """
    Validate that the input is a valid plugin or plugin class.

    :param plugin: The plugin instance or class to validate.
    :return: True if the plugin is valid.
    :raises TypeError: If the input is not a `Plugin` instance or subclass of `Plugin`.
    """
    if not (isinstance(plugin, Plugin) or
            (isclass(plugin) and issubclass(plugin, Plugin) and plugin != Plugin)):
        raise TypeError("`plugin` must be a Plugin instance or a subclass of Plugin")
    return True


def _get_meta_key(plugin: PluginType, key: str) -> str:
    """
    Generate a namespaced metadata key for the plugin.

    :param plugin: The plugin instance or class used for namespacing.
    :param key: The original metadata key.
    :return: A namespaced key combining the plugin's name and the original key.
    """
    namespace = _get_plugin_name(plugin)
    return f"{namespace}.{key}"


def _get_plugin_name(plugin: PluginType) -> str:
    """
    Retrieve the fully qualified name of the plugin.

    :param plugin: The plugin instance or class.
    :return: The fully qualified name of the plugin in the format
             'module_name.PluginClassName'.
    """
    if isinstance(plugin, Plugin):
        return f"{plugin.__module__}.{plugin.__class__.__name__}"
    return f"{plugin.__module__}.{plugin.__name__}"
