from .event import Event


class ArgParseEvent(Event):

  def __init__(self, args):
    self.args = args
