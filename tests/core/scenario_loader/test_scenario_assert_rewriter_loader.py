from pathlib import Path
from textwrap import dedent

import pytest

from vedro._core._scenario_loader import ScenarioAssertRewriterLoader


@pytest.mark.asyncio
async def test_scenario_assert_rewriter_loader(tmp_path: Path):
    path = tmp_path / "scenario.py"
    path.write_text(dedent('''
        import vedro
        class Scenario(vedro.Scenario):
            def then(self):
                assert 1 == 2
    '''))

    loader = ScenarioAssertRewriterLoader()
    scenarios = await loader.load(path)
    assert len(scenarios) == 1

    scenario = scenarios[0]()
    with pytest.raises(AssertionError) as exception:
        scenario.then()

    assert str(exception.value) == "assert 1 == 2"
