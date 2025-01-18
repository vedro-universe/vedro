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
    if not (isclass(scenario) and issubclass(scenario, Scenario) and scenario != Scenario):
        raise TypeError("`scenario` must be a subclass of `Scenario`")
    return True


def _validate_key(key: str) -> bool:
    if not (isinstance(key, str) and key.isidentifier() and not iskeyword(key)):
        raise ValueError("`key` must be a valid Python identifier and not a reserved keyword")
    return True


def _validate_plugin(plugin: PluginType) -> bool:
    if not (isinstance(plugin, Plugin) or
            (isclass(plugin) and issubclass(plugin, Plugin) and plugin != Plugin)):
        raise TypeError("`plugin` must be a Plugin instance or a subclass of Plugin")
    return True


def _get_meta_key(plugin: PluginType, key: str) -> str:
    namespace = _get_plugin_name(plugin)
    return f"{namespace}.{key}"


def _get_plugin_name(plugin: PluginType) -> str:
    if isinstance(plugin, Plugin):
        return f"{plugin.__module__}.{plugin.__class__.__name__}"
    return f"{plugin.__module__}.{plugin.__name__}"
