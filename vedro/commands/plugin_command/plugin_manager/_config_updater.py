import os
from pathlib import Path
from typing import List

from ._config_generator import ConfigGenerator
from ._config_parser import ConfigParser

__all__ = ("ConfigUpdater",)


class ConfigUpdater:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    async def update(self, plugin_package: str, plugin_name: str, *, enabled: bool) -> None:
        config_source = await self._read_config()
        config_parser = ConfigParser()
        config_markup = await config_parser.parse(config_source)
        config_generator = ConfigGenerator(config_markup.get_indent())

        if not config_markup.get_config_section():
            generated = config_generator.gen_config_section(
                config_generator.gen_plugins_section(
                    config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
                )
            )
            start_lineno = 1

        elif not config_markup.get_plugin_list_section():
            generated = config_generator.gen_plugins_section(
                config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            )
            config_section = config_markup.get_config_section()
            assert config_section is not None
            start_lineno = config_section["end"] + 2  # next line + blank line

        elif not config_markup.get_plugin_section(plugin_name):
            generated = config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            plugin_list_section = config_markup.get_plugin_list_section()
            assert plugin_list_section is not None
            start_lineno = plugin_list_section["end"] + 2  # next line + blank line

        elif not config_markup.get_enabled_attr(plugin_name):
            generated = config_generator.gen_enabled_attr(enabled)
            plugin_section = config_markup.get_plugin_section(plugin_name)
            assert plugin_section is not None
            start_lineno = plugin_section["end"] + 1  # next line

        else:
            generated = config_generator.gen_enabled_attr(enabled, new_line=False)
            enabled_attr = config_markup.get_enabled_attr(plugin_name)
            assert enabled_attr is not None
            start_lineno = enabled_attr["start"]

        config_source = self._apply(config_source, generated, start_lineno)
        await self._save_config(config_source)

    def _apply(self, config_source: str, generated: List[str], lineno: int, *,
               linesep: str = os.linesep) -> str:
        config_lines = config_source.split(linesep)

        if lineno > len(config_lines):
            for _ in range(lineno - len(config_lines)):
                config_lines.append("")

        new_config_lines = []
        for num, line in enumerate(config_lines, start=1):
            if num == lineno:
                new_config_lines.extend(generated)
            else:
                new_config_lines.append(line)

        return linesep.join(new_config_lines)

    async def _read_config(self) -> str:
        with open(self._config_path, "r") as f:
            return f.read()

    async def _save_config(self, config_source: str) -> None:
        with open(self._config_path, "w") as f:
            f.write(config_source)
