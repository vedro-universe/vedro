from baby_steps import then, when
from pytest import raises

from vedro.core import Config, ConfigLoader


def test_config_loader():
    with when, raises(Exception) as exc_info:
        ConfigLoader(Config)

    with then:
        assert exc_info.type is TypeError
        assert "Can't instantiate abstract class ConfigLoader" in str(exc_info.value)
