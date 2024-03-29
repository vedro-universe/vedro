import os
from pathlib import Path
from textwrap import dedent

import pytest
from baby_steps import given, then, when
from dessert import AssertionRewritingHook
from pytest import raises

from vedro.plugins.assert_rewriter import ScenarioAssertRewriterLoader


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


async def test_load(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def then(self):
                    assert 1 == 2
        '''))

        loader = ScenarioAssertRewriterLoader(AssertionRewritingHook())
        scenarios = await loader.load(path)
        scenario = scenarios[0]()

    with when, raises(BaseException) as exception:
        scenario.then()

    with then:
        assert exception.type is AssertionError
        assert str(exception.value) == "assert 1 == 2"
