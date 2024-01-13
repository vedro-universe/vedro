from importlib import import_module

from baby_steps import then, when


# moved vedro.core._module_loader -> vedro.core.module_loader
# in v1.11
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._module_loader")

    with then:
        assert module.ModuleLoader
        assert module.ModuleFileLoader
