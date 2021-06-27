from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when

from vedro._core._scenario_loader import ScenarioFileLoader


@pytest.mark.asyncio
async def test_scenario_file_loader(tmp_path: Path):
    with given:
        path = tmp_path / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                pass
        '''))

        loader = ScenarioFileLoader()

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 1


@pytest.mark.asyncio
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

    with when:
        scenarios = await loader.load(path)

    with then:
        assert len(scenarios) == 2
