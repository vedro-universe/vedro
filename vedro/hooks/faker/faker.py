from district42 import SchemaType
from blahblah import Substitutor

from ..hook import Hook


class Faker(Hook):

  def __on_setup(self, event):
    SchemaType.__mod__ = lambda self, val: self.accept(Substitutor(), val)

  def subscribe(self, events):
    events.listen('setup', self.__on_setup)
