import vedro.core as core
import vedro.plugins.director as director

__all__ = ("Config",)


class Config(core.Config):
    class Plugins(core.Section):
        class Director(director.Director):
            pass

        class RichReporter(director.RichReporter):
            pass

        class SilentReporter(director.SilentReporter):
            pass

        class PyCharmReporter(director.PyCharmReporter):
            pass
