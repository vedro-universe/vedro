import re
from typing import Any, Generator, Iterable, List, Optional, Tuple

from niltype import Nil, Nilable
from rich.console import Console, ConsoleOptions, ConsoleRenderable, Group, RenderResult
from rich.padding import Padding
from rich.pretty import pretty_repr
from rich.style import Style
from rich.text import Text

from ._differ import AdvancedDiffer

__all__ = ("PrettyDiff",)


class PrettyDiff:
    def __init__(self, left: Any, right: Nilable[Any] = Nil, operator: Nilable[str] = Nil, *,
                 max_context_lines: Optional[int] = None,
                 max_nested_level: Optional[int] = None,
                 max_container_length: Optional[int] = None,
                 expand_containers: bool = False) -> None:
        self._left = left
        self._right = right
        self._operator = operator
        self._max_context_lines = max_context_lines
        self._max_nested_level = max_nested_level
        self._max_container_length = max_container_length
        self._expand_containers = expand_containers

        self._differ = AdvancedDiffer()

        self._color_red = "red"
        self._color_green = "green"
        self._color_grey = "grey50"

        self._indent_size = 4
        self._padding = (0, 4)

    def _get_header(self) -> ConsoleRenderable:
        if self._operator is Nil:
            return (
                Text(">>> assert ", style=Style(bold=True)) +
                Text("actual", style=Style(color=self._color_red, bold=True))
            )

        left, right = self._get_comparison_labels(self._operator)
        return (
            Text(">>> assert ", style=Style(bold=True)) +
            Text(f"{left}", style=Style(color=self._color_red, bold=True)) +
            Text(f" {self._operator} ", style=Style(bold=True)) +
            Text(f"{right}", style=Style(color=self._color_green, bold=True))
        )

    def _get_comparison_labels(self, operator: str) -> Tuple[str, str]:
        if operator in {"<", "<=", ">", ">="}:
            return "left", "right"
        elif operator in {"in", "not in"}:
            return "member", "container"
        else:
            return "actual", "expected"

    def _pretty_repr(self, value: Any) -> str:
        return pretty_repr(value,
                           indent_size=self._indent_size,
                           max_length=self._max_container_length,
                           max_depth=self._max_nested_level,
                           expand_all=self._expand_containers)

    def _get_left(self) -> ConsoleRenderable:
        return Text(self._pretty_repr(self._left), style=Style(color=self._color_red))

    def _get_right(self) -> ConsoleRenderable:
        return Text(self._pretty_repr(self._right), style=Style(color=self._color_green))

    def _get_diff(self) -> ConsoleRenderable:
        diff = list(self._compare(self._left, self._right))
        colored_diff = self._color_diff(diff)
        return Group(*colored_diff)

    def _compare(self, left: Any, right: Any) -> Generator[str, None, None]:
        if self._max_context_lines is not None:
            yield from self._differ.compare_unified(self._format(right), self._format(left),
                                                    self._max_context_lines)
        else:
            yield from self._differ.compare(self._format(right), self._format(left))

    def _format(self, val: Any) -> List[str]:
        formatted = pretty_repr(val, indent_size=self._indent_size, expand_all=True)
        return formatted.splitlines()

    def _color_diff(self, diff: Iterable[str]) -> List[Text]:
        colored_diff = []

        for line, next_line in self._enumerate_next(diff):
            if line.startswith("?"):
                continue

            styled_text = Text(line)

            if line.startswith("-"):
                styled_text.stylize(self._color_green)
                if next_line and next_line.startswith("?"):
                    next_line = next_line.replace("?", " ", 1)
                    for start, end in self._find_non_space_sequences(next_line):
                        styled_text.stylize(f"black on {self._color_green}", start, end)
            elif line.startswith("+"):
                styled_text.stylize(self._color_red)
                if next_line and next_line.startswith("?"):
                    next_line = next_line.replace("?", " ", 1)
                    for start, end in self._find_non_space_sequences(next_line):
                        styled_text.stylize(f"black on {self._color_red}", start, end)
            else:
                styled_text.stylize(self._color_grey)

            colored_diff.append(styled_text)

        return colored_diff

    def _find_non_space_sequences(self, s: str) -> Generator[Tuple[int, int], None, None]:
        for m in re.finditer(r'\S+', s):
            yield m.start(), m.end()

    def _enumerate_next(
        self,
        iterable: Iterable[str]
    ) -> Generator[Tuple[str, Optional[str]], None, None]:
        iterator = iter(iterable)
        current_line = next(iterator, "")
        for next_line in iterator:
            yield current_line, next_line
            current_line = next_line
        yield current_line, None

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield self._get_header()
        if self._operator == "==":
            yield Padding(self._get_diff(), self._padding)
        else:
            yield Padding(self._get_left(), self._padding)
            if self._right is not Nil:
                yield Padding(self._get_right(), self._padding)
