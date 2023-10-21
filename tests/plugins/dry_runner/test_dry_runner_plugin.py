from unittest.mock import Mock

from baby_steps import given, then, when

from vedro.core import Dispatcher, ScenarioRunner
from vedro.plugins.dry_runner import DryRunnerImpl, DryRunnerPlugin

from ._utils import (
    dispatcher,
    dry_runner_plugin,
    fire_arg_parsed_event,
    fire_config_loaded_event,
    make_config,
)

__all__ = ("dispatcher", "dry_runner_plugin",)  # fixtures


async def test_dry_run(*, dry_runner_plugin: DryRunnerPlugin, dispatcher: Dispatcher):
    with given:
        scenario_runner_ = Mock(ScenarioRunner)
        config = make_config(dispatcher, scenario_runner_)
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher, dry_run=True)

    with then:
        assert isinstance(config.Registry.ScenarioRunner(), DryRunnerImpl)


async def test_no_dry_run(*, dry_runner_plugin: DryRunnerPlugin, dispatcher: Dispatcher):
    with given:
        scenario_runner_ = Mock(ScenarioRunner)
        config = make_config(dispatcher, scenario_runner_)
        await fire_config_loaded_event(dispatcher, config)

    with when:
        await fire_arg_parsed_event(dispatcher, dry_run=False)

    with then:
        assert config.Registry.ScenarioRunner() == scenario_runner_
