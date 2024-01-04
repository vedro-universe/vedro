import random
from abc import ABC, abstractmethod
from typing import Tuple, TypeVar

__all__ = ("StandardRandomGenerator", "RandomGenerator",
           "SeedType", "StateType",)

SeedType = TypeVar("SeedType", int, float, str, bytes, bytearray)
StateType = Tuple[int, Tuple[int], None]


class RandomGenerator(ABC):
    @abstractmethod
    def set_seed(self, seed: SeedType) -> None:
        pass


class StandardRandomGenerator(RandomGenerator):
    def set_seed(self, seed: SeedType) -> None:
        random.seed(seed)
