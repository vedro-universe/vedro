import json
from configparser import ConfigParser, ExtendedInterpolation


class Config:

  _main_namespace = 'main'

  def __init__(self, defaults = {}):
    self._parser = ConfigParser(interpolation=ExtendedInterpolation())
    self._parser.read_dict(defaults)

  def read(self, cfg):
    if type(cfg) is str:
      self._parser.read(cfg)
    else:
      self._parser.read_dict(cfg)
    return self

  def keys(self, namespace = _main_namespace):
    return self._parser[namespace].keys()

  def sections(self):
    return self._parser.sections()

  def __getitem__(self, key):
    return self.__getattr__(key)

  def __getattr__(self, name):
    if name in self._parser:
      return self._parser[name]
    if name in self._parser[self._main_namespace]:
      return self._parser[self._main_namespace][name]
    raise KeyError(name)

  def to_dict(self):
    result = {}
    for section in self._parser.sections():
      result[section] = {}
      for key, val in self._parser[section].items():
        result[section][key] = val
    return result

  def __repr__(self):
    config = json.dumps(self.to_dict(), indent=4, ensure_ascii=False, sort_keys=True, default=str)
    return 'Config({})'.format(config)
