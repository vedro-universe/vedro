from hashlib import blake2b
from inspect import BoundArguments
from pathlib import Path
from typing import Any, List, Optional, Type, TypeVar, Union, cast, overload

from niltype import Nil, Nilable, NilType

from .._scenario import Scenario
from ._plugin import Plugin
from ._scenario_meta import get_scenario_meta, set_scenario_meta
from ._virtual_step import VirtualStep

__all__ = ("VirtualScenario", "ScenarioInitError",)

T = TypeVar("T")


class ScenarioInitError(Exception):
    """
    Raised when there is an error initializing a scenario.
    """
    pass


class VirtualScenario:
    """
    Represents a virtualized scenario with steps and metadata.

    This class wraps around an original Scenario class and its steps, providing
    additional metadata and functionality, such as unique identification, hashing,
    and skipping capabilities.
    """

    def __init__(self, orig_scenario: Type[Scenario], steps: List[VirtualStep], *,
                 project_dir: Path = Path.cwd()) -> None:
        """
        Initialize the VirtualScenario instance with the original scenario and steps.

        :param orig_scenario: The original scenario class.
        :param steps: A list of VirtualStep instances representing the steps in the scenario.
        :param project_dir: The project directory path.
        """
        self._orig_scenario = orig_scenario
        self._steps = steps
        # TODO: Make project_dir required in v2.0
        self._project_dir = project_dir.resolve()
        # TODO: Move path to constructor in v2.0
        self._path = Path(getattr(orig_scenario, "__file__", "."))
        self._is_skipped = False
        self._skip_reason: Union[str, None] = None

    @property
    def steps(self) -> List[VirtualStep]:
        """
        Get the list of steps in the scenario.

        :return: A list of VirtualStep instances.
        """
        return self._steps

    @property
    def unique_id(self) -> str:
        """
        Get a unique identifier for the scenario.

        :return: A string representing the unique ID of the scenario.
        """
        unique_id = f"{self.rel_path}::{self.name}"
        if self.template_index is not None:
            unique_id += f"#{self.template_index}"
        return unique_id

    @property
    def unique_hash(self) -> str:
        """
        Get a unique hash for the scenario.

        :return: A string representing the unique hash of the scenario.
        """
        return blake2b(self.unique_id.encode(), digest_size=20).hexdigest()

    @property
    def template_index(self) -> Union[int, None]:
        """
        Get the template index of the current scenario in the templated scenario.

        :return: An integer representing the template index, or None if not applicable.
        """
        idx = getattr(self._orig_scenario, "__vedro__template_index__", None)
        return cast(Union[int, None], idx)

    @property
    def template_total(self) -> Union[int, None]:
        """
        Get the total number of scenarios in the templated scenario.

        :return: An integer representing the total number of scenarios, or None if not applicable.
        """
        idx = getattr(self._orig_scenario, "__vedro__template_total__", None)
        return cast(Union[int, None], idx)

    @property
    def template_args(self) -> Union[BoundArguments, None]:
        """
        Get the bound arguments for the templated scenario.

        :return: A BoundArguments object representing the template arguments,
                 or None if not applicable.
        """
        args = getattr(self._orig_scenario, "__vedro__template_args__", None)
        return cast(Union[BoundArguments, None], args)

    @property
    def path(self) -> Path:
        """
        Get the path to the scenario file.

        :return: A Path object representing the path to the scenario file.
        """
        return self._path

    @property
    def rel_path(self) -> Path:
        """
        Get the relative path to the scenario file from the project directory.

        :return: A Path object representing the relative path to the scenario file.
        """
        return self._path.relative_to(self._project_dir)

    @property
    def name(self) -> str:
        """
        Get the name of the scenario.

        :return: A string representing the name of the scenario.
        """
        return getattr(self._orig_scenario, "__vedro__template_name__",
                       self._orig_scenario.__name__)

    @property
    def subject(self) -> str:
        """
        Get the subject of the scenario.

        :return: A string representing the subject of the scenario.
        :raises ValueError: If the subject cannot be formatted with the template arguments.
        """
        subject = getattr(self._orig_scenario, "subject", None)
        if not isinstance(subject, str) or subject.strip() == "":
            subject = self._path.stem.replace("_", " ")

        if not self.template_args:
            return subject

        try:
            return subject.format(**self.template_args.arguments)
        except Exception as exc:
            message = f'Can\'t format subject "{subject}" at "{self.rel_path}" ({exc})'
            raise ValueError(message) from None

    @property
    def namespace(self) -> str:
        """
        Get the namespace of the scenario.

        :return: A string representing the namespace of the scenario.
        """
        parts = self.rel_path.parts[1:-1]
        return str(Path(*parts)) if parts else ""

    def skip(self, reason: Optional[str] = None) -> None:
        """
        Mark the scenario as skipped with an optional reason.

        :param reason: The reason for skipping the scenario.
        """
        self._is_skipped = True
        if reason:
            self._skip_reason = reason

    @property
    def skip_reason(self) -> Optional[str]:
        """
        Get the reason for skipping the scenario.

        :return: A string representing the skip reason or None if not skipped.
        """
        return self._skip_reason

    def is_skipped(self) -> bool:
        """
        Check if the scenario is marked as skipped.

        :return: A boolean indicating if the scenario is skipped.
        """
        return self._is_skipped

    def set_meta(self, key: str, value: Any, *, plugin: Plugin,
                 fallback_key: Optional[str] = None) -> None:
        """
        Set metadata for the associated scenario.

        This method sets a metadata key-value pair for the original scenario
        wrapped by this VirtualScenario, scoped to the specified plugin.
        Optionally, a fallback key can be set for backward compatibility.

        :param key: The metadata key to set. Must be a valid Python identifier.
        :param value: The metadata value to set.
        :param plugin: The plugin instance to scope the metadata under.
        :param fallback_key: Optional. A fallback attribute name for backward compatibility.
        """
        set_scenario_meta(self._orig_scenario, key, value,
                          plugin=plugin,
                          fallback_key=fallback_key)

    @overload
    def get_meta(self, key: str, *, plugin: Plugin, default: T,
                 fallback_key: Optional[str] = None) -> T:  # pragma: no cover
        ...  # When default is provided, return T

    @overload
    def get_meta(self, key: str, *, plugin: Plugin, default: NilType = Nil,
                 fallback_key: Optional[str] = None) -> NilType:  # pragma: no cover
        ...  # When default is not provided, return NilType

    def get_meta(self, key: str, *, plugin: Plugin, default: Nilable[T] = Nil,
                 fallback_key: Optional[str] = None) -> Union[T, NilType]:
        """
        Retrieve metadata for the associated scenario.

        This method retrieves the metadata value associated with the specified key,
        scoped to the given plugin, from the original scenario wrapped by this VirtualScenario.
        If the metadata is not found, it returns the provided default value or Nil.
        Optionally, a fallback key can be checked for backward compatibility.

        :param key: The metadata key to retrieve. Must be a valid Python identifier.
        :param plugin: The plugin instance the metadata is scoped under.
        :param default: The default value to return if the metadata is not found. Defaults to Nil.
        :param fallback_key: Optional. A fallback attribute name for backward compatibility.
        :return: The metadata value if found, the fallback attribute value,
                 or the default if not found.
        """
        return get_scenario_meta(self._orig_scenario, key,
                                 default=default,
                                 plugin=plugin,
                                 fallback_key=fallback_key)

    def __call__(self) -> Scenario:
        """
        Initialize and return an instance of the original scenario.

        :return: An instance of the original scenario.
        :raises ScenarioInitError: If the scenario cannot be initialized.
        """
        try:
            return self._orig_scenario()
        except Exception as exc:
            message = f'Can\'t initialize scenario "{self.subject}" at "{self.rel_path}" ({exc!r})'
            raise ScenarioInitError(message) from None

    def __repr__(self) -> str:
        """
        Return a string representation of the VirtualScenario instance.

        :return: A string representing the VirtualScenario instance.
        """
        return f"<{self.__class__.__name__} {str(self.rel_path)!r}>"

    def __eq__(self, other: Any) -> bool:
        """
        Check equality with another object.

        :param other: The other object to compare with.
        :return: A boolean indicating if the other object is equal to this instance.
        """
        return isinstance(other, self.__class__) and (self.__dict__ == other.__dict__)
