import re
import heapq


class Dispatcher:

  def __init__(self):
    self._events = {}

  def __get_event_name(self, cls):
    cls_name = re.sub('(?!^)([A-Z]+)', r'_\1', cls.__name__)
    return cls_name.lower().replace('_event', '')

  def listen(self, event_name, handler, priority = 0):
    if event_name not in self._events:
      self._events[event_name] = []
    self._events[event_name] += [(priority, handler)]
    return self

  def register(self, subscriber):
    subscriber.subscribe(self)
    return self

  def forget(self):
    self._events = {}
    return self

  def fire(self, event):
    event_name = self.__get_event_name(event.__class__)
    if event_name in self._events:
      handlers = sorted(self._events[event_name], key=lambda x: x[0], reverse=True)
      for priority, handler in handlers:
        handler(event)
    return self
