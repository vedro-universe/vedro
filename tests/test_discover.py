import pytest

from vedro import Runner
from vedro._core import ScenarioDiscoverer, VirtualScenario
from vedro._core._scenario_finder import ScenarioFileFinder
from vedro._core._scenario_finder._file_filters import ExtFilter
from vedro._core._scenario_loader import ScenarioFileLoader


@pytest.mark.asyncio
async def test_discover():
    finder = ScenarioFileFinder(ExtFilter(only=["py"]))
    loader = ScenarioFileLoader()
    discoverer = ScenarioDiscoverer(finder, loader)
    runner = Runner(discoverer)

    scenarios = await runner.discover("tests/scenarios")

    assert len(scenarios) == 1
    assert isinstance(scenarios[0], VirtualScenario)
