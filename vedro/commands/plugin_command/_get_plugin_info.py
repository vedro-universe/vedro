from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, metadata
from typing import Type

import vedro
from vedro.core import PluginConfig

__all__ = ("get_plugin_info", "PluginInfo",)


@dataclass
class PluginInfo:
    name: str
    enabled: bool
    package: str = "Unknown"
    version: str = "0.0.0"
    summary: str = "No data"
    is_default: bool = False


def get_plugin_info(plugin_config: Type[PluginConfig]) -> PluginInfo:
    plugin_name = getattr(plugin_config, "__name__", "Plugin")
    plugin_info = PluginInfo(plugin_name, plugin_config.enabled)

    plugin = plugin_config.plugin
    module = plugin.__module__
    package = module.split(".")[0]

    # plugin declared in vedro.cfg.py
    if module == "vedro.cfg":
        plugin_info.package = module
        if plugin_config.description:
            plugin_info.summary = plugin_config.description
        return plugin_info

    # default plugin
    if package == "vedro":
        summary = plugin_config.description or "Core Plugin"
        plugin_info.package = ".".join(module.split(".")[:-1])
        plugin_info.version = vedro.__version__
        plugin_info.summary = summary
        plugin_info.is_default = True
        return plugin_info

    try:
        meta = metadata(package)
    except PackageNotFoundError:
        return plugin_info

    plugin_info.package = package
    if "Version" in meta:
        plugin_info.version = meta["Version"]
    if "Summary" in meta:
        plugin_info.summary = meta["Summary"]
    return plugin_info
