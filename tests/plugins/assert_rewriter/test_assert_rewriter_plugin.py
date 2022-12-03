from baby_steps import then, when

from vedro.core import Plugin
from vedro.plugins.assert_rewriter import AssertRewriter, AssertRewriterPlugin


def test_plugin():
    with when:
        plugin = AssertRewriterPlugin(AssertRewriter)

    with then:
        assert isinstance(plugin, Plugin)
