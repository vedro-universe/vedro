from importlib.abc import Loader
from types import ModuleType
from typing import Any

from vedro.core import ModuleFileLoader

__all__ = ("AssertRewriterModuleLoader",)

RewriterType = Any


class AssertRewriterModuleLoader(ModuleFileLoader):
    def __init__(self, *, validate_module_names: bool = False, **kwargs: Any) -> None:
        super().__init__(validate_module_names=validate_module_names, **kwargs)

        try:
            from dessert import AssertionRewritingHook  # type: ignore
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "Package 'dessert' is not found, install it via 'pip install dessert'")
        else:
            self._rewriter = AssertionRewritingHook()

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        self._rewriter.exec_module(module)
