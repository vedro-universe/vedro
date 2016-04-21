from ..hook import Hook


class Reporter(Hook):

  def __init__(self, verbosity):
    self._verbosity = verbosity

  def _on_config_load(self, event):
    self._target = event.config['target']

  def _on_setup(self, event):
    self._passed = 0
    self._failed = 0
    self._skipped = 0
    self._total = 0

  def _on_scenario_run(self, event):
    pass

  def _on_step_pass(self, event):
    pass

  def _on_step_fail(self, event):
    pass

  def _on_scenario_pass(self, event):
    self._total += 1
    self._passed += 1

  def _on_scenario_fail(self, event):
    self._total += 1
    self._failed += 1

  def _on_scenario_skip(self, event):
    self._total += 1
    self._skipped += 1

  def _on_cleanup(self, event):
    pass

  def subscribe(self, events):
    events.listen('config_load', self._on_config_load)
    events.listen('setup', self._on_setup)
    events.listen('scenario_run', self._on_scenario_run)
    events.listen('step_pass', self._on_step_pass)
    events.listen('step_fail', self._on_step_fail)
    events.listen('scenario_pass', self._on_scenario_pass)
    events.listen('scenario_fail', self._on_scenario_fail)
    events.listen('scenario_skip', self._on_scenario_skip)
    events.listen('cleanup', self._on_cleanup)
