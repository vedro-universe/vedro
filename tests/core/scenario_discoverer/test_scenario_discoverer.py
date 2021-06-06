from pathlib import Path
from unittest.mock import AsyncMock, call, MagicMock, Mock

import pytest

from vedro import Scenario
from vedro._core._scenario_discoverer import ScenarioDiscoverer
from vedro._core._scenario_finder import ScenarioFinder
from vedro._core._scenario_loader import ScenarioLoader
from vedro._core._virtual_scenario import VirtualScenario


@pytest.fixture()
def finder_factory():
    def _factory(files):
        iterator = MagicMock()
        iterator.__aiter__.return_value = iter(files)
        return Mock(ScenarioFinder, find=Mock(return_value=iterator))
    return _factory


@pytest.fixture()
def loader_factory():
    def _factory(scenarios):
        return Mock(ScenarioLoader, load=AsyncMock(side_effect=iter(scenarios)))
    return _factory


def create_scenario(filename):
    return Mock(Scenario, __file__=filename)


@pytest.mark.asyncio
async def test_scenario_discoverer(*, finder_factory, loader_factory):
    root = Path("/tmp")
    scenario1 = create_scenario(root / "scenario-1.py")
    scenario3 = create_scenario(root / "folder" / "scenario-3.py")
    scenario4 = create_scenario(root / "folder" / "scenario-4.py")
    tree = {
        scenario1.__file__: [scenario1],
        root / "scenario-2.py": [],
        scenario3.__file__: [scenario3, scenario4],
    }
    finder_ = finder_factory(tree.keys())
    loader_ = loader_factory(tree.values())
    discoverer = ScenarioDiscoverer(finder_, loader_)

    scenarios = await discoverer.discover(root)
    assert scenarios == [
        VirtualScenario(scenario1, []),
        VirtualScenario(scenario3, []),
        VirtualScenario(scenario4, []),
    ]
    assert finder_.mock_calls == [call.find(root)]
    assert loader_.mock_calls == [call.load(f) for f in tree.keys()]
