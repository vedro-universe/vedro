from typing import Dict, List, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParseEvent, ConfigLoadedEvent

from ._director_init_event import DirectorInitEvent
from ._reporter import Reporter

__all__ = ("Director", "DirectorPlugin",)


class DirectorPlugin(Plugin):
    def __init__(self, config: Type["Director"]) -> None:
        super().__init__(config)
        self._dispatcher: Union[Dispatcher, None] = None
        self._registered_reporters: Dict[str, Reporter] = {}
        self._default_reporters = config.default_reporters[:]

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                                     .listen(ArgParseEvent, self.on_arg_parse)

    async def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        await self._dispatcher.fire(DirectorInitEvent(self))

    async def on_arg_parse(self, event: ArgParseEvent) -> None:
        if len(self._registered_reporters) == 0:
            return

        if len(self._default_reporters) == 1:
            default_reporters = self._default_reporters[0]
        else:
            default_reporters = "', '".join(self._default_reporters)
        help_message = f"Set reporters (default: '{default_reporters}')"

        event.arg_parser.add_argument("-r", "--reporters",
                                      nargs='*',
                                      choices=self._registered_reporters,
                                      default=self._default_reporters,
                                      help=help_message)
        args, *_ = event.arg_parser.parse_known_args()
        for reporter_name in args.reporters:
            reporter = self._registered_reporters[reporter_name]
            reporter.on_chosen()

    def register(self, name: str, reporter: Reporter) -> None:
        if len(self._default_reporters) == 0 and len(self._registered_reporters) == 0:
            self._default_reporters.append(name)
        self._registered_reporters[name] = reporter


class Director(PluginConfig):
    plugin = DirectorPlugin
    description = "Manages and configures reporters for scenario execution"

    # List of default reporters to be used if no other reporters are specified
    default_reporters: List[str] = []
