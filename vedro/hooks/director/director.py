from ..hook import Hook
from .reporters import (
  SilentReporter,
  MinimalisticReporter,
  ColoredReporter,
  JUnitReporter,
  CommonReporter
)


class Director(Hook):

  reporters = {
    'silent': SilentReporter,
    'minimalistic': MinimalisticReporter,
    'colored': ColoredReporter,
    'junit': JUnitReporter,
    'common': CommonReporter
  }
  default = 'common'
  
  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-r', '--reporter',
      choices=self.reporters,
      default=self.default
    )

  def __on_arg_parse(self, event):
    self._reporter = event.args.reporter
    self._dispatcher.register(self.reporters[self._reporter]())

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
