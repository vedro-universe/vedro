import argparse
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Sequence, Tuple

__all__ = ("CommandArgumentParser",)


class CommandArgumentParser(ArgumentParser):
    def parse_known_args(self, args: Optional[Sequence[str]] = None,
                         namespace: Optional[Namespace] = None) -> Tuple[Namespace, List[str]]:
        if args is None:
            # $ prog command <...>
            args = sys.argv[2:]
        else:
            args = list(args)

        return super().parse_known_args(args, namespace)

    def add_help_action(self) -> None:
        self.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    # https://github.com/python/cpython/issues/95073
    def remove_help_action(self) -> None:
        for action in self._actions:
            if not isinstance(action, argparse._HelpAction):
                continue
            self._remove_action(action)
            for option_string in action.option_strings:
                del self._option_string_actions[option_string]
