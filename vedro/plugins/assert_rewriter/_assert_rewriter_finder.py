from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Sequence, Tuple, Union

from ._assert_rewriter_adapter import AssertRewriterAdapter

__all__ = ("AssertRewriterFinder", "RewritePathsType",)

RewritePathsType = Union[Tuple[Path, ...], List[Path]]


class AssertRewriterFinder(MetaPathFinder):
    def __init__(self, rewrite_paths: RewritePathsType) -> None:
        self._rewrite_paths = tuple(rewrite_paths)

    @property
    def rewrite_paths(self) -> Tuple[Path, ...]:
        return self._rewrite_paths

    def find_spec(self, fullname: str,
                  path: Optional[Sequence[str]] = None,
                  target: Optional[ModuleType] = None) -> Optional[ModuleSpec]:
        # Use PathFinder as a class, not instance
        spec = PathFinder.find_spec(fullname, path, target)

        # Early returns for specs that shouldn't be modified
        if not spec:
            return None

        # Check if module has a physical location
        if not getattr(spec, 'has_location', False):
            return spec

        # Skip special origins
        if spec.origin in (None, "built-in", "frozen"):
            return spec

        # Ensure loader exists before wrapping
        if not spec.loader:
            return spec

        # Only rewrite Python source files
        try:
            module_path = Path(spec.origin).resolve()  # type: ignore
        except (ValueError, OSError):
            # Can't resolve path, skip rewriting
            return spec

        if module_path.suffix != '.py':
            # Skip .pyc, .pyd, .so, etc.
            return spec

        # Check if module is under any of the rewrite paths
        for rewrite_path in self._rewrite_paths:
            if self._is_relative_to(module_path, rewrite_path):
                spec.loader = AssertRewriterAdapter(spec.loader)
                break

        return spec

    def _is_relative_to(self, path: Path, parent: Path) -> bool:
        """
        Check if the given path is relative to the specified parent directory.

        :param path: The path to check.
        :param parent: The parent directory to check against.
        :return: True if the path is relative to the parent directory, False otherwise.
        """
        try:
            path.relative_to(parent)
        except ValueError:
            return False
        else:
            return True
