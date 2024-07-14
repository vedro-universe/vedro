import string
import sys
import uuid
from hashlib import blake2b
from typing import Dict, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, CleanupEvent, ScenarioRunEvent

from ._random import RandomGenerator, StandardRandomGenerator

__all__ = ("Seeder", "SeederPlugin",)

_random = StandardRandomGenerator()


class SeederPlugin(Plugin):
    def __init__(self, config: Type["Seeder"], *, random: RandomGenerator = _random) -> None:
        super().__init__(config)
        self._random = random
        self._use_fixed_seed = config.use_fixed_seed
        self._show_seeds = config.show_seeds
        self._initial_seed: Union[str, None] = None
        self._history: Dict[str, int] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed, priority=-sys.maxsize - 1) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        event.arg_parser.add_argument("--seed", type=str, nargs="?", help="Set seed")

        help_msg = "Use the same seed when a scenario is run multiple times in the same execution"
        event.arg_parser.add_argument("--fixed-seed",
                                      action="store_true",
                                      default=self._use_fixed_seed,
                                      help=help_msg)

        help_msg = "Show concrete seeds for each scenario run"
        event.arg_parser.add_argument("--show-seeds",
                                      action="store_true",
                                      default=self._show_seeds,
                                      help=help_msg)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._initial_seed = event.args.seed or self._gen_initial_seed()
        self._use_fixed_seed = event.args.fixed_seed
        self._show_seeds = event.args.show_seeds

        self._random.set_seed(self._initial_seed)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        assert self._initial_seed is not None  # for type checker

        unique_id = event.scenario_result.scenario.unique_id
        self._history[unique_id] = self._history.get(unique_id, 0) + 1

        index = 1 if self._use_fixed_seed else self._history[unique_id]
        seed = self._create_seed(self._initial_seed, unique_id, index)
        self._random.set_seed(seed)

        if self._show_seeds:
            seed_repr = self._get_seed_repr(seed)
            event.scenario_result.add_extra_details(f"seed: {seed_repr[:8]}..{seed_repr[-8:]}")

    def on_cleanup(self, event: CleanupEvent) -> None:
        if (event.report.passed + event.report.failed) > 0:
            assert self._initial_seed is not None  # for type checker
            event.report.add_summary("--seed " + self._get_seed_repr(self._initial_seed))

    def _get_seed_repr(self, seed: str) -> str:
        alphabet = set(string.ascii_letters + string.digits + "-_")
        for char in seed:
            if char not in alphabet:
                return f"{seed!r}"
        return f"{seed}"

    def _gen_initial_seed(self) -> str:
        return str(uuid.uuid4())

    def _create_seed(self, initial_seed: str, scenario_id: str, index: int) -> str:
        seed = f"{initial_seed}//{scenario_id}//{index}"
        return blake2b(seed.encode()).hexdigest()


class Seeder(PluginConfig):
    plugin = SeederPlugin
    description = "Sets seeds for deterministic random behavior in scenarios"

    # Use the same seed when a scenario is run multiple times in the same execution
    use_fixed_seed: bool = False

    # Show concrete seeds for each scenario run
    show_seeds: bool = False
