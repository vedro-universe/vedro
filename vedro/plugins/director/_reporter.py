import re

from vedro.core import Plugin

__all__ = ("Reporter",)


class Reporter(Plugin):
    @property
    def name(self) -> str:
        cls_name = self.__class__.__name__
        if cls_name.endswith(Reporter.__name__):
            cls_name = cls_name[:-len(Reporter.__name__)]
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls_name).lower()
