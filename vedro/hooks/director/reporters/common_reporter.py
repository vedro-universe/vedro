from colorama import init, Fore, Style
from ..reporter import Reporter


class CommonReporter(Reporter):

  def __init__(self):
    self._prev_namespace = None

  def _on_setup(self, event):
    super()._on_setup(event)
    self._prev_namespace = None
    init(autoreset=True)
    print(Style.BRIGHT + self._target)

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    print(Fore.RED + ' ✗ {}'.format(event.scenario.subject))

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    print(Fore.GREEN + ' ✔ {}'.format(event.scenario.subject))

  def _on_scenario_skip(self, event):
    super()._on_scenario_pass(event)
    print(Fore.LIGHTYELLOW_EX + ' » {}'.format(event.scenario.subject))

  def _on_scenario_run(self, event):
    super()._on_scenario_run(event)
    namespace = event.scenario.namespace
    namespace = namespace.replace('_', ' ').replace('/', ' / ')
    if (namespace is not None) and (namespace != self._prev_namespace):
      self._prev_namespace = namespace
      print(Style.BRIGHT + '* {}'.format(namespace))

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    print('\n# {total} scenario{s}, {failed} failed, {skipped} skipped'.format(
      total=self._total,
      failed=self._failed,
      skipped=self._skipped,
      s='' if (self._total == 1) else 's'
    ))
