from importlib.abc import Loader
from types import ModuleType
from typing import Any

from vedro.core import ScenarioFileLoader

__all__ = ("ScenarioAssertRewriterLoader",)

RewriterType = Any


class ScenarioAssertRewriterLoader(ScenarioFileLoader):
    def __init__(self, rewriter: RewriterType) -> None:
        super().__init__()
        self._rewriter = rewriter

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        self._rewriter.exec_module(module)
