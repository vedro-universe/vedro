import os
import sys
import argparse
import builtins
from .core import Dispatcher, Config, Runner
from .hooks import *
from .events import *


os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

def run(*args, **kwargs):
  arg_parser = argparse.ArgumentParser()

  dispatcher = Dispatcher()
  dispatcher.register(Director(dispatcher, arg_parser))
  dispatcher.register(Interrupter(dispatcher, arg_parser))
  dispatcher.register(Skipper(dispatcher, arg_parser))
  dispatcher.register(Environ())
  dispatcher.register(Packagist())
  dispatcher.register(Injector())
  dispatcher.register(Renamer())
  dispatcher.register(Validator())
  dispatcher.register(Terminator())

  dispatcher.fire(InitEvent(*args, **kwargs))

  args = arg_parser.parse_args()
  dispatcher.fire(ArgParseEvent(args))

  config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vedro.cfg')
  config = Config().read(config_path)

  config.read(config['vedro']['config'])
  dispatcher.fire(ConfigLoadEvent(config))

  runner = Runner()
  scenarios = runner.discover(config['vedro']['scenarios'])

  for scenario in scenarios:
    runner.load(scenario)
    dispatcher.fire(ScenarioLoadEvent(scenario))

  dispatcher.fire(SetupEvent(scenarios))

  scenarios = sorted(scenarios, key=lambda x: x.priority, reverse=True)
  for scenario in scenarios:
    if scenario.skipped:
      dispatcher.fire(ScenarioSkipEvent(scenario))
      continue
    dispatcher.fire(ScenarioRunEvent(scenario))
    runner.run(scenario)
    if scenario.failed:
      dispatcher.fire(ScenarioFailEvent(scenario))
    else:
      dispatcher.fire(ScenarioPassEvent(scenario))

  dispatcher.fire(CleanupEvent())
