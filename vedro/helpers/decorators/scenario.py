from functools import partial
from itertools import count


class scenario:

  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

  def __generate_name(self, fn):
    for i in count():
      name = self.__class__.__name__ + str(i + 1)
      if name not in fn.__globals__:
        return name

  def __call__(self, fn):
    name = self.__generate_name(fn)
    wrapper = partial(fn, *self.args, **self.kwargs)
    wrapper.__tags__ = getattr(self, "__tags__", [])
    wrapper.__name__ = name
    wrapper.__globals__ = fn.__globals__
    wrapper.__code__ = fn.__code__
    fn.__globals__[name] = wrapper
    return fn

class skip_scenario(scenario): pass
class only_scenario(scenario): pass
