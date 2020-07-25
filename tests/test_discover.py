import pytest

from vedro import Runner
from vedro._core import VirtualScenario


@pytest.mark.asyncio
async def test_discover():
    runner = Runner()
    scenarios = runner.discover("tests/scenarios")
    assert len(scenarios) == 1
    assert isinstance(scenarios[0], VirtualScenario)
