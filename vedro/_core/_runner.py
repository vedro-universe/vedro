import importlib
import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from asyncio import Event
from inspect import isclass
from pathlib import Path
from typing import Any, AsyncGenerator, List, Optional, Tuple, Type

from .._events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioFailEvent,
    ScenarioPassEvent,
    ScenarioRunEvent,
    ScenarioSkipEvent,
    StartupEvent,
    StepFailEvent,
    StepPassEvent,
)
from .._scenario import Scenario
from ..plugins import Director, Skipper, Terminator, Validator
from ._dispatcher import Dispatcher
from ._virtual_scenario import VirtualScenario
from ._virtual_step import VirtualStep


class Runner:
    def __init__(self, *, validator: Optional[Validator] = None) -> None:
        self._validator: Validator = validator if validator else Validator()

    def load(self, path: str) -> List[Type[Scenario]]:
        name = os.path.splitext(path)[0].replace("/", ".")
        module = importlib.import_module(name)

        scenarios = []
        for name in dir(module):
            val = getattr(module, name)
            if isclass(val) and val.__name__.startswith("Scenario"):
                assert issubclass(val, Scenario), f"{val} must be a subclass of vedro.Scenario"
                scenarios.append(val)
        return scenarios

    def discover(self, root: str) -> List[VirtualScenario]:
        start_dir = os.path.relpath(root)

        scenarios = []
        for path, _, files in os.walk(start_dir):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                if filename.startswith(".") or filename.startswith("_"):
                    continue
                module_scenarios = self.load(os.path.join(path, filename))
                for scenario in module_scenarios:
                    scenarios.append(VirtualScenario(scenario))

        def cmp(scn: VirtualScenario) -> Tuple[Any, ...]:
            path = Path(scn.path)
            return (len(path.parts),) + path.parts
        scenarios.sort(key=cmp)
        return scenarios

    async def _run_steps(self, scenario: VirtualScenario) -> AsyncGenerator[VirtualStep, None]:
        scope = scenario()
        scenario.set_scope(scope)
        for step in scenario.get_steps():
            try:
                if step.is_coro():
                    await step(scope)
                else:
                    step(scope)
            except:  # noqa: E722
                exception = sys.exc_info()
                scenario.set_exception(exception)
                step.mark_failed()
                yield step
            else:
                step.mark_passed()
                yield step

    async def run(self, event: Event) -> None:
        os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

        arg_parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

        dispatcher = Dispatcher()
        dispatcher.register(self._validator)
        dispatcher.register(Director())
        dispatcher.register(Skipper())
        dispatcher.register(Terminator())

        await dispatcher.fire(ArgParseEvent(arg_parser))
        args = arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        scenarios = self.discover("scenarios")
        await dispatcher.fire(StartupEvent(scenarios))

        for scenario in scenarios:
            if event.is_set():
                break

            if scenario.is_skipped():
                await dispatcher.fire(ScenarioSkipEvent(scenario))
                continue

            await dispatcher.fire(ScenarioRunEvent(scenario))

            async for step in self._run_steps(scenario):
                if step.is_failed():
                    await dispatcher.fire(StepFailEvent(step))
                    scenario.mark_failed()
                    break
                elif step.is_passed():
                    await dispatcher.fire(StepPassEvent(step))
                else:
                    raise ValueError()
            else:
                scenario.mark_passed()

            if scenario.is_passed():
                await dispatcher.fire(ScenarioPassEvent(scenario))
            elif scenario.is_failed():
                await dispatcher.fire(ScenarioFailEvent(scenario))
            else:
                raise ValueError()

        await dispatcher.fire(CleanupEvent())
