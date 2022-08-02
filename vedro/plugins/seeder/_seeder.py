import uuid
from typing import Dict, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioRunEvent,
    StartupEvent,
)

from ._random import RandomGenerator, StandardRandomGenerator, StateType

__all__ = ("Seeder", "SeederPlugin",)

_random = StandardRandomGenerator()


class SeederPlugin(Plugin):
    MIN_SEED = 1
    MAX_SEED = 2 ** 63 - 1

    def __init__(self, config: Type["Seeder"], *, random: RandomGenerator = _random) -> None:
        super().__init__(config)
        self._random = random

        self._inital_seed: Union[str, None] = None
        self._discovered_seed: Union[int, None] = None
        self._scheduled_seed: Union[int, None] = None
        self._scheduled_state: Union[StateType, None] = None

        self._scenarios: Dict[str, int] = {}
        self._history: Dict[str, int] = {}

    def _generate_seed(self) -> int:
        return self._random.random_int(self.MIN_SEED, self.MAX_SEED)

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--seed", nargs="?", help="Set seed")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._inital_seed = event.args.seed if (event.args.seed is not None) else str(uuid.uuid4())

    def on_startup(self, event: StartupEvent) -> None:
        assert self._inital_seed is not None
        self._random.set_seed(self._inital_seed)

        self._scheduled_seed = self._generate_seed()
        self._random.set_seed(self._scheduled_seed)
        self._scheduled_state = self._random.get_state()

        self._discovered_seed = self._generate_seed()
        self._random.set_seed(self._discovered_seed)

        for scenario in event.scheduler.discovered:
            self._scenarios[scenario.unique_id] = self._generate_seed()

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        unique_id = event.scenario_result.scenario.unique_id
        if unique_id not in self._history:
            self._history[unique_id] = 0
        self._history[unique_id] += 1

        if unique_id not in self._scenarios:
            assert self._scheduled_state is not None
            self._random.set_state(self._scheduled_state)
            self._scenarios[unique_id] = self._generate_seed()
            self._scheduled_state = self._random.get_state()

        seed = self._scenarios[unique_id]
        self._random.set_seed(seed)

        for _ in range(self._history[unique_id]):
            seed = self._generate_seed()
        self._random.set_seed(seed)

    def on_cleanup(self, event: CleanupEvent) -> None:
        if (event.report.passed + event.report.failed) > 0:
            event.report.add_summary(f"--seed {self._inital_seed}")


class Seeder(PluginConfig):
    plugin = SeederPlugin
