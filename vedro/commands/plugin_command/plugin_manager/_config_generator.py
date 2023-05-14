from typing import List

__all__ = ("ConfigGenerator",)


class ConfigGenerator:
    def __init__(self, indent: str) -> None:
        self._indent = indent

    def gen_config_section(self, plugins_section: List[str], *, offset: int = 0) -> List[str]:
        return [
            f"{self._indent * offset}class Config(vedro.Config):",
            *plugins_section,
        ]

    def gen_plugins_section(self, plugin_section: List[str], *, offset: int = 1) -> List[str]:
        return [
            "",
            f"{self._indent * offset}class Plugins(vedro.Config.Plugins):",
            *plugin_section,
        ]

    def gen_plugin_section(self, plugin_package: str, plugin_name: str, enabled: bool, *,
                           offset: int = 2) -> List[str]:
        return [
            "",
            f"{self._indent * offset}class {plugin_name}({plugin_package}.{plugin_name}):",
            f"{self._indent * (offset + 1)}enabled = {enabled}",
        ]

    def gen_enabled_attr(self, enabled: bool, *,
                         offset: int = 3) -> List[str]:
        return [
            f"{self._indent * offset}enabled = {enabled}"
        ]

    def gen_import(self, package: str) -> List[str]:
        return [
            f"import {package}",
        ]
