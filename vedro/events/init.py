from .event import Event


class InitEvent(Event):
  
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs
