from pathlib import Path

from vedro.core import Config, ConfigType

__all__ = ("ConfigValidator",)


class ConfigValidator:
    def __init__(self, config: ConfigType) -> None:
        self._config = config

    def validate(self) -> None:
        default_scenarios_dir = self._config.default_scenarios_dir
        if default_scenarios_dir == Config.default_scenarios_dir:
            return

        if not isinstance(default_scenarios_dir, (Path, str)):
            raise TypeError(
                "Expected `default_scenarios_dir` to be a Path, "
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
            scenarios_dir.relative_to(self._config.project_dir)
        except ValueError:
            raise ValueError(
                f"`default_scenarios_dir` ('{scenarios_dir}') must be inside project directory "
                f"('{self._config.project_dir}')"
            )
