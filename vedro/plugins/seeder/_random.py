import random
from abc import ABC, abstractmethod
from typing import Tuple, TypeVar, cast

__all__ = ("StandardRandomGenerator", "RandomGenerator",
           "SeedType", "StateType",)

SeedType = TypeVar("SeedType", int, float, str, bytes, bytearray)
StateType = Tuple[int, Tuple[int], None]


class RandomGenerator(ABC):
    @abstractmethod
    def set_seed(self, seed: SeedType) -> None:
        pass

    @abstractmethod
    def random_int(self, start: int, end: int) -> int:
        pass

    @abstractmethod
    def get_state(self) -> StateType:
        pass

    @abstractmethod
    def set_state(self, state: StateType) -> None:
        pass


class StandardRandomGenerator(RandomGenerator):
    def set_seed(self, seed: SeedType) -> None:
        random.seed(seed)

    def random_int(self, start: int, end: int) -> int:
        return random.randint(start, end)

    def get_state(self) -> StateType:
        return cast(StateType, random.getstate())

    def set_state(self, state: StateType) -> None:
        random.setstate(state)
