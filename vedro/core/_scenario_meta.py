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
    assert isclass(scenario) and issubclass(scenario, Scenario) and scenario != Scenario
    assert isinstance(key, str) and key.isidentifier() and not iskeyword(key)
    assert isinstance(plugin, Plugin) or (issubclass(plugin, Plugin) and plugin != Plugin)

    namespace = _get_plugin_name(plugin)
    meta_key = f"{namespace}.{key}"

    # do not use this method directly
    scenario.__vedro__meta__._set(meta_key, value)  # type: ignore

    if fallback_key is not None:
        # backward compatibility
        setattr(scenario, fallback_key, value)


@overload
def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: T,
                      fallback_key: Optional[str] = None) -> T:
    ...  # When default is provided, return T


@overload
def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: NilType = Nil,
                      fallback_key: Optional[str] = None) -> NilType:
    ...  # When default is not provided, return NilType


def get_scenario_meta(scenario: Type[Scenario], key: str, *,
                      plugin: PluginType,
                      default: Nilable[T] = Nil,
                      fallback_key: Optional[str] = None) -> Union[T, NilType]:
    assert issubclass(scenario, Scenario) and scenario != Scenario
    assert isinstance(key, str) and key.isidentifier() and not iskeyword(key)
    assert isinstance(plugin, Plugin) or (issubclass(plugin, Plugin) and plugin != Plugin)

    namespace = _get_plugin_name(plugin)
    meta_key = f"{namespace}.{key}"

    if (meta_val := scenario.__vedro__meta__.get(meta_key)) is not Nil:  # type: ignore
        return cast(T, meta_val)

    template = getattr(scenario, "__vedro__template__", None)
    if template is not None:
        if (tmpl_meta_val := template.__vedro__meta__.get(meta_key)) is not Nil:
            return cast(T, tmpl_meta_val)

    if fallback_key is not None:
        # backward compatibility
        # do not use fallback_key in new code
        return getattr(scenario, fallback_key, default)

    return default


def _get_plugin_name(plugin: PluginType) -> str:
    if isinstance(plugin, Plugin):
        return f"{plugin.__module__}.{plugin.__class__.__name__}"
    return f"{plugin.__module__}.{plugin.__name__}"
