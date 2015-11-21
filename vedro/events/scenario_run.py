from .event import Event


class ScenarioRunEvent(Event):

  def __init__(self, scenario):
    self.scenario = scenario
