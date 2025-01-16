import random
from typing import Type, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, CleanupEvent

__all__ = ("TipAdviser", "TipAdviserPlugin",)


@final
class TipAdviserPlugin(Plugin):
    """
    Provides tips and suggestions based on command-line arguments after test execution.

    The `TipAdviserPlugin` analyzes specific command-line arguments and offers relevant tips
    to enhance the test execution experience.

    Tips are displayed in the summary report after the test run.
    """

    def __init__(self, config: Type["TipAdviser"]) -> None:
        """
        Initialize the TipAdviserPlugin with the provided configuration.

        :param config: The TipAdviser configuration class.
        """
        super().__init__(config)
        self._show_tips: bool = config.show_tips
        self._repeats: int = 1
        self._fail_fast: bool = False
        self._fixed_seed: bool = False

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for parsing arguments and cleaning up after execution.

        :param dispatcher: The dispatcher to register event listeners on.
        """
        dispatcher.listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after command-line arguments are parsed.

        Extract relevant arguments and store their values for use in generating tips.

        :param event: The ArgParsedEvent instance containing parsed arguments.
        """
        self._repeats = event.args.repeats if hasattr(event.args, 'repeats') else 1
        self._fail_fast = event.args.fail_fast if hasattr(event.args, 'fail_fast') else False
        self._fixed_seed = event.args.fixed_seed if hasattr(event.args, 'fixed_seed') else False

        # Note: In Vedro, plugins are generally designed to operate independently and
        # do not have knowledge of each other's existence. This modular design ensures
        # that plugins can be used in isolation without unintended dependencies or
        # interference.
        # However, the `TipAdviserPlugin` is an experimental plugin that is aware of
        # certain other plugins and their  associated command-line arguments.
        # This awareness allows it to provide helpful tips based on the presence and
        # configuration of those plugins. While  this behavior breaks the typical
        # isolation of Vedro plugins, it is intentional  to enhance the user experience
        # by offering actionable suggestions tailored to the test execution context.

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event by displaying a random tip, if applicable.

        Based on the parsed arguments, generates tips for enhancing test runs. Tips are
        added to the test run's summary report if the `show_tips` option is enabled.

        :param event: The CleanupEvent instance containing the test report.
        """
        if not self._show_tips:
            return

        tips = []
        if self._repeats > 1 and not self._fixed_seed:
            tips.append(
                "Consider using `--fixed-seed` for consistent results across repeated runs"
            )
        if self._repeats > 1 and self._fail_fast:
            tips.append(
                "Consider using `--fail-fast-on-repeat` to to stop after the first failing repeat"
            )

        if len(tips) > 0:
            tips.append(
                "To disable these tips, run `vedro plugin disable vedro.plugins.tip_adviser`"
            )
            random_tip = random.choice(tips)
            event.report.add_summary(f"Tip: {random_tip}")


class TipAdviser(PluginConfig):
    """
    Configuration class for the TipAdviserPlugin.

    Defines settings for the TipAdviserPlugin, including whether tips should be displayed
    during test execution.
    """

    plugin = TipAdviserPlugin
    description = "Provides random tips based on Vedro command-line arguments"

    # If True, the plugin will display tips at the end of the test run
    show_tips: bool = True
