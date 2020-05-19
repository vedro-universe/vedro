from .event import Event


class ConfigLoadEvent(Event):

  def __init__(self, config):
    self.config = config
