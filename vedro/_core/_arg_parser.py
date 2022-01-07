import argparse
import sys
from typing import Any, Optional

__all__ = ("ArgumentParser",)


class ArgumentParser(argparse.ArgumentParser):
    _subparser_action: Optional[argparse.Action] = None
    _subparser_default: Optional[str] = None

    def add_subparsers(self, **kwargs: Any) -> Any:
        action = super().add_subparsers(**kwargs)
        self._subparser_action = action
        return action

    def get_subparsers(self) -> Any:
        return self._subparser_action

    def set_default_subparser(self, name: str) -> None:
        self._subparser_default = name

    def parse_known_args(self, args: Any = None, namespace: Any = None) -> Any:
        if args is None:
            args = sys.argv[1:]
        else:
            args = list(args)

        if self._subparser_default and self._subparser_action and self._subparser_action.choices:
            arguments = set(args)
            commands = set(self._subparser_action.choices)
            help_args = {"-h", "--help"}
            if not help_args.intersection(arguments) and not commands.intersection(arguments):
                args.insert(0, self._subparser_default)

        return super().parse_known_args(args, namespace)
