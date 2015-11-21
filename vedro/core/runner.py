import sys
import os
import importlib
import inspect
from .profiler import Profiler
from .scenario import Scenario


class Runner:

  def __discover_scenarios(self, root):
    scenarios = []
    for path, _, files in os.walk(root):
      if path.endswith('_'): continue
      namespace = path[len(root) + 1:]
      scenarios += [Scenario(os.path.join(path, filename), namespace) for filename in files]
    return scenarios

  def __load_scenario(self, module_name):
    module = importlib.import_module(module_name)
    variables = [x for x in dir(module) if x.endswith('scenario')]
    if len(variables) != 1:
      raise Exception('File {} must have at least one scenario'.format(scenario.path))
    return getattr(module, variables[0])

  def __get_steps(self, fn, scope):
    return [scope[x.co_name] for x in fn.__code__.co_consts if inspect.iscode(x)]

  def discover(self, root):
    return self.__discover_scenarios(root)

  def load(self, scenario):
    module_name = os.path.splitext(scenario.path)[0].replace('/', '.')
    scenario.fn = self.__load_scenario(module_name)
    profiler = Profiler().register()
    try:
      scenario.fn()
    finally:
      profiler.deregister()
    scenario.scope = profiler.get_locals()
    scenario.subject = scenario.scope['subject']
    scenario.steps = self.__get_steps(scenario.fn, scenario.scope)

  def run(self, scenario):
    for step in scenario.steps:
      try:
        step()
      except Exception as e:
        scenario.exception = sys.exc_info()
        return scenario.mark_failed()
    return scenario.mark_passed()
