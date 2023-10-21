from typing import Dict, List, TypedDict, Union

__all__ = ("ConfigMarkup", "ConfigSectionType", "PluginListSectionType",
           "PluginSectionType", "EnabledAttrType", "ImportType", "MarkupElement",)


class MarkupElement(TypedDict):
    offset: int
    start: int
    end: int


class ImportType(MarkupElement):
    alias: Union[str, None]


class EnabledAttrType(MarkupElement):
    pass


class PluginSectionType(MarkupElement):
    enabled: Union[EnabledAttrType, None]


class PluginListSectionType(MarkupElement):
    children: Dict[str, PluginSectionType]


class ConfigSectionType(MarkupElement):
    plugins: Union[PluginListSectionType, None]


class ConfigMarkup:
    def __init__(self, config: Union[ConfigSectionType, None],
                 imports: Dict[str, ImportType],
                 indent: str) -> None:
        self._config_section = config
        self._imports = imports
        self._indent = indent

    def get_indent(self) -> str:
        return self._indent

    def get_import_list(self) -> List[ImportType]:
        return list(self._imports.values())

    def get_import(self, package_name: str) -> Union[ImportType, None]:
        return self._imports.get(package_name, None)

    def get_config_section(self) -> Union[ConfigSectionType, None]:
        return self._config_section

    def get_plugin_list_section(self) -> Union[PluginListSectionType, None]:
        config_section = self.get_config_section()
        return config_section["plugins"] if config_section else None

    def get_plugin_section(self, plugin_name: str) -> Union[PluginSectionType, None]:
        plugin_list_section = self.get_plugin_list_section()
        return plugin_list_section["children"].get(plugin_name) if plugin_list_section else None

    def get_enabled_attr(self, plugin_name: str) -> Union[EnabledAttrType, None]:
        plugin_section = self.get_plugin_section(plugin_name)
        return plugin_section["enabled"] if plugin_section else None
