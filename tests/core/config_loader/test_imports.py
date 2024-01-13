from importlib import import_module

from baby_steps import then, when


# moved vedro.core._config_loader -> vedro.core.config_loader
# in v1.11
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._config_loader")

    with then:
        assert module.Config is not None
        assert module.Section is not None
        assert module.ConfigType

        assert module.ConfigLoader
        assert module.ConfigFileLoader
