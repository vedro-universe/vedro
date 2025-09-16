from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Union

from ._assert_rewriter_loader import AssertRewriterLoader

__all__ = ("AssertRewriterAdapter",)


class AssertRewriterAdapter(Loader):
    def __init__(self, orig_loader: Loader) -> None:
        self._orig_loader = orig_loader
        self._assert_rewriter_loader = AssertRewriterLoader()

    def create_module(self, spec: ModuleSpec) -> Union[ModuleType, None]:
        if create_method := getattr(self._orig_loader, "create_module", None):
            try:
                return create_method(spec)  # type: ignore
            except NotImplementedError:
                pass
        return None

    def exec_module(self, module: ModuleType) -> None:
        self._assert_rewriter_loader._exec_module(self._orig_loader, module)
