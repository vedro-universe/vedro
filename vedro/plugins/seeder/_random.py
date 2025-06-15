import random
from abc import ABC, abstractmethod
from typing import Tuple, TypeVar

__all__ = ("StandardRandomGenerator", "RandomGenerator",
           "SeedType", "StateType",)

SeedType = TypeVar("SeedType", int, float, str, bytes, bytearray)
StateType = Tuple[int, Tuple[int], None]


class RandomGenerator(ABC):
    """
    Abstract base class for random generators.

    This class defines the interface for setting the seed of a random number generator.
    Any subclass should implement the `set_seed` method, which sets the seed for deterministic
    random number generation.

    The seed can be of various types including int, float, str, bytes, or bytearray.
    """

    @abstractmethod
    def set_seed(self, seed: SeedType) -> None:
        """
        Set the seed for the random number generator.

        :param seed: The seed value to initialize the random number generator. It can be of
                     type int, float, str, bytes, or bytearray.
        """
        pass


class StandardRandomGenerator(RandomGenerator):
    """
    Standard implementation of a random number generator using Python's built-in `random` module.

    This class provides a concrete implementation of the `RandomGenerator` abstract base class,
    and sets the seed using Python's `random.seed()` method.
    """

    def set_seed(self, seed: SeedType) -> None:
        """
        Set the seed for Python's built-in random number generator.

        This method uses `random.seed()` to initialize the random number generator
        with the given seed.

        :param seed: The seed value to initialize the random number generator.
                     It can be of type int, float, str, bytes, or bytearray.
        """
        random.seed(seed)
