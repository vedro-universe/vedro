import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock, MagicMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock, MagicMock

from pathlib import Path
from unittest.mock import Mock, call

import pytest

from vedro import Scenario
from vedro.core import (
    MultiScenarioDiscoverer,
    ScenarioFinder,
    ScenarioLoader,
    ScenarioOrderer,
    VirtualScenario,
)


def make_finder(files):
    iterator = MagicMock()
    iterator.__aiter__.return_value = iter(files)
    return Mock(ScenarioFinder, find=Mock(return_value=iterator))


def make_loader(scenarios):
    return Mock(ScenarioLoader, load=AsyncMock(side_effect=iter(scenarios)))


def make_orderer():
    async def sort(scenarios):
        return scenarios
    return Mock(ScenarioOrderer, sort=sort)


def create_scenario(filename):
    return Mock(Scenario, __file__=filename)


@pytest.mark.asyncio
async def test_scenario_discoverer():
    root = Path("/tmp")
    scenario1 = create_scenario(root / "scenario-1.py")
    scenario3 = create_scenario(root / "folder" / "scenario-2.py")
    scenario4 = create_scenario(root / "folder" / "scenario-10.py")
    tree = {
        scenario1.__file__: [scenario1],
        root / "scenario-2.py": [],
        scenario3.__file__: [scenario3, scenario4],
    }
    finder_ = make_finder(tree.keys())
    loader_ = make_loader(tree.values())
    orderer_ = make_orderer()
    discoverer = MultiScenarioDiscoverer(finder_, loader_, orderer_)

    scenarios = await discoverer.discover(root)
    assert scenarios == [
        VirtualScenario(scenario1, []),
        VirtualScenario(scenario3, []),
        VirtualScenario(scenario4, []),
    ]
    assert finder_.mock_calls == [call.find(root)]
    assert loader_.mock_calls == [call.load(f) for f in tree.keys()]
