import cabina

from vedro.plugins.director import Director
from vedro.plugins.director.pycharm import PyCharmReporter
from vedro.plugins.director.rich import RichReporter
from vedro.plugins.director.silent import SilentReporter

__all__ = ("Config",)


class Config(cabina.Config, cabina.Section):
    class Plugins(cabina.Section):
        class Director(Director):
            pass

        class RichReporter(RichReporter):
            pass

        class SilentReporter(SilentReporter):
            pass

        class PyCharmReporter(PyCharmReporter):
            pass
