import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, call

import pytest
from baby_steps import given, then, when
from pytest import raises

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


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        Path("./scenarios").mkdir(exist_ok=True)
        yield tmp_path
    finally:
        os.chdir(cwd)


async def test_scenario_discoverer(tmp_dir: Path):
    with given:
        root = Path("scenarios")
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

    with when:
        scenarios = await discoverer.discover(tmp_dir, project_dir=tmp_dir)

    with then("scenarios discovered correctly"):
        assert scenarios == [
            VirtualScenario(scenario1, [], project_dir=tmp_dir),
            VirtualScenario(scenario3, [], project_dir=tmp_dir),
            VirtualScenario(scenario4, [], project_dir=tmp_dir),
        ]

    with then("finder and loader called with correct arguments"):
        assert finder_.mock_calls == [call.find(tmp_dir)]
        assert loader_.mock_calls == [call.load(f) for f in tree.keys()]


async def test_scenario_discoverer_orderer_changes_count(tmp_dir: Path):
    with given:
        root = Path("scenarios")
        scenario1 = create_scenario(root / "scenario-1.py")
        scenario2 = create_scenario(root / "scenario-2.py")
        tree = {
            scenario1.__file__: [scenario1],
            scenario2.__file__: [scenario2],
        }
        finder_ = make_finder(tree.keys())
        loader_ = make_loader(tree.values())

        class ScenarioOrdererWithChange(ScenarioOrderer):
            async def sort(self, scenarios):
                return scenarios[:1]

        discoverer = MultiScenarioDiscoverer(finder_, loader_, ScenarioOrdererWithChange())

    with when, raises(ValueError) as exc_info:
        await discoverer.discover(tmp_dir, project_dir=tmp_dir)

    with then:
        assert str(exc_info.value) == (
            "The scenario orderer returned 1 scenario(s), but 2 scenario(s) were discovered. "
            "Please ensure the orderer only reorders scenarios without adding or removing any"
        )
