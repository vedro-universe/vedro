from functools import wraps


class static(object):
  
  def __init__(self, cls):
    self.cls = cls

  def __getattribute__(self, name):
    cls = object.__getattribute__(self, 'cls')
    fn = getattr(cls, name)
    @wraps(fn)
    def wrapper(*args, **kwargs):
      return fn(cls, *args, **kwargs)
    return wrapper
