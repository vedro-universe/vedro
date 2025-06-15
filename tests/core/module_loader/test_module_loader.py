from baby_steps import then, when
from pytest import raises

from vedro.core import ModuleLoader


def test_abstract_module_loader_instantiation():
    with when, raises(BaseException) as exc:
        ModuleLoader()

    with then:
        assert exc.type is TypeError
        assert "Can't instantiate abstract class ModuleLoader" in str(exc.value)
