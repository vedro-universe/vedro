import ast
import token
from io import BytesIO
from tokenize import tokenize
from typing import Dict, Union

from ._config_markup import (
    ConfigMarkup,
    ConfigSectionType,
    EnabledAttrType,
    ImportType,
    PluginListSectionType,
    PluginSectionType,
)

__all__ = ("ConfigParser",)


class ConfigParser:
    async def parse(self, config_source: str, *, default_indent: str = " " * 4) -> ConfigMarkup:
        config_ast = ast.parse(config_source)
        imports = self._parse_imports(config_ast)
        config_section = self._parse_config_section(config_ast)
        indent = self._get_indent(config_source, default_indent)
        return ConfigMarkup(config_section, imports, indent)

    def _get_indent(self, config_source: str, default_indent: str) -> str:
        stream = BytesIO(config_source.encode())
        indents = [tok.string for tok in tokenize(stream.readline) if tok.type == token.INDENT]
        return min(indents, key=len) if indents else default_indent

    def _parse_imports(self, st: ast.AST) -> Dict[str, ImportType]:
        res: Dict[str, ImportType] = {}
        for node in ast.iter_child_nodes(st):
            if not isinstance(node, ast.Import):
                continue
            end_lineno = getattr(node, "end_lineno", 0)
            for alias in node.names:
                res[alias.name] = {
                    "alias": alias.asname,
                    "start": node.lineno,
                    "end": end_lineno,
                    "offset": node.col_offset,
                }
        return res

    def _parse_config_section(self, st: ast.AST) -> Union[ConfigSectionType, None]:
        for node in ast.iter_child_nodes(st):
            if isinstance(node, ast.ClassDef) and (node.name == "Config"):
                end_lineno = getattr(node, "end_lineno", 0)
                return {
                    "plugins": self._parse_plugin_list_section(node),
                    "start": node.lineno,
                    "end": end_lineno,
                    "offset": node.col_offset,
                }
        return None

    def _parse_plugin_list_section(self, st: ast.ClassDef) -> Union[PluginListSectionType, None]:
        for node in ast.iter_child_nodes(st):
            if isinstance(node, ast.ClassDef) and (node.name == "Plugins"):
                end_lineno = getattr(node, "end_lineno", 0)
                return {
                    "start": node.lineno,
                    "end": end_lineno,
                    "offset": node.col_offset,
                    "children": self._parse_plugin_section(node),
                }
        return None

    def _parse_plugin_section(self, st: ast.ClassDef) -> Dict[str, PluginSectionType]:
        res: Dict[str, PluginSectionType] = {}
        for node in ast.iter_child_nodes(st):
            if isinstance(node, ast.ClassDef):
                end_lineno = getattr(node, "end_lineno", 0)
                res[node.name] = {
                    "start": node.lineno,
                    "end": end_lineno,
                    "offset": node.col_offset,
                    "enabled": self._parse_enabled_attr(node),
                }
        return res

    def _parse_enabled_attr(self, st: ast.ClassDef) -> Union[EnabledAttrType, None]:
        for node in ast.iter_child_nodes(st):
            if not isinstance(node, ast.Assign):
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and (target.id == "enabled"):
                end_lineno = getattr(node, "end_lineno", 0)
                return {
                    "start": node.lineno,
                    "end": end_lineno,
                    "offset": node.col_offset,
                }
        return None
