from ..hook import Hook


class Interrupter(Hook):

  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('--let-it-crash',
      action='store_true',
      default=False
    )

  def __on_arg_parse(self, event):
    self._let_it_crash = event.args.let_it_crash

  def __on_setup(self, event):
    self._scenarios = event.scenarios

  def __on_scenario_fail(self, event):
    if self._let_it_crash:
      self.__skip_remaining()

  def __skip_remaining(self):
    for scenario in self._scenarios:
      scenario.mark_skipped()

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('setup', self.__on_setup)
    events.listen('scenario_fail', self.__on_scenario_fail)
