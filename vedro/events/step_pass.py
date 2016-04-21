from .event import Event


class StepPassEvent(Event):

  def __init__(self, step):
    self.step = step
