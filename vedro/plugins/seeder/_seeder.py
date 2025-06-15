import string
import sys
import uuid
from hashlib import blake2b
from typing import Dict, Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, CleanupEvent, ScenarioRunEvent

from ._random import RandomGenerator, StandardRandomGenerator

__all__ = ("Seeder", "SeederPlugin",)

_random = StandardRandomGenerator()


@final
class SeederPlugin(Plugin):
    """
    A plugin that provides deterministic random behavior by seeding random number generators.

    The `SeederPlugin` ensures that scenarios have reproducible random behavior by assigning
    a unique or fixed seed value for each scenario execution. It also provides options to display
    the seeds used during the execution.
    """

    def __init__(self, config: Type["Seeder"], *, random: RandomGenerator = _random) -> None:
        """
        Initialize the SeederPlugin with the provided configuration.

        :param config: The Seeder configuration class.
        :param random: A random generator instance. Defaults to `StandardRandomGenerator`.
        """
        super().__init__(config)
        self._random = random
        self._use_fixed_seed = config.use_fixed_seed
        self._show_seeds = config.show_seeds
        self._initial_seed: Union[str, None] = None
        self._history: Dict[str, int] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for argument parsing, scenario execution, and cleanup.

        :param dispatcher: The dispatcher to register event listeners on.
        """
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed, priority=-sys.maxsize - 1) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle argument parsing by adding options for seeding.

        Adds command-line arguments for controlling the seed used in scenarios, whether to use
        a fixed seed, and whether to display seeds during execution.

        :param event: The ArgParseEvent instance.
        """
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
        """
        Handle the event after arguments have been parsed, processing seed options.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        """
        self._initial_seed = event.args.seed or self._gen_initial_seed()
        self._use_fixed_seed = event.args.fixed_seed
        self._show_seeds = event.args.show_seeds

        self._random.set_seed(self._initial_seed)

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Handle the event when a scenario starts running, setting a scenario-specific seed.

        If configured to show seeds, adds the seed used for the scenario to the scenario result.

        :param event: The ScenarioRunEvent instance.
        """
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
        """
        Handle the cleanup event, adding the initial seed to the summary report.

        If any scenarios were executed, the initial seed used during the test run is added
        to the report's summary.

        :param event: The CleanupEvent instance.
        """
        if (event.report.passed + event.report.failed) > 0:
            assert self._initial_seed is not None  # for type checker
            event.report.add_summary("--seed " + self._get_seed_repr(self._initial_seed))

    def _get_seed_repr(self, seed: str) -> str:
        """
        Return a representation of the seed, ensuring that it only contains allowed characters.

        :param seed: The seed string.
        :return: A safe representation of the seed.
        """
        alphabet = set(string.ascii_letters + string.digits + "-_")
        for char in seed:
            if char not in alphabet:
                return f"{seed!r}"
        return f"{seed}"

    def _gen_initial_seed(self) -> str:
        """
        Generate an initial seed based on a new UUID.

        :return: A new UUID string used as the initial seed.
        """
        return str(uuid.uuid4())

    def _create_seed(self, initial_seed: str, scenario_id: str, index: int) -> str:
        """
        Create a unique seed for a scenario based on the initial seed, scenario ID, and index.

        Uses the BLAKE2b hashing algorithm to generate a deterministic seed.

        :param initial_seed: The initial seed set for the entire test run.
        :param scenario_id: The unique ID of the scenario.
        :param index: The index of the scenario execution.
        :return: A hashed seed string.
        """
        seed = f"{initial_seed}//{scenario_id}//{index}"
        return blake2b(seed.encode()).hexdigest()


class Seeder(PluginConfig):
    """
    Configuration class for the SeederPlugin.

    Defines settings for the SeederPlugin, including options for using a fixed seed across
    multiple scenario executions, and showing the seeds used during test runs.
    """

    plugin = SeederPlugin
    description = "Sets seeds for deterministic random behavior in scenarios"

    # Use the same seed when a scenario is run multiple times in the same execution
    use_fixed_seed: bool = False

    # Show concrete seeds for each scenario run
    show_seeds: bool = False
