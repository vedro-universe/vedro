import sys
import os
import importlib
import inspect
from .profiler import Profiler
from .scenario import Scenario
from ..helpers import scenario as scenario_decorator


class Runner:

  def __discover_scenarios(self, root):
    scenarios = []
    for path, _, files in os.walk(root):
      if path.endswith('_'): continue
      namespace = path[len(root) + 1:]
      for filename in files:
        scenarios += self.__load_scenarios(os.path.join(path, filename), namespace)
    return scenarios

  def __build_scenario(self, path, namespace, fn):
    profiler = Profiler().register()
    try:
      fn()
    finally:
      profiler.deregister()
    scope = profiler.get_locals()
    steps = [scope[x.co_name] for x in fn.__code__.co_consts if inspect.iscode(x)]
    return Scenario(path, namespace, fn, scope, scope['subject'], steps)

  def __load_scenarios(self, path, namespace):
    module = importlib.import_module(os.path.splitext(path)[0].replace('/', '.'))
    variables = [x for x in dir(module) if 'scenario' in x]
    if len(variables) == 0:
      raise Exception('File {} must have at least one scenario'.format(path))
    scenarios = []
    for v in variables:
      fn = getattr(module, v)
      if fn != scenario_decorator:
        scenarios += [self.__build_scenario(path, namespace, fn)]
    return scenarios

  def discover(self, root):
    return self.__discover_scenarios(root)

  def run(self, scenario):
    for step in scenario.steps:
      try:
        step()
      except Exception as e:
        scenario.exception = sys.exc_info()
        return scenario.mark_failed()
    return scenario.mark_passed()
