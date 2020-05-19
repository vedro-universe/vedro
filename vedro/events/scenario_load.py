from .event import Event


class ScenarioLoadEvent(Event):

  def __init__(self, scenario):
    self.scenario = scenario
