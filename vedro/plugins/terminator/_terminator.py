import sys
from typing import Callable, Type, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, ArgParseEvent, CleanupEvent

__all__ = ("Terminator", "TerminatorPlugin",)


@final
class TerminatorPlugin(Plugin):
    """
    A plugin that controls the exit status of the test run based on the outcome of the tests.

    The `TerminatorPlugin` determines the exit code after the test run, taking into account
    test interruptions, failed tests, and whether any scenarios were executed. It can be
    configured to exit with code 0 even if no scenarios are run via a command-line argument.
    """

    def __init__(self, config: Type["Terminator"], *, exit_fn: Callable[[int], None] = sys.exit):
        """
        Initialize the TerminatorPlugin with the provided configuration.

        :param config: The Terminator configuration class.
        :param exit_fn: A callable function used to exit the program with a specific exit code.
            Defaults to `sys.exit`.
        """
        super().__init__(config)
        self._exit_fn = exit_fn
        self._no_scenarios_ok: bool = False

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to Vedro events for argument parsing and cleanup.

        This method registers listeners to handle command-line argument parsing and test cleanup,
        determining the appropriate exit code based on the test results and configuration.

        :param dispatcher: The dispatcher to register event listeners on.
        """
        dispatcher.listen(ArgParseEvent, self.on_arg_parse) \
                  .listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(CleanupEvent, self.on_cleanup, priority=sys.maxsize)

    def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle the argument parsing event to add the `--no-scenarios-ok` option.

        This option allows the user to configure the plugin to exit with code 0
        even if no scenarios are executed.

        :param event: The ArgParseEvent instance.
        """
        event.arg_parser.add_argument("--no-scenarios-ok",
                                      action="store_true",
                                      default=self._no_scenarios_ok,
                                      help="Exit with code 0 even if no scenarios are executed")

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        """
        Handle the event after arguments have been parsed.

        This method captures the value of the `--no-scenarios-ok` argument for use
        during the test run.

        :param event: The ArgParsedEvent instance.
        """
        self._no_scenarios_ok = event.args.no_scenarios_ok

    def on_cleanup(self, event: CleanupEvent) -> None:
        """
        Handle the cleanup event, determining the exit code based on the test report.

        This method checks if the test run was interrupted, if any tests failed,
        and whether scenarios were executed, and then exits the program with an
        appropriate exit code.

        :param event: The CleanupEvent instance containing the test report.
        """
        if event.report.interrupted:
            exc = event.report.interrupted.value
            if isinstance(exc, SystemExit) and (exc.code is not None):
                self._exit_fn(int(exc.code))
            else:
                self._exit_fn(130)  # Standard exit code for interruption (e.g., SIGINT)
        elif event.report.failed > 0:
            self._exit_fn(1)  # Exit code 1 for failed tests
        elif not self._no_scenarios_ok and event.report.passed == 0:
            self._exit_fn(1)  # Exit code 1 if no scenarios were executed and not allowed
        else:
            self._exit_fn(0)  # Exit code 0 for successful or acceptable runs


class Terminator(PluginConfig):
    """
    Configuration class for the TerminatorPlugin.

    Defines settings for controlling the exit behavior based on the results of the test run.
    Users can configure whether to exit with code 0 when no scenarios are executed.
    """

    plugin = TerminatorPlugin
    description = "Handles exit status based on test results and interruptions"
