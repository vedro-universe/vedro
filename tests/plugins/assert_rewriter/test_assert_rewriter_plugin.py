import pytest
from baby_steps import given, then, when

from vedro.core import Dispatcher
from vedro.plugins.assert_rewriter import AssertRewriterLoader, LegacyAssertRewriterLoader

from ._utils import (
    assert_rewriter_plugin,
    dispatcher,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    make_config,
)

__all__ = ("dispatcher", "assert_rewriter_plugin",)  # pytest fixtures


@pytest.mark.usefixtures(assert_rewriter_plugin.__name__)
async def test_registers_default_assert_rewriter_loader(*, dispatcher: Dispatcher):
    with given:
        config = make_config()
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher)

    with then:
        assert isinstance(config.Registry.ModuleLoader(), AssertRewriterLoader)


@pytest.mark.usefixtures(assert_rewriter_plugin.__name__)
async def test_registers_legacy_assert_rewriter_loader(*, dispatcher: Dispatcher):
    with given:
        config = make_config()
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher, legacy_assertions=True)

    with then:
        assert isinstance(config.Registry.ModuleLoader(), LegacyAssertRewriterLoader)
