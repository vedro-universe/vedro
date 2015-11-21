from ..hook import Hook


class Skipper(Hook):

  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-n', '--namespace')
    self._arg_parser.add_argument('-s', '--scenario')

  def __on_arg_parse(self, event):
    self._namespace = event.args.namespace
    self._scenario = event.args.scenario
    if self._namespace is not None:
      self._namespace = self._namespace.replace(' ', '_').replace(' / ', '/')

  def __namespace_mismatch(self, scenario):
    return (self._namespace is not None) and (scenario.namespace != self._namespace)

  def __subject_mismatch(self, scenario):
    return (self._scenario is not None) and (scenario.subject != self._scenario)

  def __mark_all_skipped_except(self, only_scenario):
    for scenario in self._scenarios:
      if scenario != only_scenario:
        scenario.mark_skipped()

  def __on_setup(self, event):
    self._scenarios = event.scenarios
    for scenario in self._scenarios:
      if (self._namespace is None) and (self._scenario is None):
        if scenario.fn.__name__.startswith('skip'):
          scenario.mark_skipped()
        if scenario.fn.__name__.startswith('only'):
          return self.__mark_all_skipped_except(scenario)
      if self.__namespace_mismatch(scenario) or self.__subject_mismatch(scenario):
        scenario.mark_skipped()
  
  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('setup', self.__on_setup)
