import os
from ..hook import Hook


class Packagist(Hook):

  def __get_files(self, path):
    files = []
    for filename in os.listdir(path):
      if (not filename.startswith('_')) and (not filename.startswith('.')):
        files += [filename[:-3] if filename.endswith('.py') else filename]
    return files

  def __get_directories(self, path):
    directories = []
    for filename in os.listdir(path):
      filename = os.path.join(path, filename)
      if not filename.endswith('_') and os.path.isdir(filename):
        directories += [filename]
    return directories

  def __make_init_file(self, files):
    return '\n'.join(['from .{} import *'.format(x) for x in files]) + '\n'

  def __generate_init_files(self, directories):
    for directory in directories:
      files = self.__get_files(directory)
      self.__generate_init_files(self.__get_directories(directory))
      with open(os.path.join(directory, '__init__.py'), 'w') as init_file:
        init_file.write(self.__make_init_file(files))

  def __on_config_load(self, event):
    supported_directories = event.config['vedro']['support'].strip().split()
    self.directories = [x for x in supported_directories if os.path.exists(x)]
    self.__generate_init_files(self.directories)

  def __on_cleanup(self, event):
    for directory in self.directories:
      for path, _, files in os.walk(directory):
        init_file = os.path.join(path, '__init__.py')
        if os.path.exists(init_file): os.remove(init_file)

  def subscribe(self, events):
    events.listen('config_load', self.__on_config_load)
    # events.listen('cleanup', self.__on_cleanup)
