import valeera
from district42 import SchemaType
from ..hook import Hook


class Validator(Hook):

  def __validate(self, a, b):
    self._validator = valeera.Validator(valeera.Formatter()).validate(b, a)
    return self._validator.passes()

  def __on_setup(self, event):
    self._validator = None
    SchemaType.__eq__ = lambda a, b: self.__validate(a, b)

  def __on_scenario_fail(self, event):
    event.scenario.errors = self._validator.errors() if self._validator else []

  def subscribe(self, events):
    events.listen('setup', self.__on_setup)
    events.listen('scenario_fail', self.__on_scenario_fail, 9999)
