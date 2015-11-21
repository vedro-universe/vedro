import sys


class Profiler:

  def __init__(self):
    self._locals = None

  def __tracer(self, frame, event, arg):
    if event == 'return':
      self._locals = frame.f_locals.copy()

  def get_locals(self):
    return self._locals

  def register(self):
    sys.setprofile(self.__tracer)
    return self

  def deregister(self):
    sys.setprofile(None)
    return self
