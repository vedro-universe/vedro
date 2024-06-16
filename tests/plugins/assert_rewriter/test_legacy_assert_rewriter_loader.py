from os import linesep
from pathlib import Path
from textwrap import dedent

from baby_steps import given, then, when
from pytest import raises

from vedro.plugins.assert_rewriter import LegacyAssertRewriterLoader

from ._utils import tmp_scn_dir

__all__ = ("tmp_scn_dir",)  # pytest fixtures


async def test_load_assertion_failure(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def step(self):
                    assert 1 == 2
        '''))

        loader = LegacyAssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == "assert 1 == 2"


async def test_load_assertion_failure_with_message(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def step(self):
                    assert 1 == 2, "assertion failed"
        '''))

        loader = LegacyAssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == linesep.join([
            "assertion failed",
            "assert 1 == 2",
        ])
