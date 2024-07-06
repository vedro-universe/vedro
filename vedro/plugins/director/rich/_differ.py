from difflib import Differ, SequenceMatcher
from typing import Iterator, Sequence

__all__ = ("AdvancedDiffer",)


class AdvancedDiffer(Differ):
    def compare(self, a: Sequence[str], b: Sequence[str]) -> Iterator[str]:
        return super().compare(a, b)

    def compare_unified(self, a: Sequence[str], b: Sequence[str], n: int) -> Iterator[str]:
        groups = SequenceMatcher(None, a, b).get_grouped_opcodes(n)
        for idx, group in enumerate(groups):
            if idx > 0:
                yield "..."

            for tag, i1, i2, j1, j2 in group:
                if tag == "equal":
                    g = self._dump(" ", a, i1, i2)
                elif tag == "replace":
                    g = self._fancy_replace(a, i1, i2, b, j1, j2)
                elif tag == "delete":
                    g = self._dump("-", a, i1, i2)
                elif tag == "insert":
                    g = self._dump("+", b, j1, j2)
                else:  # pragma: no cover
                    raise ValueError(f"unknown tag {tag!r}")
                yield from g

    def _dump(self, tag: str, x: Sequence[str], lo: int, hi: int) -> Iterator[str]:
        return super()._dump(tag, x, lo, hi)  # type: ignore

    def _fancy_replace(self, a: Sequence[str], alo: int, ahi: int,
                       b: Sequence[str], blo: int, bhi: int) -> Iterator[str]:
        return super()._fancy_replace(a, alo, ahi, b, blo, bhi)  # type: ignore
