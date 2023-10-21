from collections import deque
from pathlib import Path
from time import monotonic_ns

import pytest

from vedro import Scenario
from vedro.core import Dispatcher, VirtualScenario
from vedro.plugins.deferrer import Deferrer, DeferrerPlugin


@pytest.fixture()
def dispatcher() -> Dispatcher:
    return Dispatcher()


@pytest.fixture()
def queue() -> deque:
    return deque()


@pytest.fixture()
def deferrer(dispatcher: Dispatcher, queue: deque) -> DeferrerPlugin:
    deferrer = DeferrerPlugin(Deferrer, queue=queue)
    deferrer.subscribe(dispatcher)
    return deferrer


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{monotonic_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])
