import sys
from ..hook import Hook


class Terminator(Hook):

  def __on_setup(self, event):
    self.__failed = 0

  def __on_scenario_fail(self, event):
    self.__failed += 1

  def __on_cleanup(self, event):
    sys.exit(int(bool(self.__failed)))

  def subscribe(self, events):
    events.listen('setup', self.__on_setup)
    events.listen('scenario_fail', self.__on_scenario_fail)
    events.listen('cleanup', self.__on_cleanup, -1)
