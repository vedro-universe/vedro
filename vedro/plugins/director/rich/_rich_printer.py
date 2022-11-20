import json
import os
from traceback import format_exception
from types import FrameType, TracebackType
from typing import Any, Callable, Dict, List, Optional, Union, cast

from rich.console import Console, RenderableType
from rich.status import Status
from rich.style import Style
from rich.traceback import Trace, Traceback

import vedro
from vedro.core import ExcInfo, ScenarioStatus, StepStatus

__all__ = ("RichPrinter",)


def make_console() -> Console:
    return Console(highlight=False, force_terminal=True, markup=False, soft_wrap=True)


class RichPrinter:
    def __init__(self, console_factory: Callable[[], Console] = make_console,
                 *, traceback_factory: Callable[..., Traceback] = Traceback) -> None:
        self._console = console_factory()
        self._traceback_factory = traceback_factory
        self._scenario_spinner: Union[Status, None] = None

    @property
    def console(self) -> Console:
        return self._console

    def print_header(self, title: str = "Scenarios") -> None:
        self._console.out(title)

    def print_namespace(self, namespace: str) -> None:
        namespace = namespace.replace("_", " ").replace("/", " / ")
        self._console.out(f"* {namespace}", style=Style(bold=True))

    def print_scenario_subject(self, subject: str, status: ScenarioStatus, *,
                               elapsed: Optional[float] = None, prefix: str = "") -> None:
        if status == ScenarioStatus.PASSED:
            subject = f"✔ {subject}"
            style = Style(color="green")
        elif status == ScenarioStatus.FAILED:
            subject = f"✗ {subject}"
            style = Style(color="red")
        elif status == ScenarioStatus.SKIPPED:
            subject = f"○ {subject}"
            style = Style(color="grey70")
        else:
            return

        self._console.out(prefix, end="")
        if elapsed is not None:
            self._console.out(subject, style=style, end="")
            self._console.out(f" ({elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(subject, style=style)

    def print_scenario_caption(self, caption: str, *, prefix: str = "") -> None:
        self._console.out(prefix, end="")
        self._console.out(f"{caption}", style=Style(color="grey50"))

    def print_step_name(self, name: str, status: StepStatus, *,
                        elapsed: Optional[float] = None, prefix: str = "") -> None:
        if status == StepStatus.PASSED:
            name = f"✔ {name}"
            style = Style(color="green")
        elif status == StepStatus.FAILED:
            name = f"✗ {name}"
            style = Style(color="red")
        else:
            return

        self._console.out(prefix, end="")
        if elapsed is not None:
            self._console.out(name, style=style, end="")
            self._console.out(f" ({elapsed:.2f}s)", style=Style(color="grey50"))
        else:
            self._console.out(name, style=style)

    def __filter_internals(self, traceback: TracebackType) -> TracebackType:
        class _Traceback:
            def __init__(self, tb_frame: FrameType, tb_lasti: int, tb_lineno: int,
                         tb_next: Optional[TracebackType]) -> None:
                self.tb_frame = tb_frame
                self.tb_lasti = tb_lasti
                self.tb_lineno = tb_lineno
                self.tb_next = tb_next

        tb = _Traceback(traceback.tb_frame, traceback.tb_lasti, traceback.tb_lineno,
                        traceback.tb_next)

        root = os.path.dirname(vedro.__file__)
        while tb.tb_next is not None:
            filename = os.path.abspath(tb.tb_frame.f_code.co_filename)
            if os.path.commonpath([root, filename]) != root:
                break
            tb = tb.tb_next  # type: ignore

        return cast(TracebackType, tb)

    def print_exception(self, exc_info: ExcInfo, *,
                        max_frames: int = 8, show_internal_calls: bool = False) -> None:
        if show_internal_calls:
            traceback = exc_info.traceback
        else:
            traceback = self.__filter_internals(exc_info.traceback)

        formatted = format_exception(exc_info.type, exc_info.value, traceback, limit=max_frames)
        self._console.out("".join(formatted), style=Style(color="yellow"))

    def __filter_locals(self, trace: Trace) -> None:
        for stack in trace.stacks:
            for frame in stack.frames:
                if frame.locals is not None:
                    frame.locals = {k: v for k, v in frame.locals.items()
                                    if k != "self" and not k.startswith("@")}

    def print_pretty_exception(self, exc_info: ExcInfo, *,
                               max_frames: int = 8,  # min=4 (see rich.traceback.Traceback impl)
                               show_locals: bool = False,
                               show_internal_calls: bool = False,
                               word_wrap: bool = False) -> None:
        if show_internal_calls:
            traceback = exc_info.traceback
        else:
            traceback = self.__filter_internals(exc_info.traceback)

        trace = Traceback.extract(exc_info.type, exc_info.value, traceback,
                                  show_locals=show_locals)

        if show_locals:
            self.__filter_locals(trace)

        tb = self._traceback_factory(trace, max_frames=max_frames, word_wrap=word_wrap)
        self._console.print(tb)
        self.print_empty_line()

    def pretty_format(self, value: Any) -> Any:
        try:
            return json.dumps(value, ensure_ascii=False, indent=4)
        except BaseException:
            return repr(value)

    def print_scope(self, scope: Dict[str, Any]) -> None:
        self.print_scope_header("Scope")
        for key, val in scope.items():
            self.print_scope_key(key, indent=1)
            self.print_scope_val(self.pretty_format(val))
        self.print_empty_line()

    def print_scope_header(self, title: str) -> None:
        self._console.out(title, style=Style(color="blue", bold=True))

    def print_scope_key(self, key: str, *, indent: int = 0, line_break: bool = False) -> None:
        prepend = " " * indent
        end = "\n" if line_break else ""
        self._console.out(f"{prepend}{key}: ", end=end, style=Style(color="blue"))

    def print_scope_val(self, val: Any) -> None:
        self._console.print(val)

    def print_interrupted(self, exc_info: ExcInfo, *, show_traceback: bool = False) -> None:
        message = f"!!! Interrupted by “{exc_info.value!r}“ !!!"
        spaces = " " * (len(message) - 6)
        multiline_message = "\n".join([
            "!!!" + spaces + "!!!",
            message,
            "!!!" + spaces + "!!!",
        ])
        self._console.out(multiline_message, style=Style(color="yellow"))
        if show_traceback:
            self.print_exception(exc_info)

    def print_report_summary(self, summary: List[str]) -> None:
        if len(summary) == 0:
            return
        text = "# " + "\n# ".join(summary)
        self._console.out(text, style=Style(color="grey70"))

    def print_report_stats(self, *, total: int, passed: int, failed: int, skipped: int,
                           elapsed: float, is_interrupted: bool = False) -> None:
        if is_interrupted or (failed > 0 or passed == 0):
            style = Style(color="red", bold=True)
        else:
            style = Style(color="green", bold=True)

        scenarios = "scenario" if (total == 1) else "scenarios"
        self._console.out(f"# {total} {scenarios}, "
                          f"{passed} passed, {failed} failed, {skipped} skipped",
                          style=style, end="")
        self._console.out(f" ({elapsed:.2f}s)", style=Style(color="blue"))

    def print_empty_line(self) -> None:
        self._console.out(" ")

    def print(self, smth: Any, *, end: str = "\n") -> None:
        self._console.out(smth, end=end)

    def show_spinner(self, status: RenderableType = "") -> None:
        if self._scenario_spinner:
            self.hide_spinner()
        self._scenario_spinner = self._console.status(status)
        self._scenario_spinner.start()

    def hide_spinner(self) -> None:
        if self._scenario_spinner:
            self._scenario_spinner.stop()
            self._scenario_spinner = None
