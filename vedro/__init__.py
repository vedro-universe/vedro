import os
import sys
import argparse
import builtins
from .core import Dispatcher, Config, Runner, Scope
from .helpers import scenario, skip_scenario, only_scenario
from .hooks import *
from .events import *


os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

config = Config()

def run(*args, **kwargs):
  arg_parser = argparse.ArgumentParser()

  dispatcher = Dispatcher()
  dispatcher.register(Director(dispatcher, arg_parser))
  dispatcher.register(Interrupter(dispatcher, arg_parser))
  dispatcher.register(Skipper(dispatcher, arg_parser))
  dispatcher.register(Environ())
  dispatcher.register(Packagist())
  dispatcher.register(Validator())
  dispatcher.register(Terminator())
  dispatcher.register(FailWriter(dispatcher, arg_parser))

  dispatcher.fire(InitEvent(*args, **kwargs))

  args = arg_parser.parse_args()
  dispatcher.fire(ArgParseEvent(args))

  config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vedro.cfg')
  config.read(config_path)

  config.read(config['vedro']['config'])
  dispatcher.fire(ConfigLoadEvent(config))

  runner = Runner()
  scenarios = runner.discover(config['vedro']['scenarios'])
  dispatcher.fire(SetupEvent(scenarios))

  scenarios = sorted(scenarios, key=lambda x: x.priority, reverse=True)
  for scenario in scenarios:
    if scenario.skipped:
      dispatcher.fire(ScenarioSkipEvent(scenario))
      continue
    dispatcher.fire(ScenarioRunEvent(scenario))
    for step in runner.run(scenario):
      if step.failed:
        dispatcher.fire(StepFailEvent(step))
      else:
        dispatcher.fire(StepPassEvent(step))
    if scenario.failed:
      dispatcher.fire(ScenarioFailEvent(scenario))
    else:
      dispatcher.fire(ScenarioPassEvent(scenario))

  dispatcher.fire(CleanupEvent())
