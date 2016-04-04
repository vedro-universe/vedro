from ..reporter import Reporter


class MinimalisticReporter(Reporter):

  def _on_setup(self, event):
    super()._on_setup(event)
    print(self._target)

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    print(' ✗ {}'.format(event.scenario.subject))

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    print(' ✔ {}'.format(event.scenario.subject))

  def _on_scenario_skip(self, event):
    super()._on_scenario_skip(event)
    # print(' » {}'.format(event.scenario.subject))

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    print('\n# {total} scenario{s}, {failed} failed, {skipped} skipped'.format(
      total=self._total,
      failed=self._failed,
      skipped=self._skipped,
      s='' if (self._total == 1) else 's'
    ))
