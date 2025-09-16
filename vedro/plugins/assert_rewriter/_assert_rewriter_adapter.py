from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Union

from ._assert_rewriter_loader import AssertRewriterLoader

__all__ = ("AssertRewriterAdapter",)


class AssertRewriterAdapter(Loader):
    """
    Wraps an existing loader to apply assertion rewriting transparently.

    The adapter delegates module creation/execution to the original loader but
    ensures the module's source is processed by :class:`AssertRewriterLoader`
    so that ``assert`` statements produce enriched failure information.
    """

    def __init__(self, orig_loader: Loader) -> None:
        """
        Initialize the adapter with the original loader.

        :param orig_loader: The underlying loader discovered by the import
                            machinery. All operations are delegated to this loader, with
                            execution routed through the assert rewriter.
        """
        self._orig_loader = orig_loader
        self._assert_rewriter_loader = AssertRewriterLoader()

    def create_module(self, spec: ModuleSpec) -> Union[ModuleType, None]:
        """
        Create a module using the original loader if it supports it.

        If the original loader implements ``create_module``, delegate to it and
        return the resulting module. If ``create_module`` is not implemented or
        explicitly signals that it should be ignored (via
        ``NotImplementedError``), return ``None`` to let the import machinery
        create the default module object.

        :param spec: The module spec for the module being created.
        :return: A module object provided by the original loader, or ``None`` to
                 indicate default module creation.
        """
        if create_method := getattr(self._orig_loader, "create_module", None):
            try:
                return create_method(spec)  # type: ignore
            except NotImplementedError:
                pass
        return None

    def exec_module(self, module: ModuleType) -> None:
        """
        Execute the module while applying assertion rewriting.

        Delegate execution to :class:`AssertRewriterLoader`, which orchestrates
        the original loader's execution and injects the AST transformation for
        assert statements.

        :param module: The module object to execute.
        """
        self._assert_rewriter_loader._exec_module(self._orig_loader, module)
