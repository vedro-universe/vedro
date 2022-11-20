from asyncio import CancelledError

import vedro.core as core
import vedro.plugins.artifacted as artifacted
import vedro.plugins.assert_rewriter as assert_rewriter
import vedro.plugins.deferrer as deferrer
import vedro.plugins.director as director
import vedro.plugins.dry_runner as dry_runner
import vedro.plugins.interrupter as interrupter
import vedro.plugins.orderer as orderer
import vedro.plugins.repeater as repeater
import vedro.plugins.rerunner as rerunner
import vedro.plugins.seeder as seeder
import vedro.plugins.skipper as skipper
import vedro.plugins.slicer as slicer
import vedro.plugins.tagger as tagger
import vedro.plugins.terminator as terminator
from vedro.core import (
    Dispatcher,
    Factory,
    MonotonicScenarioRunner,
    MonotonicScenarioScheduler,
    MultiScenarioDiscoverer,
    ScenarioDiscoverer,
    ScenarioFileFinder,
    ScenarioFileLoader,
    ScenarioFinder,
    ScenarioLoader,
    ScenarioOrderer,
    ScenarioRunner,
    ScenarioScheduler,
    Singleton,
)
from vedro.core._scenario_finder._file_filters import (
    AnyFilter,
    DunderFilter,
    ExtFilter,
    HiddenFilter,
)
from vedro.core.scenario_orderer import PlainScenarioOrderer

__all__ = ("Config",)


class Config(core.Config):

    class Registry(core.Config.Registry):
        Dispatcher = Singleton[Dispatcher](Dispatcher)

        ScenarioFinder = Factory[ScenarioFinder](lambda: ScenarioFileFinder(
            file_filter=AnyFilter([HiddenFilter(), DunderFilter(), ExtFilter(only=["py"])]),
            dir_filter=AnyFilter([HiddenFilter(), DunderFilter()])
        ))

        ScenarioLoader = Factory[ScenarioLoader](ScenarioFileLoader)

        ScenarioOrderer = Factory[ScenarioOrderer](PlainScenarioOrderer)

        ScenarioDiscoverer = Factory[ScenarioDiscoverer](lambda: MultiScenarioDiscoverer(
            finder=Config.Registry.ScenarioFinder(),
            loader=Config.Registry.ScenarioLoader(),
            orderer=Config.Registry.ScenarioOrderer(),
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

        class Orderer(orderer.Orderer):
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

        class AssertRewriter(assert_rewriter.AssertRewriter):
            enabled = True

        class DryRunner(dry_runner.DryRunner):
            enabled = True

        class Terminator(terminator.Terminator):
            enabled = True
