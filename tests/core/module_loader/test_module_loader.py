from baby_steps import given, when
from pytest import raises

from vedro.core import ModuleLoader


def test_abstract_module_loader_instantiation():
    with when, raises(BaseException) as exc_info:
        ModuleLoader()

    with given:
        assert exc_info.type is TypeError
        assert "Can't instantiate abstract class ModuleLoader" in str(exc_info.value)
