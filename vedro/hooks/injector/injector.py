import builtins
import importlib
import os
from ..hook import Hook
from ...core import Scope
from ...helpers.decorators import static


class Injector(Hook):

  def __get_packages(self, config):
    packages = config['vedro']['support'].strip().split()
    return [package for package in packages if os.path.exists(package)]

  def __get_package_files(self, package_path):
    package_files = []
    for filename in os.listdir(package_path):
      if filename.endswith('.py') and not filename.startswith('_'):
        package_files += [filename]
    return package_files

  def __get_module_variables(self, module_name):
    module = importlib.import_module(module_name)
    variables = {}
    for variable in dir(module):
      if not variable.startswith('_'):
        variables[variable] = getattr(module, variable)
    return variables

  def __inject_variables(self, variables):
    for variable in variables:
      setattr(builtins, variable, variables[variable])

  def __on_init(self, event):
    self.__inject_variables({'Scope': Scope, 'static': static})
    if 'globals' in event.kwargs:
      self.__inject_variables(event.kwargs['globals'])

  def __on_config_load(self, event):
    self.__inject_variables({'cfg': event.config})
    for package in self.__get_packages(event.config):
      for package_file in self.__get_package_files(package):
        module_name = package + '.' + os.path.splitext(package_file)[0]
        module_variables = self.__get_module_variables(module_name)
        self.__inject_variables(module_variables)

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('config_load', self.__on_config_load)
