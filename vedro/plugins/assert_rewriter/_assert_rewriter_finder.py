from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Sequence, Tuple, Union

from ._assert_rewriter_adapter import AssertRewriterAdapter

__all__ = ("AssertRewriterFinder", "RewritePathsType",)

RewritePathsType = Union[Tuple[Path, ...], List[Path]]


class AssertRewriterFinder(MetaPathFinder):
    """
    Intercepts module discovery and injects the assert-rewriting loader.

    The finder consults Python's default :class:`PathFinder`, and for ``.py``
    modules that reside under any configured rewrite directory, it wraps the
    discovered loader with :class:`AssertRewriterAdapter`. This enables AST
    transformations that enrich assertion failures while preserving semantics.
    """

    def __init__(self, rewrite_paths: RewritePathsType) -> None:
        """
        Initialize the finder with directories to rewrite.

        :param rewrite_paths: Iterable of directories whose Python modules
                              should have their ``assert`` statements rewritten. Paths are stored
                              as a tuple in the order they are provided.
        """
        self._rewrite_paths = tuple(rewrite_paths)

    @property
    def rewrite_paths(self) -> Tuple[Path, ...]:
        """
        Return the configured rewrite directories.

        :return: A tuple of absolute or relative :class:`pathlib.Path` objects
                 that delimit where assertion rewriting is applied.
        """
        return self._rewrite_paths

    def find_spec(self, fullname: str,
                  path: Optional[Sequence[str]] = None,
                  target: Optional[ModuleType] = None) -> Optional[ModuleSpec]:
        """
        Find a module spec and wrap its loader to enable assert rewriting.

        The method defers to :class:`PathFinder` to obtain a :class:`ModuleSpec`.
        For built-in/frozen modules, modules without a location or loader, or
        non-source files (e.g., ``.pyc``, ``.so``), the spec is returned
        unchanged. For ``.py`` files located under any of ``rewrite_paths``,
        the spec's loader is wrapped with :class:`AssertRewriterAdapter`.

        :param fullname: The fully-qualified module name being imported.
        :param path: The package path for submodule imports, as provided by the
                     import system. Often ``None`` for top-level imports.
        :param target: The module object that is the target of a reload, when
                       applicable. Usually ``None`` for regular imports.
        :return: A possibly modified :class:`ModuleSpec` if the module is found,
                 or ``None`` if the module cannot be found.
        """
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
