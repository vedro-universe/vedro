import importlib
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest
from baby_steps import given, then, when
from niltype import Nil
from pytest import raises

from vedro.plugins.assert_rewriter import (
    AssertRewriterAdapter,
    AssertRewriterFinder,
    CompareOperator,
    assert_,
)


@pytest.fixture
def module_search_path(tmp_path: Path) -> Path:
    sys.path.insert(0, str(tmp_path))
    try:
        yield tmp_path
    finally:
        sys.path.remove(str(tmp_path))


def test_finder_wraps_loader(tmp_path: Path):
    with given:
        pkg_dir = tmp_path / "helpers"
        pkg_dir.mkdir(exist_ok=True)

        module_path = pkg_dir / "fn.py"
        module_path.write_text(dedent('''
            def fn():
                assert 1 == 2
        '''))

        finder = AssertRewriterFinder(rewrite_paths=[pkg_dir.resolve()])
        sys_path = [str(pkg_dir)]

    with when, patch("sys.path", sys_path):
        spec = finder.find_spec("fn")

    with then:
        assert spec is not None
        assert spec.name == "fn"
        assert spec.origin == str(module_path)
        assert isinstance(spec.loader, AssertRewriterAdapter)


def test_import_rewrites_assertions(module_search_path: Path):
    with given:
        pkg_dir = module_search_path / "helpers"
        pkg_dir.mkdir(exist_ok=True)

        module_path = pkg_dir / "fn.py"
        module_path.write_text(dedent('''
            def fn():
                assert 1 == 2
        '''))

        finder = AssertRewriterFinder(rewrite_paths=[pkg_dir.resolve()])
        meta_path = [finder]

    with when, patch("sys.meta_path", meta_path), raises(BaseException) as exc:
        mod = importlib.import_module("helpers.fn")
        mod.fn()

    with then:
        assert exc.type is AssertionError
        assert assert_.get_left(exc.value) == 1
        assert assert_.get_right(exc.value) == 2
        assert assert_.get_operator(exc.value) == CompareOperator.EQUAL
        assert assert_.get_message(exc.value) == Nil
