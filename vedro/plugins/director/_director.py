from typing import Dict, Sequence, Type, Union, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParseEvent, ConfigLoadedEvent

from ._director_init_event import DirectorInitEvent
from ._reporter import Reporter

__all__ = ("Director", "DirectorPlugin",)


@final
class DirectorPlugin(Plugin):
    """
    Manages the registration and activation of scenario reporters.

    This plugin initializes reporters during configuration load and argument parsing,
    allowing reporters to be dynamically selected based on CLI arguments.
    """

    def __init__(self, config: Type["Director"]) -> None:
        """
        Initialize the DirectorPlugin with the provided configuration.

        :param config: The configuration class for the plugin.
        """
        super().__init__(config)
        self._dispatcher: Union[Dispatcher, None] = None
        self._registered_reporters: Dict[str, Reporter] = {}
        self._default_reporters = config.default_reporters[:]

    def subscribe(self, dispatcher: Dispatcher) -> None:
        """
        Subscribe to necessary events using the provided dispatcher.

        :param dispatcher: The event dispatcher used to bind event handlers.
        """
        self._dispatcher = dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                                     .listen(ArgParseEvent, self.on_arg_parse)

    async def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        """
        Handle the configuration loaded event and fire DirectorInitEvent.

        :param event: The event triggered after configuration is loaded.
        """
        assert isinstance(self._dispatcher, Dispatcher)
        await self._dispatcher.fire(DirectorInitEvent(self))

    async def on_arg_parse(self, event: ArgParseEvent) -> None:
        """
        Handle argument parsing to activate default or registered reporters.

        :param event: The event triggered when CLI arguments are being parsed.
        :raises ValueError: If default reporters are configured but none are registered,
                            or if an unknown reporter is specified.
        """
        if len(self._registered_reporters) == 0:
            if len(self._default_reporters) > 0:
                default_reporters = "', '".join(self._default_reporters)
                raise ValueError(
                    "Default reporters are specified, but no reporters have been registered: "
                    f"'{default_reporters}'."
                )
            return

        default_reporters = "', '".join(self._default_reporters) or '<no reporters>'
        help_message = f"Set reporters (default: '{default_reporters}')"

        event.arg_parser.add_argument("-r", "--reporters",
                                      nargs='*',
                                      choices=self._registered_reporters,
                                      default=self._default_reporters,
                                      help=help_message)
        args, *_ = event.arg_parser.parse_known_args()
        for reporter_name in args.reporters:
            if reporter_name not in self._registered_reporters:
                raise ValueError(f"Unknown reporter specified: '{reporter_name}'.")
            reporter = self._registered_reporters[reporter_name]
            reporter.on_chosen()

    def register(self, name: str, reporter: Reporter) -> None:
        """
        Register a reporter under a given name.

        :param name: The name to associate with the reporter.
        :param reporter: The reporter instance to register.
        """
        self._registered_reporters[name] = reporter


class Director(PluginConfig):
    """
    Declares the plugin configuration for the DirectorPlugin.

    This configuration allows defining default reporters that are used
    if no other reporters are specified via CLI.
    """
    plugin = DirectorPlugin
    description = "Manages and configures reporters for scenario execution"

    default_reporters: Sequence[str] = []
    """
    List of default reporters to be used if no other reporters are specified.

    These reporters will be activated automatically unless overridden via
    the '--reporters' CLI option.
    """
