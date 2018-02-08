import os
from dotenv import load_dotenv
from ..hook import Hook


class Environ(Hook):

  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-e', '--env', nargs='*')

  def __on_arg_parse(self, event):
    self._env_files = event.args.env

  def __on_config_load(self, event):
    if self._env_files is not None:
      for env_file in self._env_files:
        load_dotenv(env_file, verbose=True, override=True)
    env = {key: value for key, value in os.environ.items() if '$' not in value}
    event.config.read({'env': env})
  
  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('config_load', self.__on_config_load)
