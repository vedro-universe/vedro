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
    raise KeyError()
