from .scenario import scenario


class with_tags(scenario):
  def __init__(self, tags, scenario):
    self._tags = tags
    self._scenario = scenario

  def __call__(self, fn):
    self._scenario.__tags__ = self._tags
    self._scenario(fn)
    return fn
