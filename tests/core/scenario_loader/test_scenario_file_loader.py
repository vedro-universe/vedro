import os
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core._scenario_loader import ScenarioFileLoader


@contextmanager
def changed_cwd(dest: Path):
    cwd = os.getcwd()
    try:
        os.chdir(dest)
        yield dest
    finally:
        os.chdir(cwd)


@pytest.mark.parametrize("name", [
    "Scenario",  # default
    "TmpScenario",  # custom name
    "Scenario_1",  # backward compatibility
    "Scenario_1_VedroScenario",  # parametrized
])
async def test_scenario_file_loader(name, *, tmp_path: Path):
    with given:
        path = tmp_path / "scenario.py"
        path.write_text(dedent(f'''
            import vedro
            class {name}(vedro.Scenario):
                pass
        '''))

        loader = ScenarioFileLoader()

    with when, changed_cwd(tmp_path) as cwd:
        scenarios = await loader.load(path.relative_to(cwd))

    with then:
        assert len(scenarios) == 1


async def test_scenarios_file_loader(tmp_path: Path):
    with given:
        path = tmp_path / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class CreateUserScenario(vedro.Scenario):
                pass
            class UpdatedUserScenario(vedro.Scenario):
                pass
        '''))

        loader = ScenarioFileLoader()

    with when, changed_cwd(tmp_path) as cwd:
        scenarios = await loader.load(path.relative_to(cwd))

    with then:
        assert len(scenarios) == 2


async def test_template_scenario_file_loader(tmp_path: Path):
    with given:
        path = tmp_path / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                @vedro.params("Bob")
                @vedro.params("Alice")
                def __init__(self, user):
                    pass
        '''))

        loader = ScenarioFileLoader()

    with when, changed_cwd(tmp_path) as cwd:
        scenarios = await loader.load(path.relative_to(cwd))

    with then:
        assert len(scenarios) == 2


async def test_scenario_file_loader_invalid_module_name(tmp_path: Path):
    with given:
        path = tmp_path / "scenario with space.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                pass
        '''))
        loader = ScenarioFileLoader()

    with when, changed_cwd(tmp_path) as cwd, raises(BaseException) as exc:
        await loader.load(path.relative_to(cwd))

    with then:
        assert exc.type is ValueError
