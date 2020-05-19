from enum import Enum


class Step:

  class Status(Enum):
    Passed, Failed = range(2)

  def __init__(self, fn):
    self.name = fn.__name__
    self.fn = fn
    self.status = None

  @property
  def go(self):
    return self.fn

  @property
  def passed(self):
    return self.status == self.Status.Passed

  def mark_passed(self):
    self.status = self.Status.Passed
    return self

  @property
  def failed(self):
    return self.status == self.Status.Failed

  def mark_failed(self):
    self.status = self.Status.Failed
    return self
