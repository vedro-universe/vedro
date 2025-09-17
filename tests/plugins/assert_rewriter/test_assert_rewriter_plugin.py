from pathlib import Path
from unittest.mock import patch, sentinel

import pytest
from baby_steps import given, then, when
from pytest import raises

from vedro.core import Dispatcher
from vedro.plugins.assert_rewriter import (
    AssertRewriter,
    AssertRewriterFinder,
    AssertRewriterLoader,
    AssertRewriterPlugin,
    LegacyAssertRewriterLoader,
)

from ._utils import (
    assert_rewriter_plugin,
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    make_config,
    tmp_scn_dir,
)

__all__ = ("dispatcher", "assert_rewriter_plugin", "tmp_scn_dir",)  # pytest fixtures


@pytest.mark.usefixtures(assert_rewriter_plugin.__name__)
async def test_registers_default_loader(*, dispatcher: Dispatcher):
    with given:
        config = make_config()
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert isinstance(config.Registry.ModuleLoader(), AssertRewriterLoader)


@pytest.mark.usefixtures(assert_rewriter_plugin.__name__)
async def test_registers_legacy_loader(*, dispatcher: Dispatcher):
    with given:
        config = make_config()
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher, legacy_assertions=True)

    with then:
        assert isinstance(config.Registry.ModuleLoader(), LegacyAssertRewriterLoader)


async def test_no_finder_when_paths_empty(*, dispatcher: Dispatcher):
    with given:
        class _AssertRewriter(AssertRewriter):
            assert_rewrite_paths = []

        assert_rewriter_plugin = AssertRewriterPlugin(_AssertRewriter)
        assert_rewriter_plugin.subscribe(dispatcher)

        config = make_config()
        await fire_config_loaded_event(dispatcher, config)

    with when, patch("sys.meta_path", []) as patched:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert len(patched) == 0


async def test_adds_finder_to_meta_path(*, tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        rewrite_path = Path("./helpers")
        rewrite_path.mkdir(exist_ok=True)

        class _AssertRewriter(AssertRewriter):
            assert_rewrite_paths = [rewrite_path]

        assert_rewriter_plugin = AssertRewriterPlugin(_AssertRewriter)
        assert_rewriter_plugin.subscribe(dispatcher)

        config = make_config(project_dir_=tmp_scn_dir.parent)
        await fire_config_loaded_event(dispatcher, config)

        existing_finder = sentinel.finder

    with when, patch("sys.meta_path", [existing_finder]) as patched:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert len(patched) == 2
        assert isinstance(patched[0], AssertRewriterFinder)
        assert patched[1] is existing_finder


async def test_raises_for_invalid_path(*, tmp_scn_dir: Path, dispatcher: Dispatcher):
    with given:
        rewrite_path = Path("./helpers")

        class _AssertRewriter(AssertRewriter):
            assert_rewrite_paths = [rewrite_path]

        assert_rewriter_plugin = AssertRewriterPlugin(_AssertRewriter)
        assert_rewriter_plugin.subscribe(dispatcher)

        config = make_config(project_dir_=tmp_scn_dir.parent)
        await fire_config_loaded_event(dispatcher, config)

    with when, patch("sys.meta_path", []), raises(BaseException) as exc:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert exc.type is ValueError
