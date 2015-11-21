import os
from ..hook import Hook


class Packagist(Hook):

  def __get_packages(self, config):
    packages = config['vedro']['support'].strip().split()
    return [package for package in packages if os.path.exists(package)]

  def __get_package_files(self, package_path):
    package_files = []
    for filename in os.listdir(package_path):
      if filename.endswith('.py') and not filename.startswith('_'):
        package_files += [filename]
    return package_files

  def __make_init_file(self, package_files):
    return '\n'.join(['from .{} import *'.format(x[:-3]) for x in package_files]) + '\n'

  def __on_config_load(self, event):
    self.packages = self.__get_packages(event.config)
    for package in self.packages:
      package_files = self.__get_package_files(package)
      with open(os.path.join(package, '__init__.py'), 'w') as init_file:
        init_file.write(self.__make_init_file(package_files))

  def __on_cleanup(self, event):
    for package in self.packages:
      path = os.path.join(package, '__init__.py')
      if os.path.exists(path):
        os.remove(path)

  def subscribe(self, events):
    events.listen('config_load', self.__on_config_load)
    events.listen('cleanup', self.__on_cleanup)
