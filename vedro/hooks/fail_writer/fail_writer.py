from ..hook import Hook


class FailWriter(Hook):
  def __init__(self, dispatcher, arg_parser):
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-l', '--log-failed', action='store_true')

  def __on_arg_parse(self, event):
    self._log_failed = event.args.log_failed or []

  def __on_setup(self, event):
    if(self._log_failed):
      self.__file = open('last_failed.report', 'w')

  def __on_scenario_fail(self, event):
    if(self._log_failed):
      print(event.scenario.subject, file=self.__file)

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('setup', self.__on_setup)
    events.listen('scenario_fail', self.__on_scenario_fail, 9999)
