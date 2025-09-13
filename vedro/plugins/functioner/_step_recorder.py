from typing import Iterator, List, Optional, Tuple, Union

__all__ = ("StepRecorder", "get_step_recorder",)


RecordType = Tuple[str, str, float, float, Union[BaseException, None]]


class StepRecorder:
    def __init__(self) -> None:
        self._records: List[RecordType] = []

    def record(self, kind: str, name: str, start_at: float, ended_at: float,
               exc: Optional[BaseException] = None) -> None:
        self._records.append((kind, name, start_at, ended_at, exc))

    def clear(self) -> None:
        self._records.clear()

    def __iter__(self) -> Iterator[RecordType]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)


_step_recorder = None


def get_step_recorder() -> StepRecorder:
    global _step_recorder
    if _step_recorder is None:
        _step_recorder = StepRecorder()
    return _step_recorder
