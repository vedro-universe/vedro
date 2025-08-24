from baby_steps import then, when
from pytest import raises

from vedro.core import PluginConfig
from vedro.plugins.director import Reporter


def test_reporter():
    with when, raises(BaseException) as exc:
        Reporter(PluginConfig)

    with then:
        assert exc.type is TypeError
