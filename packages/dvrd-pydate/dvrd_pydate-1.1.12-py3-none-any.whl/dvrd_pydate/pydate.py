from calendar import monthrange
from datetime import date, timedelta, datetime
from typing import Self, Generator, TypeAlias

from dvrd_pydate.enums import DatePart, TimePart

days_in_week = 7
months_in_year = 12

CommonArg: TypeAlias = int | float | str | DatePart | TimePart


class PyDate(date):
    @staticmethod
    def from_value(value: date | str | int | float = None) -> "PyDate":
        return PyDate(value)

    @staticmethod
    def parse_date(*, value: str, fmt: str) -> "PyDate":
        parsed = datetime.strptime(value, fmt)
        return PyDate(parsed.year, parsed.month, parsed.day)

    @staticmethod
    def iter(*, start: date | str = None, end: date | str | None = None,
             step: DatePart | TimePart | tuple[int | float, DatePart | TimePart] = DatePart.DAY,
             max_steps: int = None) -> \
            Generator["PyDate", None, None]:
        if max_steps == 0:
            # Raises StopIteration
            return
        if isinstance(step, TimePart):
            raise KeyError('Cannot use time parts in PyDate')
        elif isinstance(step, tuple):
            if isinstance((step_key := step[1]), TimePart):
                raise KeyError('Cannot use time parts in PyDate')
            step_value = step[0]
        else:
            step_value = 1
            step_key = step

        if start is None:
            start = date.today()
        current = PyDate.from_value(start)
        end_value = None if end is None else PyDate.from_value(end)
        current_step = 0
        while end_value is None or current < end_value:
            yield current
            current_step += 1
            if max_steps is not None and current_step == max_steps:
                break
            current = current.add(step_value, step_key)

    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if arg is None:
                return PyDate.today()
            if isinstance(arg, str):
                return PyDate.fromisoformat(args[0])
            elif isinstance(arg, date):
                return date.__new__(cls, arg.year, arg.month, arg.day)
            elif isinstance(arg, (int, float)):
                return PyDate.fromtimestamp(arg)
        if not args and not kwargs:
            now = date.today()
            return date.__new__(cls, now.year, now.month, now.day)
        return date.__new__(cls, *args, **kwargs)

    @property
    def max_day(self) -> int:
        return monthrange(self.year, self.month)[1]

    def set(self, value_or_key: CommonArg, key_or_value: CommonArg):
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        match key:
            case DatePart.DAY | DatePart.DAYS:
                return self.set_day(value)
            case DatePart.MONTH | DatePart.MONTHS:
                return self.set_month(value)
            case DatePart.YEAR | DatePart.YEARS:
                return self.set_year(value)

    def add(self, value_or_key: CommonArg, key_or_value: CommonArg) -> Self:
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        match key:
            case DatePart.YEARS | DatePart.YEAR:
                return self.add_years(value)
            case DatePart.MONTH | DatePart.MONTHS:
                return self.add_months(value)
            case DatePart.WEEK | DatePart.WEEKS:
                return self.add_weeks(value)
            case DatePart.DAY | DatePart.DAYS:
                return self.add_days(value)

    def subtract(self, value_or_key: CommonArg, key_or_value: CommonArg) -> Self:
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        match key:
            case DatePart.YEARS | DatePart.YEAR:
                return self.subtract_years(value)
            case DatePart.MONTH | DatePart.MONTHS:
                return self.subtract_months(value)
            case DatePart.WEEK | DatePart.WEEKS:
                return self.subtract_weeks(value)
            case DatePart.DAY | DatePart.DAYS:
                return self.subtract_days(value)

    def set_year(self, value: int) -> Self:
        return self.replace(year=value)

    set_years = set_year

    def add_years(self, value: int) -> Self:
        return self.replace(year=self.year + value)

    def add_year(self) -> Self:
        return self.add_years(1)

    def subtract_years(self, value: int) -> Self:
        return self.replace(year=self.year - value)

    def subtract_year(self) -> Self:
        return self.subtract_years(1)

    def set_month(self, month: int) -> Self:
        """
        Set the month
        :param month: 1-indexed month (1-12)
        :return: new PyDate
        """
        return self.replace(month=month)

    set_months = set_month

    def add_months(self, value: int) -> Self:
        new_date = self.clone()
        add_years, month_value = divmod(new_date.month + value, months_in_year + 1)
        if add_years:
            month_value += 1
        year = new_date.year + add_years
        max_date = monthrange(year, month_value)[1]
        return new_date.replace(year=new_date.year + add_years, month=month_value, day=min(max_date, new_date.day))

    def add_month(self) -> Self:
        return self.add_months(1)

    def subtract_months(self, value: int) -> Self:
        new_date = self.clone()
        subtract_years, remaining_months = divmod(value, months_in_year)
        if subtract_years:
            new_date = new_date.subtract_years(subtract_years)
        if (month_value := new_date.month - remaining_months) < 1:
            new_date = new_date.subtract_year()
            month_value = 12 - abs(month_value)
        max_date = monthrange(new_date.year, month_value)[1]
        return new_date.replace(month=month_value, day=min(new_date.day, max_date))

    def subtract_month(self) -> Self:
        return self.subtract_months(1)

    def add_weeks(self, value: int) -> Self:
        return self + timedelta(weeks=value)

    def add_week(self) -> Self:
        return self.add_weeks(1)

    def subtract_weeks(self, value: int) -> Self:
        return self - timedelta(weeks=value)

    def subtract_week(self) -> Self:
        return self.subtract_weeks(1)

    def set_day(self, value: int) -> Self:
        return self.replace(day=value)

    set_days = set_day

    def add_days(self, value: int) -> Self:
        return self + timedelta(days=value)

    def add_day(self) -> Self:
        return self.add_days(1)

    def subtract_days(self, value: int) -> Self:
        return self - timedelta(days=value)

    def subtract_day(self) -> Self:
        return self.subtract_days(1)

    def clone(self) -> "PyDate":
        return type(self).from_value(self)

    def start_of(self, part: DatePart | TimePart) -> Self:
        if isinstance(part, TimePart):
            raise KeyError('Time part cannot be used in PyDate')
        if part in [DatePart.YEAR, DatePart.YEARS]:
            return self.replace(month=1, day=1)
        elif part in [DatePart.MONTH, DatePart.MONTHS]:
            return self.replace(day=1)
        elif part in [DatePart.WEEK, DatePart.WEEKS]:
            current_weekday = self.weekday()
            return self.replace(day=self.day - current_weekday)
        elif part in [DatePart.DAY, DatePart.DAYS]:
            return self
        else:
            raise KeyError(f'Unsupported start_of part {part}')

    def end_of(self, part: DatePart | TimePart) -> Self:
        if isinstance(part, TimePart):
            raise KeyError('Time part cannot be used in PyDate')
        if part in [DatePart.YEAR, DatePart.YEARS]:
            return self.replace(month=12, day=31)
        elif part in [DatePart.MONTH, DatePart.MONTHS]:
            return self.replace(day=self.max_day)
        elif part in [DatePart.WEEK, DatePart.WEEKS]:
            current_day = self.weekday()
            return self.replace(day=self.day + 6 - current_day)
        elif part in [DatePart.DAY, DatePart.DAYS]:
            return self
        else:
            raise KeyError(f'Unsupported end_of part {part}')

    def is_before(self, other: date | str, granularity: DatePart | TimePart = DatePart.DAY) -> bool:
        if not isinstance(other, PyDate):
            other = PyDate.from_value(other)
        return self.start_of(granularity) < other.start_of(granularity)

    def is_same_or_before(self, other: date | str, granularity: DatePart | TimePart = DatePart.DAY) -> bool:
        if not isinstance(other, PyDate):
            other = PyDate.from_value(other)
        return self.start_of(granularity) <= other.start_of(granularity)

    def is_same(self, other: date | str, granularity: DatePart | TimePart = DatePart.DAY) -> bool:
        if not isinstance(other, PyDate):
            other = PyDate.from_value(other)
        return self.start_of(granularity) == other.start_of(granularity)

    def is_same_or_after(self, other: date | str, granularity: DatePart | TimePart = DatePart.DAY) -> bool:
        if not isinstance(other, PyDate):
            other = PyDate.from_value(other)
        return self.start_of(granularity) >= other.start_of(granularity)

    def is_after(self, other: date | str, granularity: DatePart | TimePart = DatePart.DAY) -> bool:
        if not isinstance(other, PyDate):
            other = PyDate.from_value(other)
        return self.start_of(granularity) > other.start_of(granularity)

    def is_between(self, other1: date | str, other2: date | str, *, granularity: DatePart | TimePart = DatePart.DAY,
                   from_inclusive: bool = True, to_inclusive: bool = True) -> bool:
        if not isinstance(other1, PyDate):
            other1 = PyDate.from_value(other1)
        if not isinstance(other2, PyDate):
            other2 = PyDate.from_value(other2)
        from_date = min(other1, other2)
        to_date = max(other1, other2)
        if from_inclusive:
            if not self.is_same_or_after(from_date, granularity):
                return False
        elif not self.is_after(from_date, granularity):
            return False
        if to_inclusive:
            if not self.is_same_or_before(to_date, granularity):
                return False
        elif not self.is_before(to_date, granularity):
            return False
        return True

    def py_datetime(self):
        from dvrd_pydate.pydatetime import PyDateTime
        return PyDateTime(self.year, self.month, self.day)


def _determine_key_and_value(arg1: CommonArg, arg2: CommonArg) -> tuple[DatePart, int]:
    arg1 = _number_or_date_part(arg1)
    arg2 = _number_or_date_part(arg2)
    key = value = None
    if isinstance(arg1, (int, float)):
        value = arg1
    elif isinstance(arg1, DatePart):
        key = arg1
    elif isinstance(arg1, TimePart):
        raise TypeError('TimePart cannot be used in PyDate')

    if isinstance(arg2, (int, float)):
        value = arg2
    elif isinstance(arg2, DatePart):
        key = arg2
    elif isinstance(arg2, TimePart):
        raise TypeError('TimePart cannot be used in PyDate')

    if key is None or value is None:
        raise ValueError('Key and/or value cannot be None')
    return key, value


def _number_or_date_part(arg: CommonArg) -> int | float | DatePart | TimePart:
    if isinstance(arg, str):
        return DatePart.get_item(arg)
    return arg
