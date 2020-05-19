import sys
from ..hook import Hook


class Terminator(Hook):

  def __on_setup(self, event):
    self._passed = 0
    self._failed = 0

  def _on_scenario_pass(self, event):
    self._passed += 1

  def __on_scenario_fail(self, event):
    self._failed += 1

  def __on_cleanup(self, event):
    if self._failed > 0 or self._passed == 0:
      sys.exit(1)
    else:
      sys.exit(0)

  def subscribe(self, events):
    events.listen('setup', self.__on_setup)
    events.listen('scenario_pass', self._on_scenario_pass)
    events.listen('scenario_fail', self.__on_scenario_fail)
    events.listen('cleanup', self.__on_cleanup, -1)
