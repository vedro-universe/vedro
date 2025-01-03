import random
from typing import Type, final

from vedro.core import Dispatcher, Plugin, PluginConfig
from vedro.events import ArgParsedEvent, CleanupEvent

__all__ = ("TipsPlugin", "Tips",)


@final
class TipsPlugin(Plugin):
    def __init__(self, config: Type["Tips"]) -> None:
        super().__init__(config)
        self._show_tips: bool = config.show_tips
        self._repeats: int = 1
        self._fail_fast: bool = False
        self._fixed_seed: bool = False

    def subscribe(self, dispatcher: Dispatcher) -> None:
        dispatcher.listen(ArgParsedEvent, self.on_arg_parsed) \
                  .listen(CleanupEvent, self.on_cleanup)

    def on_arg_parsed(self, event: ArgParsedEvent) -> None:
        self._repeats = event.args.repeats if hasattr(event.args, 'repeats') else 1
        self._fail_fast = event.args.fail_fast if hasattr(event.args, 'fail_fast') else False
        self._fixed_seed = event.args.fixed_seed if hasattr(event.args, 'fixed_seed') else False

    def on_cleanup(self, event: CleanupEvent) -> None:
        if not self._show_tips:
            return

        tips = []
        if self._repeats > 1 and not self._fixed_seed:
            tips.append(
                "Use `--fixed-seed` to ensure consistent test results across repeated runs.")
        if self._repeats > 1 and self._fail_fast:
            tips.append(
                "Use `--fail-fast-on-repeat` to stop on the first failing repeat.")

        if len(tips) > 0:
            tips.append(
                "Run `vedro plugin disable tips` if you do not want to see these tips.")
            random_tip = random.choice(tips)
            event.report.add_summary(f"Tip: {random_tip}")


class Tips(PluginConfig):
    plugin = TipsPlugin
    description = "<description>"

    show_tips: bool = True
