from typing import Dict, Type, Union

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParseEvent, ConfigLoadedEvent

from ._director_init_event import DirectorInitEvent
from ._reporter import Reporter

__all__ = ("Director", "DirectorPlugin",)


class DirectorPlugin(Plugin):
    def __init__(self, config: Type["Director"]) -> None:
        super().__init__(config)
        self._dispatcher: Union[Dispatcher, None] = None
        self._reporters: Dict[str, Reporter] = {}
        self._default_reporter = ""

    def subscribe(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher.listen(ConfigLoadedEvent, self.on_config_loaded) \
                                     .listen(ArgParseEvent, self.on_arg_parse)

    async def on_config_loaded(self, event: ConfigLoadedEvent) -> None:
        assert isinstance(self._dispatcher, Dispatcher)
        await self._dispatcher.fire(DirectorInitEvent(self))

    async def on_arg_parse(self, event: ArgParseEvent) -> None:
        if len(self._reporters) == 0:
            return
        event.arg_parser.add_argument("-r", "--reporters", nargs='*', choices=self._reporters,
                                      default=[self._default_reporter],
                                      help=f"Set reporter (default {self._default_reporter})")
        args, *_ = event.arg_parser.parse_known_args()
        for reporter_name in args.reporters:
            reporter = self._reporters[reporter_name]
            reporter.on_chosen()

    def register(self, name: str, reporter: Reporter) -> None:
        if len(self._reporters) == 0:
            self._default_reporter = name
        self._reporters[name] = reporter


class Director(PluginConfig):
    plugin = DirectorPlugin
