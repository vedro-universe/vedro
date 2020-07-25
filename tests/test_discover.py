import os

import pytest

from vedro import Runner
from vedro._core import VirtualScenario

os.chdir(os.path.dirname(__file__))


@pytest.mark.asyncio
async def test_discover():
    runner = Runner()
    scenarios = runner.discover("scenarios")
    assert len(scenarios) == 1
    assert isinstance(scenarios[0], VirtualScenario)
