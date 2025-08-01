from __future__ import annotations

import dataclasses


@dataclasses.dataclass(kw_only=True, frozen=True)
class Delta:
    years: int = 0
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
