import random
from typing import Any, Dict, Type, Union, cast
from uuid import uuid4

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioRunEvent,
    StartupEvent,
)

__all__ = ("Seeder", "SeederPlugin",)


class SeederPlugin(Plugin):
    def __init__(self, config: Type["Seeder"], *, random: Any = random) -> None:
        super().__init__(config)
        self._random = random
        self._seed: Union[str, None] = None
        self._scenarios: Dict[str, int] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--seed", nargs="?", help="Set seed")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._seed = event.args.seed
        if self._seed is None:
            self._seed = str(uuid4())

    def _generate_seed(self) -> int:
        return cast(int, self._random.randint(1, 2 ** 63 - 1))

    def on_startup(self, event: StartupEvent) -> None:
        self._random.seed(self._seed)
        for scenario in event.scenarios:
            self._scenarios[scenario.unique_id] = self._generate_seed()

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        seed = self._scenarios[event.scenario_result.scenario.unique_id]
        self._random.seed(seed)
        for _ in range(event.scenario_result.rerun):
            seed = self._generate_seed()
        self._random.seed(seed)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if (event.report.passed + event.report.failed) > 0:
            summary = f"--seed {self._seed}"
            event.report.add_summary(summary)


class Seeder(PluginConfig):
    plugin = SeederPlugin
