from importlib.abc import Loader
from types import ModuleType

from vedro.core import ModuleFileLoader

__all__ = ("AssertRewriterModuleLoader",)


class AssertRewriterModuleLoader(ModuleFileLoader):
    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        super()._exec_module(loader, module)
