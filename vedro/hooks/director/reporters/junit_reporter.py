import xml.etree.ElementTree as etree
from collections import OrderedDict
from traceback import format_exception
from ..reporter import Reporter


class JUnitReporter(Reporter):

  def _on_setup(self, event):
    super()._on_setup(event)
    self._namespaces = OrderedDict()
    self._namespace = None

  def _set_namespace(self, namespace):
    namespace = namespace.replace('_', ' ').replace('/', ' / ')
    if (namespace is not None) and (namespace != self._namespace):
      self._namespaces[namespace] = {
        'id': len(self._namespaces),
        'subject': namespace,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'scenarios': []
      }
      self._namespace = namespace

  def _on_scenario_skip(self, event):
    super()._on_scenario_skip(event)
    self._set_namespace(event.scenario.namespace)
    self._namespaces[self._namespace]['skipped'] += 1
    self._namespaces[self._namespace]['scenarios'] += [event.scenario]

  def _on_scenario_run(self, event):
    super()._on_scenario_run(event)
    self._set_namespace(event.scenario.namespace)

  def _on_scenario_pass(self, event):
    super()._on_scenario_pass(event)
    self._namespaces[self._namespace]['passed'] += 1
    self._namespaces[self._namespace]['scenarios'] += [event.scenario]

  def _on_scenario_fail(self, event):
    super()._on_scenario_fail(event)
    self._namespaces[self._namespace]['failed'] += 1
    self._namespaces[self._namespace]['scenarios'] += [event.scenario]

  def _on_cleanup(self, event):
    super()._on_cleanup(event)
    root = etree.Element('root')
    testsuites = etree.SubElement(root, 'testsuites',
      name=self._target,
      tests=str(self._passed),
      failures=str(self._failed)
    )
    for name, namespace in self._namespaces.items():
      testsuite = etree.SubElement(testsuites, 'testsuite',
        id=str(namespace['id']),
        name=namespace['subject'],
        tests=str(namespace['passed']),
        failures=str(namespace['failed']),
        skipped=str(namespace['skipped'])
      )
      for scenario in namespace['scenarios']:
        testcase = etree.SubElement(testsuite, 'testcase',
          name=scenario.subject,
          classname=namespace['subject'] + ' / ' + scenario.subject
        )
        if scenario.skipped:
          etree.SubElement(testcase, 'skipped')
        elif scenario.failed:
          exception = ''.join(format_exception(*scenario.exception))
          if scenario.errors:
            exception += ' - ' + '\n - '.join(scenario.errors)
          message, type = str(scenario.exception[1]), scenario.exception[0].__name__
          etree.SubElement(testcase, 'failure', message=message, type=type).text = exception

    print('<?xml version="1.0" encoding="UTF-8"?>')
    etree.dump(testsuites)
