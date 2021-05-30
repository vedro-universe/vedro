import os
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from asyncio import Event
from pathlib import Path
from typing import Any, AsyncGenerator, List, Optional, Tuple

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
from ..plugins import Director, Skipper, Terminator, Validator
from ._dispatcher import Dispatcher
from ._scenario_discoverer import ScenarioDiscoverer
from ._virtual_scenario import VirtualScenario
from ._virtual_step import VirtualStep


class Runner:
    def __init__(self, discoverer: ScenarioDiscoverer, *,
                 validator: Optional[Validator] = None) -> None:
        self._discoverer = discoverer
        self._validator: Validator = validator if validator else Validator()

    async def discover(self, root: Path) -> List[VirtualScenario]:
        start_dir = os.path.relpath(root)
        scenarios = await self._discoverer.discover(Path(start_dir))
        virtual_scenarios = [VirtualScenario(scn) for scn in scenarios]

        def cmp(scn: VirtualScenario) -> Tuple[Any, ...]:
            path = Path(scn.path)
            return (len(path.parts),) + path.parts
        virtual_scenarios.sort(key=cmp)

        return virtual_scenarios

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

        formatter = ArgumentDefaultsHelpFormatter
        arg_parser = ArgumentParser("vedro", formatter_class=formatter, add_help=False)

        dispatcher = Dispatcher()
        dispatcher.register(self._validator)
        dispatcher.register(Director())
        dispatcher.register(Skipper())
        dispatcher.register(Terminator())

        await dispatcher.fire(ArgParseEvent(arg_parser))
        arg_parser.add_argument("-h", "--help",
                                action="help", help="show this help message and exit")
        args = arg_parser.parse_args()
        await dispatcher.fire(ArgParsedEvent(args))

        scenarios = await self.discover(Path("scenarios"))
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
