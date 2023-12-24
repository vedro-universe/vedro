import os
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent

from baby_steps import given, then, when
from dessert import AssertionRewritingHook
from pytest import raises

from vedro.plugins.assert_rewriter import ScenarioAssertRewriterLoader


@contextmanager
def changed_cwd(dest: Path):
    cwd = os.getcwd()
    try:
        os.chdir(dest)
        yield dest
    finally:
        os.chdir(cwd)


async def test_load(tmp_path: Path):
    with given, changed_cwd(tmp_path) as cwd:
        path = tmp_path / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def then(self):
                    assert 1 == 2
        '''))

        loader = ScenarioAssertRewriterLoader(AssertionRewritingHook())
        scenarios = await loader.load(path.relative_to(cwd))
        scenario = scenarios[0]()

    with when, raises(BaseException) as exception:
        scenario.then()

    with then:
        assert exception.type is AssertionError
        assert str(exception.value) == "assert 1 == 2"
