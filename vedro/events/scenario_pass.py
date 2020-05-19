from .event import Event


class ScenarioPassEvent(Event):

  def __init__(self, scenario):
    self.scenario = scenario
