from .event import Event


class StepFailEvent(Event):

  def __init__(self, step):
    self.step = step
