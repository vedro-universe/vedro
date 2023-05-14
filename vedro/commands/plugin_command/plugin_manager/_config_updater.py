import os
from pathlib import Path
from typing import List, Union

from vedro.core import Config

from ._config_generator import ConfigGenerator
from ._config_markup import ConfigMarkup
from ._config_parser import ConfigParser

__all__ = ("ConfigUpdater",)


class ConfigUpdater:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._default_config_path = Path("vedro.cfg.py")

    async def update(self, plugin_package: str, plugin_name: str, *, enabled: bool) -> None:
        config_path = self._get_config_path()
        config_source = await self._read_config(config_path)
        config_parser = ConfigParser()
        config_markup = await config_parser.parse(config_source)
        config_generator = ConfigGenerator(config_markup.get_indent())

        if not config_markup.get_config_section():
            imports = self._gen_imports_if_needed(["vedro", plugin_package],
                                                  config_markup, config_generator)
            generated = config_generator.gen_config_section(
                config_generator.gen_plugins_section(
                    config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
                )
            )
            last_import = self._get_last_import(config_markup) or 0
            start_lineno = last_import + 1
            replace = False

        elif not config_markup.get_plugin_list_section():
            imports = self._gen_imports_if_needed(["vedro", plugin_package],
                                                  config_markup, config_generator)
            generated = config_generator.gen_plugins_section(
                config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            )
            config_section = config_markup.get_config_section()
            assert config_section is not None
            start_lineno = config_section["end"] + 1
            replace = False

        elif not config_markup.get_plugin_section(plugin_name):
            imports = self._gen_imports_if_needed([plugin_package],
                                                  config_markup, config_generator)
            generated = config_generator.gen_plugin_section(plugin_package, plugin_name, enabled)
            plugin_list_section = config_markup.get_plugin_list_section()
            assert plugin_list_section is not None
            start_lineno = plugin_list_section["end"] + 1
            replace = False

        elif not config_markup.get_enabled_attr(plugin_name):
            imports = []
            generated = config_generator.gen_enabled_attr(enabled)
            plugin_section = config_markup.get_plugin_section(plugin_name)
            assert plugin_section is not None
            start_lineno = plugin_section["end"] + 1
            replace = False

        else:
            imports = []
            generated = config_generator.gen_enabled_attr(enabled)
            enabled_attr = config_markup.get_enabled_attr(plugin_name)
            assert enabled_attr is not None
            start_lineno = enabled_attr["start"]
            replace = True

        config_source = self.apply(config_source, generated, start_lineno, replace)
        config_source = self.apply(config_source, imports, 1)
        await self._save_config(config_path, config_source)

    def _gen_imports_if_needed(self, imports: List[str],
                               markup: ConfigMarkup,
                               generator: ConfigGenerator) -> List[str]:
        generated = []
        for import_name in imports:
            import_info = markup.get_import(import_name)
            if (import_info is None) or (import_info["alias"] is not None):
                generated += generator.gen_import(import_name)

        last_import = self._get_last_import(markup)
        if len(generated) > 0 and (last_import is None):
            return generated + [os.linesep]
        return generated

    def _get_last_import(self, markup: ConfigMarkup) -> Union[int, None]:
        config_section = markup.get_config_section()
        last_import = -1
        for import_info in markup.get_import_list():
            if config_section and (import_info["start"] > config_section["start"]):
                continue
            if import_info["start"] > last_import:
                last_import = import_info["start"]

        return last_import if (last_import > 0) else None

    def apply(self, config_source: str, generated: List[str], lineno: int, replace: bool = False,
              *, linesep: str = os.linesep) -> str:
        config_lines = config_source.split(linesep)

        if lineno > len(config_lines):
            for _ in range(lineno - len(config_lines)):
                config_lines.append("")

        new_config_lines = []
        for num, line in enumerate(config_lines, start=1):
            if num == lineno:
                new_config_lines.extend(generated)
                if not replace:
                    new_config_lines.append(line)
            else:
                new_config_lines.append(line)

        return linesep.join(new_config_lines)

    def _get_config_path(self) -> Path:
        path = self._config_path.absolute()
        if path == Config.path:
            return self._default_config_path
        return path

    async def _read_config(self, config_path: Path) -> str:
        try:
            with open(config_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    async def _save_config(self, config_path: Path, config_source: str) -> None:
        with open(config_path, "w") as f:
            f.write(config_source)
