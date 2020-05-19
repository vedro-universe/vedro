from ..hook import Hook


class Tagger(Hook):

  def __init__(self, dispatcher, arg_parser):
    self._dispatcher = dispatcher
    self._arg_parser = arg_parser

  def __on_init(self, *args, **kwargs):
    self._arg_parser.add_argument('-t', '--tags', nargs='+')

  def __on_arg_parse(self, event):
    self._tags = set(map(str.upper, event.args.tags)) if event.args.tags else set()

  def __on_setup(self, event):
    if len(self._tags) == 0:
      return
    for scenario in event.scenarios:
      if len(self._tags & scenario.tags) == 0:
        scenario.mark_skipped()

  def subscribe(self, events):
    events.listen('init', self.__on_init)
    events.listen('arg_parse', self.__on_arg_parse)
    events.listen('setup', self.__on_setup)
