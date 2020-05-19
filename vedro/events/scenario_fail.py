from .event import Event


class ScenarioFailEvent(Event):

  def __init__(self, scenario):
    self.scenario = scenario
