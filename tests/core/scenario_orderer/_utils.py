from pathlib import Path

from vedro import Scenario
from vedro.core import VirtualScenario

__all__ = ("make_vscenario",)


def make_vscenario(path: str) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(path).absolute()

    return VirtualScenario(_Scenario, steps=[])
