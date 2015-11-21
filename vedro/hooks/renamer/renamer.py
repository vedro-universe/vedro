import os
from ..hook import Hook


class Renamer(Hook):

  def __on_scenario_load(self, event):
    scenario = event.scenario
    directory, basename = os.path.split(scenario.path)
    filename, ext = os.path.splitext(basename)
    expected_filename = scenario.subject.replace(' ', '_')
    if filename != expected_filename:
      new_path = os.path.join(directory, expected_filename + ext)
      os.rename(scenario.path, new_path)
  
  def subscribe(self, events):
    events.listen('scenario_load', self.__on_scenario_load)
