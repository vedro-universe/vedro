import difflib
import json
import re
from typing import Any, Generator, Iterable, List, Optional, Tuple

from rich.console import Group
from rich.padding import Padding
from rich.text import Text


def _find_non_space_sequences(s: str) -> Generator[Tuple[int, int], None, None]:
    for m in re.finditer(r'\S+', s):
        yield m.start(), m.end()


def _enumerate_next(iterable: Iterable[str]) -> Generator[Tuple[str, Optional[str]], None, None]:
    iterator = iter(iterable)
    current_line = next(iterator, "")
    for next_line in iterator:
        yield current_line, next_line
        current_line = next_line
    yield current_line, None


def _format(val: Any) -> List[str]:
    return json.dumps(val, indent=2, ensure_ascii=False, sort_keys=True, default=repr).splitlines()


def _color_diff(diff: Iterable[str]) -> List[Text]:
    colored_diff = []

    for line, next_line in _enumerate_next(diff):
        if line.startswith("?"):
            continue

        styled_text = Text(line)

        if line.startswith("-"):
            styled_text.stylize("green")
            if next_line and next_line.startswith("?"):
                next_line = next_line.replace("?", " ", 1)
                for start, end in _find_non_space_sequences(next_line):
                    styled_text.stylize("black on green", start, end)
        elif line.startswith("+"):
            styled_text.stylize("red")
            if next_line and next_line.startswith("?"):
                next_line = next_line.replace("?", " ", 1)
                for start, end in _find_non_space_sequences(next_line):
                    styled_text.stylize("black on red", start, end)
        else:
            styled_text.stylize("grey50")

        colored_diff.append(styled_text)

    return colored_diff


def _compare(actual: Any, expected: Any) -> Generator[str, None, None]:
    differ = difflib.Differ()
    yield from differ.compare(_format(actual), _format(expected))


def pretty_diff(actual: Any, expected: Any) -> Padding:
    diff = _compare(expected, actual)
    colored_diff = _color_diff(diff)
    renderable = Group(*colored_diff)
    return Padding(renderable, (0, 2))
