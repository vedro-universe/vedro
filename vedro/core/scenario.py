from enum import Enum


class Scenario:

  class Status(Enum):
    Passed, Failed, Skipped = range(3)

  def __init__(self, path = None, namespace = None):
    self.path = path
    self.namespace = namespace
    self.priority = 0
    self.subject = None
    self.scope = None
    self.fn = None
    self.steps = None
    self.status = None
    self.exception = None

  @property
  def passed(self):
    return self.status == self.Status.Passed

  def mark_passed(self):
    self.status = self.Status.Passed

  @property
  def failed(self):
    return self.status == self.Status.Failed

  def mark_failed(self):
    self.status = self.Status.Failed
  
  @property
  def skipped(self):
    return self.status == self.Status.Skipped

  def mark_skipped(self):
    self.status = self.Status.Skipped
