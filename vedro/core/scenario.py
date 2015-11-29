from enum import Enum


class Scenario:

  class Status(Enum):
    Passed, Failed, Skipped = range(3)

  def __init__(self, path, namespace, fn, scope, subject, steps):
    self.priority = 0
    self.path = path
    self.namespace = namespace
    self.fn = fn
    self.subject = subject
    self.scope = scope
    self.steps = steps
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
