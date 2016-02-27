from ..hook import Hook


class Skipper(Hook):

  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-s', '--scenarios', nargs='+')
    self._arg_parser.add_argument('-i', '--ignore', nargs='+')

  def __on_arg_parse(self, event):
    self._ignored = event.args.ignore or []
    self._specified = event.args.scenarios or []

  def __on_config_load(self, event):
    prefix = event.config['vedro']['scenarios'] + '/'
    self._ignored = [self.__normalize_scenario_name(x, prefix) for x in self._ignored]
    self._specified = [self.__normalize_scenario_name(x, prefix) for x in self._specified]

  def __normalize_scenario_name(self, name, prefix=''):
    if name.startswith(prefix):
      name = name[len(prefix):]
    return name.rsplit('.', 1)[0].replace(' / ', '/').replace(' ', '_')

  def __is_scenario_ignored(self, scenario):
    for x in self._ignored:
      if scenario.unique_name.startswith(x):
        return True
    return False

  def __is_scenario_specified(self, scenario):
    for x in self._specified:
      if scenario.unique_name.startswith(x):
        return True
    return False

  def __is_scenario_special(self, scenario):
    return scenario.fn.__name__.startswith('only')

  def __is_scenario_skipped(self, scenario):
    return scenario.fn.__name__.startswith('skip')

  def __on_setup(self, event):
    self._scenario_list = event.scenarios
    [x.mark_skipped() for x in self._scenario_list if self.__is_scenario_ignored(x)]
    if len(self._specified) > 0:
      [x.mark_skipped() for x in self._scenario_list if not self.__is_scenario_specified(x)]

    special_scenarios = [x for x in self._scenario_list if self.__is_scenario_special(x) and not x.skipped]
    if len(special_scenarios) > 0:
      [x.mark_skipped() for x in self._scenario_list if not self.__is_scenario_special(x)]
    
    for x in self._scenario_list:
      if self.__is_scenario_skipped(x) and (x.unique_name not in self._specified):
        x.mark_skipped()

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('config_load', self.__on_config_load)
    events.listen('setup', self.__on_setup)
