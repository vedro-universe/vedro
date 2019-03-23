import os
import sys
import argparse
import builtins

from .core import Dispatcher, Config, Runner, Scope
from .helpers import scenario, skip_scenario, only_scenario
from .hooks import *
from .events import *


os.chdir(os.path.dirname(os.path.join(os.getcwd(), sys.argv[0])))

config = Config({
  'main': {
    'target': os.path.basename(os.getcwd()),
  },
})

_runner = Runner()
_dispatcher = Dispatcher()
_arg_parser = argparse.ArgumentParser()

get_current_scope = lambda: _runner.get_current_scope()
get_current_step = lambda: _runner.get_current_step()

def run(*args, **kwargs):
  _dispatcher.register(Director(_dispatcher, _arg_parser))
  _dispatcher.register(Interrupter(_dispatcher, _arg_parser))
  _dispatcher.register(Skipper(_dispatcher, _arg_parser))
  _dispatcher.register(Environ(_dispatcher, _arg_parser))
  _dispatcher.register(Seeder(_dispatcher, _arg_parser))
  _dispatcher.register(Packagist())
  _dispatcher.register(Validator())
  _dispatcher.register(Terminator())

  _dispatcher.fire(InitEvent(*args, **kwargs))

  args = _arg_parser.parse_args()
  _dispatcher.fire(ArgParseEvent(args))

  config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'vedro.cfg')
  config.read(config_path)

  if os.path.exists(config['vedro']['config']):
    config.read(config['vedro']['config'])
  _dispatcher.fire(ConfigLoadEvent(config))

  scenarios = _runner.discover(config['vedro']['scenarios'])
  _dispatcher.fire(SetupEvent(scenarios))

  for scenario in scenarios:
    if scenario.skipped:
      _dispatcher.fire(ScenarioSkipEvent(scenario))
      continue
    _dispatcher.fire(ScenarioRunEvent(scenario))
    for step in _runner.run(scenario):
      if step.failed:
        _dispatcher.fire(StepFailEvent(step))
      else:
        _dispatcher.fire(StepPassEvent(step))
    if scenario.failed:
      _dispatcher.fire(ScenarioFailEvent(scenario))
    else:
      _dispatcher.fire(ScenarioPassEvent(scenario))

  _dispatcher.fire(CleanupEvent())
  _dispatcher.forget()
