import os
from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import ScenarioFileLoader


@pytest.fixture()
def tmp_scn_dir(tmp_path: Path) -> Path:
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        scn_dir = tmp_path / "scenarios/"
        scn_dir.mkdir(exist_ok=True)
        yield scn_dir.relative_to(tmp_path)
    finally:
        os.chdir(cwd)


@pytest.mark.parametrize("name", [
    "Scenario",  # default
    "TmpScenario",  # custom name (prefix)
    "ScenarioTmp",  # custom name (suffix)
    "Scenario_1",  # backward compatibility
    "Scenario_1_VedroScenario",  # parametrized
])
async def test_scenario_file_loader(name, *, tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent(f'''
            import vedro
            class {name}(vedro.Scenario):
                pass
        '''))

        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 1


async def test_scenarios_file_loader_multiple_scenarios(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class CreateUserScenario(vedro.Scenario):
                pass
            class UpdatedUserScenario(vedro.Scenario):
                pass
        '''))

        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 2


async def test_template_scenario_file_loader_with_params(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                @vedro.params("Bob")
                @vedro.params("Alice")
                def __init__(self, user):
                    pass
        '''))

        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 2


async def test_scenario_file_loader_without_inheriting_scenario(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            class Scenario:
                pass
        '''))
        loader = ScenarioFileLoader()

    with when, raises(BaseException) as exc:
        await loader.load(path)

    with then:
        assert exc.type is TypeError
        assert str(exc.value) == "'scenarios.scenario.Scenario' must inherit from 'vedro.Scenario'"


async def test_scenario_file_loader_without_scenarios(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text("")
        loader = ScenarioFileLoader()

    with when, raises(BaseException) as exc:
        await loader.load(path)

    with then:
        assert exc.type is ValueError
        assert str(exc.value) == (
            "No Vedro scenarios found in the module at 'scenarios/scenario.py'. "
            "Ensure the module contains at least one subclass of 'vedro.Scenario'"
        )


async def test_scenario_file_loader_with_other_classes(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class User:
                pass
            class Scenario(vedro.Scenario):
                pass
        '''))
        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 1


async def test_scenario_file_loader_with_other_functions(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class UserScenario(vedro.Scenario):
                pass
            def Scenario():
                pass
        '''))
        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 1
