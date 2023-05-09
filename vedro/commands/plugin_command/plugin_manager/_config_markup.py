from typing import Dict, TypedDict, Union

__all__ = ("ConfigMarkup", "ConfigSectionType", "PluginListSectionType",
           "PluginSectionType", "EnabledAttrType")


class EnabledAttrType(TypedDict):
    offset: int
    start: int
    end: Union[int, None]


class PluginSectionType(TypedDict):
    offset: int
    start: int
    end: Union[int, None]
    enabled: Union[EnabledAttrType, None]


class PluginListSectionType(TypedDict):
    offset: int
    start: int
    end: Union[int, None]
    children: Union[Dict[str, PluginSectionType], None]


class ConfigSectionType(TypedDict):
    offset: int
    start: int
    end: Union[int, None]
    plugins: Union[PluginListSectionType, None]


class ConfigMarkup:
    def __init__(self, config: Union[ConfigSectionType, None], indent: str) -> None:
        self._config_section = config
        self._indent = indent

    def get_indent(self) -> str:
        return self._indent

    def get_config_section(self) -> Union[ConfigSectionType, None]:
        return self._config_section

    def get_plugin_list_section(self) -> Union[PluginListSectionType, None]:
        config_section = self.get_config_section()
        return config_section["plugins"] if config_section else None

    def get_plugin_section(self, plugin_name: str) -> Union[PluginSectionType, None]:
        plugin_list_section = self.get_plugin_list_section()
        return plugin_list_section["children"][plugin_name] if plugin_list_section else None

    def get_enabled_attr(self, plugin_name: str) -> Union[EnabledAttrType, None]:
        plugin_section = self.get_plugin_section(plugin_name)
        return plugin_section["enabled"] if plugin_section else None
