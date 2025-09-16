from pathlib import Path
from textwrap import dedent

from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.plugins.assert_rewriter import AssertRewriterLoader, CompareOperator, assert_

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

        loader = AssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == ""

        assert assert_.get_left(exc.value) == 1
        assert assert_.get_right(exc.value) == 2
        assert assert_.get_operator(exc.value) == CompareOperator.EQUAL
        assert assert_.get_message(exc.value) == Nil


async def test_load_assertion_failure_with_message(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            import vedro
            class Scenario(vedro.Scenario):
                def step(self):
                    assert 1 == 2, "assertion failed"
        '''))

        loader = AssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == "assertion failed"

        assert assert_.get_left(exc.value) == 1
        assert assert_.get_right(exc.value) == 2
        assert assert_.get_operator(exc.value) == CompareOperator.EQUAL
        assert assert_.get_message(exc.value) == "assertion failed"


async def test_load_empty_scenario_file(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text("")

        loader = AssertRewriterLoader()

    with when:
        module = await loader.load(path)

    with then:
        assert module is not None


async def test_load_non_existent_scenario_file(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"

        loader = AssertRewriterLoader()

    with when, raises(Exception) as exc:
        await loader.load(path)

    with then:
        assert exc.type is FileNotFoundError


async def test_load_assertion_failure_with_future_annotations(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            from __future__ import annotations

            import vedro
            class Scenario(vedro.Scenario):
                def step(self):
                    assert 1 == 2
        '''))

        loader = AssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == ""


async def test_load_assertion_failure_with_docstring_and_future_annotations(tmp_scn_dir: Path):
    with given:
        path = tmp_scn_dir / "scenario.py"
        path.write_text(dedent('''
            """
            Module docstring
            """
            from __future__ import annotations

            import vedro
            class Scenario(vedro.Scenario):
                def step(self):
                    assert 1 == 2
        '''))

        loader = AssertRewriterLoader()
        module = await loader.load(path)
        scenario = module.Scenario()

    with when, raises(BaseException) as exc:
        scenario.step()

    with then:
        assert exc.type is AssertionError
        assert str(exc.value) == ""
