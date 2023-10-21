import pytest
from baby_steps import given, then, when

from vedro.plugins.orderer import RandomOrderer

from ._utils import make_vscenario, seeded


@pytest.fixture()
def orderer() -> RandomOrderer:
    return RandomOrderer()


async def test_sort_no_scenarios(*, orderer: RandomOrderer):
    with given:
        scenarios = []

    with when:
        res = await orderer.sort(scenarios)

    with then:
        assert res == []
        assert scenarios == []


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
