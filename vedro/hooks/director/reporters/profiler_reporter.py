import json
import os
import time
from traceback import format_exception
from colorama import init, Fore, Style
from ..reporter import Reporter


class ProfilerReporter(Reporter):

  def _on_setup(self, event):
    super()._on_setup(event)
    self._prev_namespace = None
    init(autoreset=True, strip=os.name == 'nt')
    print(Style.BRIGHT + self._target)
    self._start_time = time.monotonic()

  def _on_scenario_run(self, event):
    super()._on_scenario_run(event)
    namespace = event.scenario.namespace
    namespace = namespace.replace('_', ' ').replace('/', ' / ')
    if (namespace is not None) and (namespace != self._prev_namespace):
      self._prev_namespace = namespace
      print(Style.BRIGHT + '* {}'.format(namespace))
    self._scenario_start_time = time.monotonic()
    self._step_start_time = self._scenario_start_time

  def _on_step_pass(self, event):
    super()._on_step_pass(event)
    event.step.elapsed = time.monotonic() - self._step_start_time
    self._step_start_time = time.monotonic()

  def _on_step_fail(self, event):
    super()._on_step_fail(event)
    event.step.elapsed = time.monotonic() - self._step_start_time
    self._step_start_time = time.monotonic()

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    print(Fore.RED + '  ✗ {}'.format(event.scenario.subject), end='')
    print(Fore.BLUE + ' ({:.2f}s)'.format(time.monotonic() - self._scenario_start_time))

    if self._verbosity > 0:
      for step in event.scenario.steps:
        if step.failed:
          print(Fore.RED + '    ✗ {}'.format(step.name), end='')
          print(Fore.BLUE + ' ({:.2f}s)'.format(step.elapsed))
          break
        else:
          print(Fore.RED + '    ✔ {}'.format(step.name), end='')
          print(Fore.BLUE + ' ({:.2f}s)'.format(step.elapsed))

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    print(Fore.GREEN + '  ✔ {}'.format(event.scenario.subject), end='')
    print(Fore.BLUE + ' ({:.2f}s)'.format(time.monotonic() - self._scenario_start_time))

    if self._verbosity > 0:
      for step in event.scenario.steps:
        if step.failed:
          print(Fore.RED + '    ✗ {}'.format(step.name), end='')
          print(Fore.BLUE + ' ({:.2f}s)'.format(step.elapsed))
          break
        else:
          print(Fore.GREEN + '    ✔ {}'.format(step.name), end='')
          print(Fore.BLUE + ' ({:.2f}s)'.format(step.elapsed))

  def _on_scenario_skip(self, event):
    super()._on_scenario_skip(event)

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    style = Style.BRIGHT
    color = Fore.GREEN if (self._failed == 0 and self._passed > 0) else Fore.RED
    print(style + color + '\n# {total} scenario{s}, {failed} failed, {skipped} skipped, '.format(
      total=self._total,
      failed=self._failed,
      skipped=self._skipped,
      s='' if (self._total == 1) else 's'
    ), end='')
    print(style + Fore.BLUE + '({:.2f}s)'.format(time.monotonic() - self._start_time))
