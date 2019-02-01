import random
from uuid import uuid4

from ..hook import Hook


class Seeder(Hook):
  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('--launch_id', nargs='?')

  def __on_arg_parse(self, event):
    self._root_seed = event.args.launch_id
    if self._root_seed is None:
      self._root_seed = str(uuid4())

  def __on_setup(self, event):
    random.seed(self._root_seed)

    def key_fn(scenario):
      parts = scenario.path.split('/')
      return (len(parts), [(len(x), x) for x in parts])
    scenarios = sorted(event.scenarios, key=key_fn)

    self._namespaces = {}
    for scenario in scenarios:
      if scenario.namespace not in self._namespaces:
        self._namespaces[scenario.namespace] = random.randint(1, 2**63 - 1)

    prev_namespace = None
    self._scenarios = {}
    for scenario in scenarios:
      if scenario.namespace != prev_namespace:
        seed = self._namespaces[scenario.namespace]
        random.seed(seed)
        prev_namespace = scenario.namespace
      self._scenarios[scenario] = random.randint(1, 2**63 - 1)

    self._failed = 0

  def _on_scenario_run(self, event):
    seed = self._scenarios[event.scenario]
    random.seed(seed)

  def _on_scenario_fail(self, event):
    self._failed += 1

  def _on_cleanup(self, event):
    if self._failed > 0:
      print('> To reproduce these results, '
            'run tests with "--launch_id={}" parameter'.format(self._root_seed))

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('setup', self.__on_setup)
    events.listen('scenario_run', self._on_scenario_run)
    events.listen('scenario_fail', self._on_scenario_fail)
    events.listen('cleanup', self._on_cleanup, priority=-1)
