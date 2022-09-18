import random
from contextlib import contextmanager
from pathlib import Path

import pytest
from baby_steps import given, then, when

from vedro import Scenario
from vedro.core import VirtualScenario
from vedro.plugins.orderer import RandomOrderer


@pytest.fixture()
def orderer():
    return RandomOrderer()


@contextmanager
def seeded(seed: str):
    state = random.getstate()
    random.seed(seed)
    yield
    random.setstate(state)


def make_vscenario(path: str) -> VirtualScenario:
    class _Scenario(Scenario):
        __file__ = Path(path).absolute()

    return VirtualScenario(_Scenario, steps=[])


@pytest.mark.asyncio
async def test_sort_no_scenarios(*, orderer: RandomOrderer):
    with given:
        scenarios = []

    with when:
        res = await orderer.sort(scenarios)

    with then:
        assert res == []
        assert scenarios == []


@pytest.mark.asyncio
async def test_sort_scenarios(*, orderer: RandomOrderer):
    with given:
        orig_scenarios = {path: make_vscenario(path) for path in [
            "scenarios/directory/scn.py",
            "scenarios/dir1/scn1.py",
            "scenarios/dir1/scn2.py",
            "scenarios/dir2/scn2.py",
            "scenarios/scn2.py",
            "scenarios/scn10.py",
        ]}
        scenarios = list(orig_scenarios.values())

    with when, seeded("c104234e-c400-4648-aa3f-5442ce5ed1fc"):
        res = await orderer.sort(scenarios)

    with then:
        assert res == [
            orig_scenarios["scenarios/directory/scn.py"],
            orig_scenarios["scenarios/dir1/scn2.py"],
            orig_scenarios["scenarios/scn10.py"],
            orig_scenarios["scenarios/scn2.py"],
            orig_scenarios["scenarios/dir1/scn1.py"],
            orig_scenarios["scenarios/dir2/scn2.py"],
        ]
        assert scenarios == list(orig_scenarios.values())
