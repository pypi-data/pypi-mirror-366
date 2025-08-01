"""API for when_exactly package."""

from __future__ import annotations

import dataclasses
import datetime
from functools import cached_property
from typing import Iterable

from when_exactly.custom_collection import CustomCollection
from when_exactly.custom_interval import CustomInterval
from when_exactly.delta import Delta
from when_exactly.interval import Interval
from when_exactly.moment import Moment


def _gen_until[I: CustomInterval](start: I, stop: I) -> Iterable[I]:
    while start < stop:
        yield start
        start = next(start)  # type: ignore


def now() -> Moment:
    return Moment.from_datetime(datetime.datetime.now())


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Year(CustomInterval):
    """The `Year` represents an entire year, starting from _January 1_ to _December 31_.

    ## Creating a Year

    ```python
    >>> import when_exactly as we

    >>> year = we.Year(2025)
    >>> year
    Year(2025)

    >>> str(year)
    '2025'

    ```

    ## The Months of a Year

    Get the [`Months`](months.md) of a year.

    ```python
    >>> months = year.months
    >>> len(months)
    12

    >>> months[0]
    Month(2025, 1)

    >>> months[-2:]
    Months([Month(2025, 11), Month(2025, 12)])

    ```

    ## The Weeks of a Year

    Get the [`Weeks`](weeks.md) of a year.

    ```python
    >>> weeks = year.weeks
    >>> len(weeks)
    52

    >>> weeks[0]
    Week(2025, 1)

    ```
    """

    def __init__(self, year: int) -> None:
        """# Create a Year.

        Parameters:
            year: The year to represent.

        Examples:
            ```python
            >>> import when_exactly as we

            >>> year = we.Year(2025)
            >>> year
            Year(2025)

            >>> str(year)
            '2025'

            ```
        """

        Interval.__init__(
            self,
            start=Moment(year, 1, 1, 0, 0, 0),
            stop=Moment(year + 1, 1, 1, 0, 0, 0),
        )

    def __repr__(self) -> str:
        return f"Year({self.start.year})"

    def __str__(self) -> str:
        return f"{self.start.year:04}"

    @classmethod
    def from_moment(cls, moment: Moment) -> Year:
        return Year(moment.year)

    @cached_property
    def months(self) -> Months:
        return Months([Month(self.start.year, self.start.month + i) for i in range(12)])

    @cached_property
    def weeks(self) -> Weeks:
        return Weeks(
            _gen_until(
                Week(self.start.year, 1),
                Week(self.start.year + 1, 1),
            )
        )

    def month(self, month: int) -> Month:
        """Get a specific month of the year.
        Args:
            month (int): The month number (1-12).
        """
        return Month(
            self.start.year,
            month,
        )

    def __next__(self) -> Year:
        return Year.from_moment(self.stop)

    def week(self, week: int) -> Week:
        return Week(
            self.start.year,
            week,
        )

    def ordinal_day(self, ordinal_day: int) -> OrdinalDay:
        return OrdinalDay(
            self.start.year,
            ordinal_day,
        )


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Week(CustomInterval):
    def __init__(self, year: int, week: int) -> None:
        start = Moment.from_datetime(datetime.datetime.fromisocalendar(year, week, 1))
        stop = start + Delta(days=7)
        Interval.__init__(
            self,
            start=start,
            stop=stop,
        )

    def __repr__(self) -> str:
        return f"Week({self.start.week_year}, {self.start.week})"

    def __str__(self) -> str:
        return f"{self.start.week_year:04}-W{self.start.week:02}"

    @classmethod
    def from_moment(cls, moment: Moment) -> Week:
        return Week(
            moment.week_year,
            moment.week,
        )

    def __next__(self) -> CustomInterval:
        return Week.from_moment(self.stop)

    def week_day(self, week_day: int) -> WeekDay:
        return WeekDay(
            self.start.week_year,
            self.start.week,
            week_day,
        )

    @cached_property
    def week_days(self) -> WeekDays:
        return WeekDays([self.week_day(i) for i in range(1, 8)])


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class WeekDay(CustomInterval):
    """A weekday interval."""

    def __init__(self, year: int, week: int, week_day: int):
        start = Moment.from_datetime(
            datetime.datetime.fromisocalendar(
                year=year,
                week=week,
                day=week_day,
            )
        )
        stop = start + Delta(days=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return (
            f"WeekDay({self.start.week_year}, {self.start.week}, {self.start.week_day})"
        )

    def __str__(self) -> str:
        return f"{self.start.week_year}-W{self.start.week:02}-{self.start.week_day}"

    @classmethod
    def from_moment(cls, moment: Moment) -> WeekDay:
        return WeekDay(
            year=moment.week_year,
            week=moment.week,
            week_day=moment.week_day,
        )

    def __next__(self) -> WeekDay:
        return WeekDay.from_moment(moment=self.stop)

    @cached_property
    def week(self) -> Week:
        return Week.from_moment(self.start)

    def to_day(self) -> Day:
        return Day.from_moment(self.start)


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class OrdinalDay(CustomInterval):
    """An ordinal day interval."""

    def __init__(self, year: int, ordinal_day: int) -> None:
        start = Moment.from_datetime(
            datetime.datetime.fromordinal(
                datetime.date(year, 1, 1).toordinal() + ordinal_day - 1
            )
        )
        stop = start + Delta(days=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return f"OrdinalDay({self.start.year}, {self.start.ordinal_day})"

    def __str__(self) -> str:
        return f"{self.start.year:04}-{self.start.ordinal_day:03}"

    @classmethod
    def from_moment(cls, moment: Moment) -> OrdinalDay:
        return OrdinalDay(moment.year, moment.ordinal_day)

    def __next__(self) -> OrdinalDay:
        return OrdinalDay.from_moment(self.stop)


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Second(CustomInterval):
    """A second interval."""

    def __init__(
        self, year: int, month: int, day: int, hour: int, minute: int, second: int
    ) -> None:
        start = Moment(year, month, day, hour, minute, second)
        stop = start + Delta(seconds=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return f"Second({self.start.year}, {self.start.month}, {self.start.day}, {self.start.hour}, {self.start.minute}, {self.start.second})"

    def __str__(self) -> str:
        start = self.start
        return f"{start.year:04}-{start.month:02}-{start.day:02}T{start.hour:02}:{start.minute:02}:{start.second:02}"

    def minute(self) -> Minute:
        return Minute.from_moment(self.start)

    def __next__(self) -> Second:
        return Second.from_moment(self.stop)

    @classmethod
    def from_moment(cls, moment: Moment) -> Second:
        return Second(
            moment.year,
            moment.month,
            moment.day,
            moment.hour,
            moment.minute,
            moment.second,
        )


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Minute(CustomInterval):
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int) -> None:
        start = Moment(year, month, day, hour, minute, 0)
        stop = start + Delta(minutes=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return f"Minute({self.start.year}, {self.start.month}, {self.start.day}, {self.start.hour}, {self.start.minute})"

    def __str__(self) -> str:
        start = self.start
        return f"{start.year:04}-{start.month:02}-{start.day:02}T{start.hour:02}:{start.minute:02}"

    def seconds(self) -> Iterable[Second]:
        second = Second(
            self.start.year,
            self.start.month,
            self.start.day,
            self.start.hour,
            self.start.minute,
            0,
        )
        for _ in range(60):
            yield second
            second = next(second)

    def second(self, second: int) -> Second:
        return Second(
            self.start.year,
            self.start.month,
            self.start.day,
            self.start.hour,
            self.start.minute,
            second,
        )

    def __next__(self) -> Minute:
        return Minute.from_moment(self.stop)

    @classmethod
    def from_moment(cls, moment: Moment) -> Minute:
        return Minute(
            moment.year,
            moment.month,
            moment.day,
            moment.hour,
            moment.minute,
        )


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Hour(CustomInterval):
    def __init__(self, year: int, month: int, day: int, hour: int) -> None:
        start = Moment(year, month, day, hour, 0, 0)
        stop = start + Delta(hours=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return f"Hour({self.start.year}, {self.start.month}, {self.start.day}, {self.start.hour})"

    def __str__(self) -> str:
        start = self.start
        return f"{start.year:04}-{start.month:02}-{start.day:02}T{start.hour:02}"

    @classmethod
    def from_moment(cls, moment: Moment) -> Hour:
        return Hour(
            moment.year,
            moment.month,
            moment.day,
            moment.hour,
        )

    def minutes(self) -> Iterable[Minute]:
        minute = Minute(
            self.start.year,
            self.start.month,
            self.start.day,
            self.start.hour,
            0,
        )
        for _ in range(60):
            yield minute
            minute = next(minute)

    def minute(self, minute: int) -> Minute:
        return Minute(
            self.start.year,
            self.start.month,
            self.start.day,
            self.start.hour,
            minute,
        )

    def day(self) -> Day:
        return Day.from_moment(self.start)

    def __next__(self) -> Hour:
        return Hour.from_moment(self.stop)


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Day(CustomInterval):
    def __init__(self, year: int, month: int, day: int) -> None:
        start = Moment(year, month, day, 0, 0, 0)
        stop = start + Delta(days=1)
        Interval.__init__(self, start=start, stop=stop)

    def __repr__(self) -> str:
        return f"Day({self.start.year}, {self.start.month}, {self.start.day})"

    def __str__(self) -> str:
        return f"{self.start.year:04}-{self.start.month:02}-{self.start.day:02}"

    @classmethod
    def from_moment(cls, moment: Moment) -> Day:
        return Day(
            moment.year,
            moment.month,
            moment.day,
        )

    def hour(self, hour: int) -> Hour:
        return Hour(
            self.start.year,
            self.start.month,
            self.start.day,
            hour,
        )

    @cached_property
    def month(self) -> Month:
        return Month(
            self.start.year,
            self.start.month,
        )

    @cached_property
    def week(self) -> Week:
        return Week.from_moment(self.start)

    def __next__(self) -> Day:
        return Day.from_moment(self.stop)


@dataclasses.dataclass(frozen=True, init=False, repr=False)
class Month(CustomInterval):
    def __init__(self, year: int, month: int) -> None:
        start = Moment(year, month, 1, 0, 0, 0)
        stop = start + Delta(months=1)
        Interval.__init__(
            self,
            start=start,
            stop=stop,
        )

    def __repr__(self) -> str:
        return f"Month({self.start.year}, {self.start.month})"

    def __str__(self) -> str:
        return f"{self.start.year:04}-{self.start.month:02}"

    @classmethod
    def from_moment(cls, moment: Moment) -> Month:
        return Month(
            moment.year,
            moment.month,
        )

    def days(self) -> Days:
        return Days(
            _gen_until(
                Day(self.start.year, self.start.month, 1),
                Day(self.start.year, self.start.month + 1, 1),
            )
        )

    def day(self, day: int) -> Day:
        return Day(
            self.start.year,
            self.start.month,
            day,
        )

    def __next__(self) -> Month:
        return Month.from_moment(self.stop)


class Years(CustomCollection[Year]):
    pass


class Months(CustomCollection[Month]):
    pass


class Weeks(CustomCollection[Week]):
    pass


class Days(CustomCollection[Day]):
    @cached_property
    def months(self) -> Months:
        return Months([day.month for day in self])


class WeekDays(CustomCollection[WeekDay]):
    pass


class Hours(CustomCollection[Hour]):
    pass


class Minutes(CustomCollection[Minute]):
    pass


class Seconds(CustomCollection[Second]):
    pass
