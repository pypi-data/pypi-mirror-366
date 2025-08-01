from __future__ import annotations

import dataclasses

from when_exactly.moment import Moment


@dataclasses.dataclass(frozen=True)
class Interval:
    start: Moment
    stop: Moment

    def __post_init__(self) -> None:
        if self.start >= self.stop:
            raise ValueError("Interval start must be before stop")

    def __next__(self) -> Interval:
        raise NotImplementedError  # pragma: no cover

    def __lt__(self, other: Interval) -> bool:
        return self.start < other.start or self.stop < other.stop

    def __le__(self, other: Interval) -> bool:
        return self.start <= other.start or self.stop <= other.stop

    def __str__(self) -> str:
        return f"{self.start}/{self.stop}"
