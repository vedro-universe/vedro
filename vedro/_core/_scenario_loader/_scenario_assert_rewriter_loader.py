from importlib.abc import Loader
from types import ModuleType
from typing import Any, Optional

from dessert import AssertionRewritingHook  # type: ignore

from ._scenario_file_loader import ScenarioFileLoader

__all__ = ("ScenarioAssertRewriterLoader",)

RewriterType = Any


class ScenarioAssertRewriterLoader(ScenarioFileLoader):
    def __init__(self, rewriter: Optional[RewriterType] = None) -> None:
        self._rewriter = rewriter or AssertionRewritingHook()

    def _exec_module(self, loader: Loader, module: ModuleType) -> None:
        self._rewriter.exec_module(module)
