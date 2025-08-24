import pytest

from vedro.core import Plugin, PluginConfig

__all__ = ("plugin", "BaseClass", "DerivedClass",)


@pytest.fixture()
def plugin() -> Plugin:
    return Plugin(PluginConfig)


class BaseClass:
    pass


class DerivedClass(BaseClass):
    pass
