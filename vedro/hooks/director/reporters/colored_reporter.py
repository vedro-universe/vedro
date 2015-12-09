import json
from traceback import format_exception
from colorama import init, Fore, Style
from ..reporter import Reporter


class ColoredReporter(Reporter):

  def __get_representation(self, obj):
    try:
      representation = json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception as e:
      return repr(obj)
    return representation

  def __print_dict(self, dictionary):
    for key, value in dictionary.items():
      print(Fore.BLUE + ' {}:'.format(key),
            Fore.RESET + '{}'.format(self.__get_representation(value)))

  def _on_setup(self, event):
    super()._on_setup(event)
    self._prev_namespace = None
    init(autoreset=True)
    print(Style.BRIGHT + self._target)

  def _on_scenario_run(self, event):
    super()._on_scenario_run(event)
    namespace = event.scenario.namespace
    namespace = namespace.replace('_', ' ').replace('/', ' / ')
    if (namespace is not None) and (namespace != self._prev_namespace):
      self._prev_namespace = namespace
      print(Style.BRIGHT + '* {}'.format(namespace))

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    print(Fore.RED + ' ✗ {}\n'.format(event.scenario.subject))
    exception = ''.join(format_exception(*event.scenario.exception))
    if event.scenario.errors:
      print(Fore.YELLOW + exception + ' - ' + '\n - '.join(event.scenario.errors))
    else:
      print(Fore.YELLOW + exception, end='')
    if 'scope' in event.scenario.scope:
      print(Style.BRIGHT + Fore.BLUE + '\nScope:')
      self.__print_dict(event.scenario.scope['scope'])

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    print(Fore.GREEN + ' ✔ {}'.format(event.scenario.subject))

  def _on_scenario_skip(self, event):
    super()._on_scenario_skip(event)
    print(Style.BRIGHT + Fore.YELLOW + ' » ', end='')
    print(Fore.YELLOW + event.scenario.subject)

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    style, color = Style.BRIGHT, Fore.GREEN if (self._failed == 0) else Fore.RED
    print(style + color + '\n# {total} scenario{s}, {failed} failed, {skipped} skipped'.format(
      total=self._total,
      failed=self._failed,
      skipped=self._skipped,
      s='' if (self._total == 1) else 's'
    ))
