from collections import OrderedDict


class Scope(OrderedDict):

  def __init__(self, *args, **kwargs):
    self.__keys = OrderedDict(*args, **kwargs)

  def __setitem__(self, key, value):
    self.__keys[key] = value

  def __getitem__(self, key):
    if key not in self.__keys:
      raise KeyError('Scope key "{}" is not found'.format(key))
    return self.__keys[key]

  def __setattr__(self, key, value):
    if key == '_' + self.__class__.__name__ + '__keys':
      super().__setattr__(key, value)
    else:
      self[key] = value

  def __getattr__(self, key):
    if key == '_' + self.__class__.__name__ + '__keys':
      return super().__getattr__(key, value)
    elif key in self.__keys:
      return self[key]
    else:
      raise KeyError('Scope key "{}" is not found'.format(key))

  def __delitem__(self, key):
    return self.__keys.__delitem__(key)

  def __delattr__(self, key):
    del self[key]

  def get(self, key, default=None):
    return self.__keys.get(key, default)

  def keys(self):
    return self.__keys.keys()

  def __contains__(self, key):
    return self.__keys.__contains__(key)

  def __iter__(self):
    return self.__keys.__iter__()

  def __next__(self):
    return self.__keys.__next__()

  def __str__(self):
    keys = ['{}={}'.format(key, repr(value)) for key, value in self.__keys.items()]
    return '{}({})'.format(self.__class__.__name__, ', '.join(keys))
