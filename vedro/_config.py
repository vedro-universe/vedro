from asyncio import CancelledError
from typing import Sequence, Type

import vedro.core as core
import vedro.plugins.artifacted as artifacted
import vedro.plugins.assert_rewriter as assert_rewriter
import vedro.plugins.deferrer as deferrer
import vedro.plugins.director as director
import vedro.plugins.dry_runner as dry_runner
import vedro.plugins.ensurer as ensurer
import vedro.plugins.interrupter as interrupter
import vedro.plugins.last_failed as last_failed
import vedro.plugins.orderer as orderer
import vedro.plugins.repeater as repeater
import vedro.plugins.rerunner as rerunner
import vedro.plugins.seeder as seeder
import vedro.plugins.skipper as skipper
import vedro.plugins.slicer as slicer
import vedro.plugins.system_upgrade as system_upgrade
import vedro.plugins.tagger as tagger
import vedro.plugins.temp_keeper as temp_keeper
import vedro.plugins.terminator as terminator
import vedro.plugins.tip_adviser as tip_adviser
from vedro.core import (
    Dispatcher,
    Factory,
    ModuleFileLoader,
    ModuleLoader,
    MonotonicScenarioRunner,
    MonotonicScenarioScheduler,
    MultiScenarioDiscoverer,
    PluginConfig,
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
from vedro.core.config_loader import computed
from vedro.core.scenario_finder.scenario_file_finder import (
    AnyFilter,
    DunderFilter,
    ExtFilter,
    HiddenFilter,
)
from vedro.core.scenario_orderer import StableScenarioOrderer

__all__ = ("Config", "computed",)


class Config(core.Config):
    """
    Defines the main configuration for the Vedro testing framework.

    This class contains settings for the framework's behavior, such as enabling
    plugins, defining factories for core components, and specifying filters
    for scenario discovery.
    """

    validate_plugins_configs: bool = True
    """
    Whether to validate plugin configurations.

    If set to `True`, the framework will validate plugin configurations to
    ensure that no unknown attributes are defined, reducing the likelihood
    of errors.
    """

    class Registry(core.Config.Registry):
        """
        Defines factories and singleton instances for core components.

        The `Registry` class is responsible for configuring key components,
        such as the scenario finder, loader, scheduler, and runner.
        """

        Dispatcher = Singleton[Dispatcher](Dispatcher)

        ModuleLoader = Factory[ModuleLoader](ModuleFileLoader)

        ScenarioFinder = Factory[ScenarioFinder](lambda: ScenarioFileFinder(
            file_filter=AnyFilter([HiddenFilter(), DunderFilter(), ExtFilter(only=["py"])]),
            dir_filter=AnyFilter([HiddenFilter(), DunderFilter()])
        ))

        ScenarioLoader = Factory[ScenarioLoader](lambda: ScenarioFileLoader(
            module_loader=Config.Registry.ModuleLoader(),
        ))

        ScenarioOrderer = Factory[ScenarioOrderer](StableScenarioOrderer)

        ScenarioDiscoverer = Factory[ScenarioDiscoverer](lambda: MultiScenarioDiscoverer(
            finder=Config.Registry.ScenarioFinder(),
            loader=Config.Registry.ScenarioLoader(),
            orderer=Config.Registry.ScenarioOrderer(),
        ))

        ScenarioScheduler = Factory[ScenarioScheduler](MonotonicScenarioScheduler)

        # Note: The `ScenarioRunner` factory definition here should not be overridden
        # with a custom runner implementation because, starting from version 2.0,
        # custom runners will be deprecated and removed.
        ScenarioRunner = Factory[ScenarioRunner](lambda: MonotonicScenarioRunner(
            dispatcher=Config.Registry.Dispatcher(),
            interrupt_exceptions=(KeyboardInterrupt, SystemExit, CancelledError),
        ))

    class Plugins(core.Config.Plugins):
        """
        Configuration for enabling and disabling plugins.

        This class contains nested classes for each plugin, where the `enabled`
        attribute determines whether the plugin is active.
        """

        class Director(director.Director):
            enabled = True

        class RichReporter(director.RichReporter):
            enabled = True

            @computed
            def depends_on(cls) -> Sequence[Type[PluginConfig]]:
                # Temporarily commented out due to issue
                # https://github.com/vedro-universe/vedro/issues/123 until
                # https://github.com/vedro-universe/vedro/pull/83 is merged
                # return [Config.Plugins.Director]
                return []

        class SilentReporter(director.SilentReporter):
            enabled = True

            # @computed
            # def depends_on(cls) -> Sequence[Type[PluginConfig]]:
            #     return [Config.Plugins.Director]

        class PyCharmReporter(director.PyCharmReporter):
            enabled = True

            # @computed
            # def depends_on(cls) -> Sequence[Type[PluginConfig]]:
            #     return [Config.Plugins.Director]

        class TempKeeper(temp_keeper.TempKeeper):
            enabled = True

        class Orderer(orderer.Orderer):
            enabled = True

        class LastFailed(last_failed.LastFailed):
            enabled = True

        class Deferrer(deferrer.Deferrer):
            enabled = True

        class Seeder(seeder.Seeder):
            enabled = True

        class Artifacted(artifacted.Artifacted):
            enabled = True

        class Skipper(skipper.Skipper):
            enabled = True

        class Slicer(slicer.Slicer):
            enabled = True

            @computed
            def depends_on(cls) -> Sequence[Type[PluginConfig]]:
                return [Config.Plugins.Skipper]

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

        class Ensurer(ensurer.Ensurer):
            enabled = True

        class Interrupter(interrupter.Interrupter):
            enabled = True

        class SystemUpgrade(system_upgrade.SystemUpgrade):
            enabled = True

        class TipAdviser(tip_adviser.TipAdviser):
            enabled = True

        class Terminator(terminator.Terminator):
            enabled = True
