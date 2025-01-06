from pathlib import Path

from vedro.core import Config, ConfigType

__all__ = ("ConfigValidator",)


class ConfigValidator:
    """
    Validates the configuration provided to the Vedro framework.

    This class ensures that the configuration values, particularly the default
    scenarios directory, adhere to the expected constraints and types.
    """

    def __init__(self, config: ConfigType) -> None:
        """
        Initialize the ConfigValidator.

        :param config: The configuration object to validate.
        """
        self._config = config

    def validate(self) -> None:
        """
        Perform validation on the configuration object.

        Validates the `default_scenarios_dir` attribute, ensuring it is of the correct type,
        exists, is a directory, and is within the project directory.

        :raises TypeError: If `default_scenarios_dir` is not a `Path` or `str`.
        :raises FileNotFoundError: If `default_scenarios_dir` does not exist.
        :raises NotADirectoryError: If `default_scenarios_dir` is not a directory.
        :raises ValueError: If `default_scenarios_dir` is outside the project directory.
        """
        default_scenarios_dir = self._config.default_scenarios_dir
        if default_scenarios_dir == Config.default_scenarios_dir:
            # Default value is valid, no further checks needed.
            return

        if not isinstance(default_scenarios_dir, (Path, str)):
            raise TypeError(
                "Expected `default_scenarios_dir` to be a Path or str, "
                f"got {type(default_scenarios_dir)} ({default_scenarios_dir!r})"
            )

        scenarios_dir = Path(default_scenarios_dir).resolve()
        if not scenarios_dir.exists():
            raise FileNotFoundError(
                f"`default_scenarios_dir` ('{scenarios_dir}') does not exist"
            )

        if not scenarios_dir.is_dir():
            raise NotADirectoryError(
                f"`default_scenarios_dir` ('{scenarios_dir}') is not a directory"
            )

        try:
            # Ensure the scenarios directory is inside the project directory.
            scenarios_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"`default_scenarios_dir` ('{scenarios_dir}') must be inside the project directory"
                f" ('{self._config.project_dir}')"
            )
