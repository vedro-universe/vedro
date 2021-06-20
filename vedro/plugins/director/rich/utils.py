import json
import os
import shutil
from typing import Any, Dict, Generator, Tuple

from rich.console import Console

__all__ = ("make_console", "get_terminal_size", "format_scope",)


def get_terminal_size(default_columns: int = 80, default_lines: int = 24) -> os.terminal_size:
    columns, lines = shutil.get_terminal_size()
    # Fix columns=0 lines=0 in Pycharm
    if columns <= 0:
        columns = default_columns
    if lines <= 0:
        lines = default_lines
    return os.terminal_size((columns, lines))


def make_console(**options: Any) -> Console:
    size = get_terminal_size()
    default_options = dict(
        highlight=False,
        force_terminal=True,
        markup=False,
        emoji=False,
        width=size.columns,
        height=size.lines,
    )
    return Console(**{**default_options, **options})  # type: ignore


def format_scope(scope: Dict[Any, Any]) -> Generator[Tuple[str, str], None, None]:
    for key, val in scope.items():
        try:
            val_repr = json.dumps(val, ensure_ascii=False, indent=4)
        except:  # noqa: E722
            val_repr = repr(val)
        yield str(key), val_repr
