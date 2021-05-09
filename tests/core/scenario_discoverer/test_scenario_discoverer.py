from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, call

import pytest

from vedro import Scenario
from vedro._core._scenario_discoverer import ScenarioDiscoverer
from vedro._core._scenario_finder import ScenarioFinder
from vedro._core._scenario_loader import ScenarioLoader


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


@pytest.mark.asyncio
async def test_scenario_discoverer(*, finder_factory, loader_factory):
    root = Path("/tmp")
    tree = {
        root / "scenario-1.py": [Mock(Scenario)],
        root / "scenario-2.py": [],
        root / "folder" / "scenario-3.py": [Mock(Scenario), Mock(Scenario)],
    }
    finder_ = finder_factory(tree.keys())
    loader_ = loader_factory(tree.values())
    discoverer = ScenarioDiscoverer(finder_, loader_)

    scenarios = await discoverer.discover(root)

    assert scenarios == sum(tree.values(), [])
    assert finder_.mock_calls == [call.find(root)]
    assert loader_.mock_calls == [call.load(f) for f in tree.keys()]
