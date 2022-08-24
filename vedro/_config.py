from asyncio import CancelledError

import vedro.core as core
import vedro.plugins.artifacted as artifacted
import vedro.plugins.deferrer as deferrer
import vedro.plugins.director as director
import vedro.plugins.interrupter as interrupter
import vedro.plugins.repeater as repeater
import vedro.plugins.rerunner as rerunner
import vedro.plugins.seeder as seeder
import vedro.plugins.skipper as skipper
import vedro.plugins.slicer as slicer
import vedro.plugins.tagger as tagger
import vedro.plugins.terminator as terminator
from vedro.core import Dispatcher
from vedro.core._container import Factory, Singleton
from vedro.core._scenario_discoverer import DefaultScenarioDiscoverer, ScenarioDiscoverer
from vedro.core._scenario_finder import ScenarioFileFinder, ScenarioFinder
from vedro.core._scenario_finder._file_filters import (
    AnyFilter,
    DunderFilter,
    ExtFilter,
    HiddenFilter,
)
from vedro.core._scenario_loader import ScenarioFileLoader, ScenarioLoader
from vedro.core._scenario_runner import MonotonicScenarioRunner, ScenarioRunner
from vedro.core._scenario_scheduler import MonotonicScenarioScheduler, ScenarioScheduler

__all__ = ("Config",)


class Config(core.Config):

    class Registry(core.Config.Registry):
        Dispatcher = Singleton[Dispatcher](Dispatcher)

        ScenarioFinder = Factory[ScenarioFinder](lambda: ScenarioFileFinder(
            file_filter=AnyFilter([HiddenFilter(), DunderFilter(), ExtFilter(only=["py"])]),
            dir_filter=AnyFilter([HiddenFilter(), DunderFilter()])
        ))

        ScenarioLoader = Factory[ScenarioLoader](ScenarioFileLoader)

        ScenarioDiscoverer = Factory[ScenarioDiscoverer](lambda: DefaultScenarioDiscoverer(
            finder=Config.Registry.ScenarioFinder(),
            loader=Config.Registry.ScenarioLoader(),
        ))

        ScenarioScheduler = Factory[ScenarioScheduler](MonotonicScenarioScheduler)

        ScenarioRunner = Factory[ScenarioRunner](lambda: MonotonicScenarioRunner(
            dispatcher=Config.Registry.Dispatcher(),
            interrupt_exceptions=(KeyboardInterrupt, SystemExit, CancelledError),
        ))

    class Plugins(core.Config.Plugins):
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

        class Artifacted(artifacted.Artifacted):
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

        class Repeater(repeater.Repeater):
            enabled = True

        class Rerunner(rerunner.Rerunner):
            enabled = True

        class Terminator(terminator.Terminator):
            enabled = True
