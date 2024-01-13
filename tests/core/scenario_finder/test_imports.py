from importlib import import_module

from baby_steps import then, when


# moved vedro.core._scenario_finder._file_filters -> vedro.core.scenario_finder
# in v1.11
def test_backward_compatibility():
    with when:
        module = import_module("vedro.core._scenario_finder._file_filters")

    with then:
        assert module.AnyFilter
        assert module.DunderFilter
        assert module.ExtFilter
        assert module.FileFilter
        assert module.HiddenFilter
