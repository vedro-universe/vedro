from .event import Event


class ScenarioSkipEvent(Event):

  def __init__(self, scenario):
    self.scenario = scenario
