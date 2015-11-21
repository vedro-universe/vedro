import os
from ..hook import Hook


class Environ(Hook):

  def __on_config_load(self, event):
    env = {key: value for key, value in os.environ.items() if '$' not in value}
    event.config.read({'env': env})
  
  def subscribe(self, events):
    events.listen('config_load', self.__on_config_load)
