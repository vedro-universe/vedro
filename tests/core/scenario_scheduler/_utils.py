from pathlib import Path
from time import perf_counter_ns
from typing import Any, AsyncIterable, Iterator

from vedro import Scenario
from vedro.core import ScenarioResult, VirtualScenario


def make_vscenario() -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(f"scenario_{perf_counter_ns()}.py").absolute()

    return VirtualScenario(_Scenario, steps=[])


def make_scenario_result() -> ScenarioResult:
    return ScenarioResult(make_vscenario())


async def aenumerate(iterable: AsyncIterable, start: int = 0) -> Iterator[Any]:
    idx = start
    async for x in iterable:
        yield idx, x
        idx += 1
