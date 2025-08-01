import time
from types import TracebackType
from typing import Self


class Timer:
    def __init__(self) -> None:
        self._start_time: float | None = None
        self._finish_time: float | None = None

    @property
    def elapsed_seconds(self) -> float:
        if self._start_time is None:
            msg = "Timer not started. Call `with Timer() as timer: ...`"
            raise ValueError(msg)

        if self._finish_time is None:
            msg = "The timer has not finished its work yet"
            raise ValueError(msg)

        return self._finish_time - self._start_time

    @property
    def total_seconds(self) -> str:
        elapsed = self.elapsed_seconds
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed - int(elapsed)) * 10000)
        return f"{minutes}:{seconds:02}:{milliseconds:04}"

    def __enter__(self) -> Self:
        self._start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._finish_time = time.perf_counter()
