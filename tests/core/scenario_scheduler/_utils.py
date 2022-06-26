from typing import Any, AsyncIterable, Iterator
from unittest.mock import Mock

from vedro.core import ScenarioResult, VirtualScenario


def make_virtual_scenario() -> Mock:
    return Mock(spec=VirtualScenario)


def make_scenario_result():
    return ScenarioResult(Mock(spec=VirtualScenario))


async def aenumerate(iterable: AsyncIterable, start: int = 0) -> Iterator[Any]:
    idx = start
    async for x in iterable:
        yield idx, x
        idx += 1
