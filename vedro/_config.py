import vedro.core as core
import vedro.plugins.deferrer as deferrer
import vedro.plugins.director as director
import vedro.plugins.interrupter as interrupter
import vedro.plugins.seeder as seeder
import vedro.plugins.skipper as skipper
import vedro.plugins.slicer as slicer
import vedro.plugins.tagger as tagger
import vedro.plugins.terminator as terminator

__all__ = ("Config",)


class Config(core.Config):
    class Plugins(core.Section):
        class Director(director.Director):
            enabled = True

        class RichReporter(director.RichReporter):
            enabled = True

        class SilentReporter(director.SilentReporter):
            enabled = True

        class PyCharmReporter(director.PyCharmReporter):
            enabled = True

        class Deferrer(deferrer.Deferrer):
            enabled = True

        class Interrupter(interrupter.Interrupter):
            enabled = True

        class Seeder(seeder.Seeder):
            enabled = True

        class Skipper(skipper.Skipper):
            enabled = True

        class Slicer(slicer.Slicer):
            enabled = True

        class Tagger(tagger.Tagger):
            enabled = True

        class Terminator(terminator.Terminator):
            enabled = True
