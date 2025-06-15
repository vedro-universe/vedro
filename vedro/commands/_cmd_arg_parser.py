import argparse
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional, Sequence, Tuple

__all__ = ("CommandArgumentParser",)


class CommandArgumentParser(ArgumentParser):
    """
    Extends the default `argparse.ArgumentParser` to support custom behavior for
    parsing command-line arguments.
    """

    def parse_known_args(self, args: Optional[Sequence[str]] = None,  # type: ignore
                         namespace: Optional[Namespace] = None) -> Tuple[Namespace, List[str]]:
        """
        Parse the known arguments and return any unrecognized arguments.

        Overrides the default `parse_known_args` to adjust the default behavior.
        If `args` is `None`, the method uses command-line arguments starting from the third
        argument (e.g., after `$ prog command`).

        :param args: A sequence of arguments to parse. If `None`, defaults to `sys.argv[2:]`.
        :param namespace: An optional `Namespace` object to populate with parsed arguments.
        :return: A tuple containing the parsed arguments (`Namespace`) and a list of
                 unrecognized arguments.
        """
        if args is None:
            # Use arguments starting after `$ prog command <...>`
            args = sys.argv[2:]
        else:
            args = list(args)

        return super().parse_known_args(args, namespace)

    def add_help_action(self) -> None:
        """
        Add the standard help action (`-h` or `--help`) to the parser.

        This action displays the help message and exits the program when invoked.
        """
        self.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    # https://github.com/python/cpython/issues/95073
    def remove_help_action(self) -> None:
        """
        Remove the help action (`-h` or `--help`) from the parser.

        This method iterates through the parser's actions to identify the help action
        and removes it. It also clears the corresponding option strings from the
        parser's internal `_option_string_actions` dictionary.
        """
        for action in self._actions:
            if not isinstance(action, argparse._HelpAction):
                continue
            self._remove_action(action)
            for option_string in action.option_strings:
                del self._option_string_actions[option_string]
