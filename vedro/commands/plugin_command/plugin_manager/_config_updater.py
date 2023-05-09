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
            start_lineno = 0

        elif not config_markup.get_plugin_list_section():
            generated = config_generator.gen_plugins_section(
                config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            )
            config_section = config_markup.get_config_section()
            start_lineno = config_section["end"] + 2  # next line + blank line

        elif not config_markup.get_plugin_section(plugin_name):
            generated = config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            plugin_list_section = config_markup.get_plugin_list_section()
            start_lineno = plugin_list_section["end"] + 2  # next line + blank line

        elif not config_markup.get_enabled_attr(plugin_name):
            generated = config_generator.gen_enabled_attr(enabled)
            plugin_section = config_markup.get_plugin_section(plugin_name)
            start_lineno = plugin_section["end"] + 1  # next line

        else:
            generated = config_generator.gen_enabled_attr(enabled)
            enabled_attr = config_markup.get_enabled_attr(plugin_name)
            start_lineno = enabled_attr["start"]

        config_source = self._apply(config_source, generated, start_lineno)
        print(f"config_source:\n{config_source}")
        # await self._save_config(config_source)

    def _apply(self, config_source: str, generated: List[str], lineno: int, *,
               linesep: str = os.linesep) -> str:
        config_lines = config_source.splitlines()
        for num, line in enumerate(generated):
            if num + lineno >= len(config_lines):
                for _ in range(num + lineno - len(config_lines) - 1):
                    config_lines.append("")
                config_lines.append(f"{line}")
            else:
                config_lines[num + lineno] = line
        return linesep.join(config_lines)


    async def _read_config(self) -> str:
        with open(self._config_path, "r") as f:
            return f.read()

    async def _save_config(self, config_source: List[str]) -> None:
        with open(self._config_path, "w") as f:
            f.writelines(config_source)
