from enum import Enum
from typing import List, Set, Tuple, Union

__all__ = ("TagType", "TagsType",)

TagType = Union[str, Enum]
TagsType = Union[List[TagType], Tuple[TagType, ...], Set[TagType]]
