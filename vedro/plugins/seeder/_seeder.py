import base64
import string
import sys
import uuid
from hashlib import blake2b
from typing import Dict, Type, Union, final

from niltype import Nil

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import (
    ArgParsedEvent,
    ArgParseEvent,
    CleanupEvent,
    ScenarioRunEvent,
    StartupEvent,
)

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
        self._show_seed_preamble = config.show_seed_preamble
        self._use_fixed_seed = config.use_fixed_seed
        self._show_seeds = config.show_seeds
        self._initial_seed: Union[str, None] = None
        self._custom_seed = False
        self._history: Dict[str, int] = {}

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for argument parsing, scenario execution, and cleanup.

        :param dispatcher: The dispatcher to register event listeners on.
        """
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed, priority=-sys.maxsize - 1) \
                  .listen(StartupEvent, self.on_startup) \
                  .listen(ScenarioRunEvent, self.on_scenario_run) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle argument parsing by adding options for seeding.

        Adds command-line arguments for controlling the seed used in scenarios, whether to use
        a fixed seed, and whether to display seeds during execution.

        :param event: The ArgParseEvent instance.
        """
        group = event.arg_parser.add_argument_group("Seeder")

        group.add_argument("--seed", type=str, nargs="?", help="Set seed")

        help_msg = "Use the same seed when a scenario is run multiple times in the same execution"
        group.add_argument("--fixed-seed", action="store_true", default=self._use_fixed_seed,
                           help=help_msg)

        help_msg = "Show concrete seeds for each scenario run"
        group.add_argument("--show-seeds", action="store_true", default=self._show_seeds,
                           help=help_msg)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed, initializing the seed configuration.

        Sets the initial seed (either from command line or generates one), updates configuration
        flags, and seeds the random generator with the initial seed.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        """
        self._initial_seed = event.args.seed or self._gen_initial_seed()
        self._custom_seed = event.args.seed is not None
        self._use_fixed_seed = event.args.fixed_seed
        self._show_seeds = event.args.show_seeds

        self._random.set_seed(self._initial_seed)

    def on_startup(self, event: StartupEvent) -> None:
        """
        Handle the startup event, adding the initial seed to the pre-run preamble.

        Adds the initial seed to the report preamble only when this feature is enabled
        and the seed was not explicitly provided via command-line arguments. This makes
        the seed visible at the top of the run output for reproducibility.

        :param event: The StartupEvent instance.
        """
        if not self._show_seed_preamble:
            return

        assert self._initial_seed is not None  # for type checker
        event.report.add_preamble("seed: " + self._get_seed_repr(self._initial_seed))

    def on_scenario_run(self, event: ScenarioRunEvent) -> None:
        """
        Handle the event when a scenario starts running, setting a scenario-specific seed.

        Uses a custom seed if one was set via the @seed decorator, otherwise generates a unique
        seed based on the initial seed, scenario ID, and execution index. If configured to show
        seeds, adds the seed to the scenario's extra details.

        :param event: The ScenarioRunEvent instance containing scenario and result information.
        """
        assert self._initial_seed is not None  # for type checker

        unique_id = event.scenario_result.scenario.unique_id
        self._history[unique_id] = self._history.get(unique_id, 0) + 1

        index = 1 if self._use_fixed_seed else self._history[unique_id]
        custom_seed = event.scenario_result.scenario.get_meta("seed", plugin=self)
        if custom_seed is not Nil:
            seed = str(custom_seed)
        else:
            seed = self._create_seed(self._initial_seed, unique_id, index)
        self._random.set_seed(seed)

        if self._show_seeds:
            seed_repr = self._get_seed_repr(seed)
            event.scenario_result.add_extra_details(f"seed: {seed_repr}")

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, adding the initial seed to the summary report.

        If any scenarios were executed during the test run, adds the initial seed
        to the report summary for reproducibility.

        :param event: The CleanupEvent instance containing the test report.
        """
        if (event.report.passed + event.report.failed) > 0:
            assert self._initial_seed is not None  # for type checker
            event.report.add_summary("--seed " + self._get_seed_repr(self._initial_seed))

    def _get_seed_repr(self, seed: str) -> str:
        """
        Return a safe representation of the seed for display purposes.

        If the seed contains only alphanumeric characters, hyphens, and underscores,
        returns it as-is. Otherwise, returns a quoted representation.

        :param seed: The seed string to represent.
        :return: A display-safe representation of the seed string.
        """
        alphabet = set(string.ascii_letters + string.digits + "-_")
        for char in seed:
            if char not in alphabet:
                return f"{seed!r}"
        return f"{seed}"

    def _format_seed(self, source: str) -> str:
        """
        Hash and format a source string into a readable seed format.

        Uses BLAKE2b hashing to create a deterministic, compact seed string
        formatted as "xxxx-xxxxx-xxx" in lowercase base32 encoding.

        :param source: The string to hash and format.
        :return: A formatted seed string in the pattern "xxxx-xxxxx-xxx".
        """
        hash_bytes = blake2b(source.encode(), digest_size=8).digest()
        seed = base64.b32encode(hash_bytes).decode('ascii').rstrip('=')
        return f"{seed[:4]}-{seed[4:9]}-{seed[9:]}".lower()

    def _gen_initial_seed(self) -> str:
        """
        Generate a random initial seed based on a new UUID.

        :return: A formatted seed string derived from a random UUID.
        """
        return self._format_seed(str(uuid.uuid4()))

    def _create_seed(self, initial_seed: str, scenario_id: str, index: int) -> str:
        """
        Create a deterministic seed for a specific scenario execution.

        Combines the initial seed, scenario ID, and execution index to generate
        a unique, reproducible seed for each scenario run.

        :param initial_seed: The initial seed set for the entire test run.
        :param scenario_id: The unique identifier of the scenario.
        :param index: The execution index (1 for fixed seed, incremental otherwise).
        :return: A formatted seed string unique to this scenario execution.
        """
        seed_input = f"{initial_seed}//{scenario_id}//{index}"
        return self._format_seed(seed_input)


class Seeder(PluginConfig):
    """
    Configuration class for the SeederPlugin.

    Defines settings for the SeederPlugin, including options for using a fixed seed across
    multiple scenario executions, and showing the seeds used during test runs.
    """

    plugin = SeederPlugin
    description = "Sets seeds for deterministic random behavior in scenarios"

    show_seed_preamble: bool = False
    """
    Show the initial seed in the pre-run preamble.
    """

    use_fixed_seed: bool = False
    """
    Use the same seed when a scenario is run multiple times in the same execution.
    """

    show_seeds: bool = False
    """
    Show concrete seeds for each scenario run.
    """
