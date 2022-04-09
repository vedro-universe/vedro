import cabina

import vedro.plugins.director as director

__all__ = ("Config",)


class Config(cabina.Config, cabina.Section):
    class Plugins(cabina.Section):
        class Director(director.Director):
            pass

        class RichReporter(director.RichReporter):
            pass

        class SilentReporter(director.SilentReporter):
            pass

        class PyCharmReporter(director.PyCharmReporter):
            pass
