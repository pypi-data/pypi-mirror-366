from datetime import datetime, timedelta, date
from typing import Self, Generator

from dvrd_pydate.enums import DatePart, TimePart
from dvrd_pydate.pydate import PyDate, CommonArg

hours_in_day = 24
minutes_in_hour = 60
seconds_in_minute = 60
microseconds_in_second = 1000


class PyDateTime(datetime, PyDate):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if arg is None:
                return PyDateTime.now()
            if isinstance(arg, str):
                return PyDateTime.fromisoformat(arg)
            elif isinstance(arg, datetime):
                return datetime.__new__(cls, arg.year, arg.month, arg.day, arg.hour, arg.minute, arg.second,
                                        arg.microsecond, arg.tzinfo, fold=arg.fold)
            elif isinstance(arg, date):
                return datetime.__new__(cls, arg.year, arg.month, arg.day)
            elif isinstance(arg, (int, float)):
                return PyDateTime.fromtimestamp(arg)
        elif len(args) == 2:
            arg_1 = args[0]
            arg_2 = args[1]
            if isinstance(arg_1, str) and isinstance(arg_2, str):
                return PyDateTime.strptime(arg_1, arg_2)
        if not args and not kwargs:
            now = datetime.now()
            return datetime.__new__(cls, now.year, now.month, now.day, now.hour, now.minute, now.second,
                                    now.microsecond, now.tzinfo, fold=now.fold)
        return datetime.__new__(cls, *args, **kwargs)

    @staticmethod
    def from_value(value: datetime | date | str | int | float = None) -> "PyDateTime":
        return PyDateTime(value)

    @staticmethod
    def iter(*, start: date | str = None, end: date | str | None = None,
             step: DatePart | TimePart | tuple[int | float, DatePart | TimePart] = DatePart.DAY,
             max_steps: int = None) -> \
            Generator["PyDateTime", None, None]:
        if max_steps == 0:
            # Raises StopIteration
            return
        if start is None:
            start = datetime.now()
        current = PyDateTime.from_value(start)
        end_value = None if end is None else PyDateTime.from_value(end)
        if isinstance(step, tuple):
            step_value = step[0]
            step_key = step[1]
        else:
            step_value = 1
            step_key = step
        current_step = 0
        while end_value is None or current < end_value:
            yield current
            current_step += 1
            if max_steps is not None and current_step == max_steps:
                break
            current = current.add(step_value, step_key)

    def set(self, value_or_key: CommonArg, key_or_value: CommonArg) -> Self:
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        if isinstance(key, DatePart):
            return super().set(value, key)
        match key:
            case TimePart.HOURS | TimePart.HOUR:
                return self.set_hour(value)
            case TimePart.MINUTES | TimePart.MINUTE:
                return self.set_minute(value)
            case TimePart.SECONDS | TimePart.SECOND:
                return self.set_second(value)
            case TimePart.MICROSECONDS | TimePart.MICROSECOND:
                return self.set_microsecond(value)

    def add(self, value_or_key: CommonArg, key_or_value: CommonArg) -> Self:
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        match key:
            case key if isinstance(key, DatePart):
                return super().add(value, key)
            case TimePart.HOURS | TimePart.HOUR:
                return self.add_hours(value)
            case TimePart.MINUTES | TimePart.MINUTE:
                return self.add_minutes(value)
            case TimePart.SECONDS | TimePart.SECOND:
                return self.add_seconds(value)
            case TimePart.MICROSECONDS | TimePart.MICROSECOND:
                return self.add_microseconds(value)

    def subtract(self, value_or_key: CommonArg, key_or_value: CommonArg) -> Self:
        key, value = _determine_key_and_value(value_or_key, key_or_value)
        match key:
            case key if isinstance(key, DatePart):
                return super().subtract(value, key)
            case TimePart.HOURS | TimePart.HOUR:
                return self.subtract_hours(value)
            case TimePart.MINUTES | TimePart.MINUTE:
                return self.subtract_minutes(value)
            case TimePart.SECONDS | TimePart.SECOND:
                return self.subtract_seconds(value)
            case TimePart.MICROSECONDS | TimePart.MICROSECOND:
                return self.subtract_microseconds(value)

    def set_hour(self, value: int) -> Self:
        return self.replace(hour=value)

    set_hours = set_hour

    def add_hours(self, value: int | float) -> Self:
        return self + timedelta(hours=value)

    def add_hour(self) -> Self:
        return self.add_hours(1)

    def subtract_hours(self, value: int | float) -> Self:
        return self - timedelta(hours=value)

    def subtract_hour(self) -> Self:
        return self.subtract_hours(1)

    def set_minute(self, value: int) -> Self:
        return self.replace(minute=value)

    set_minutes = set_minute

    def add_minutes(self, value: int | float) -> Self:
        return self + timedelta(minutes=value)

    def add_minute(self) -> Self:
        return self.add_minutes(1)

    def subtract_minutes(self, value: int | float) -> Self:
        return self - timedelta(minutes=value)

    def subtract_minute(self) -> Self:
        return self.subtract_minutes(1)

    def set_second(self, value: int) -> Self:
        return self.replace(second=value)

    set_seconds = set_second

    def add_seconds(self, value: int | float) -> Self:
        return self + timedelta(seconds=value)

    def add_second(self) -> Self:
        return self.add_seconds(1)

    def subtract_seconds(self, value: int | float) -> Self:
        return self - timedelta(seconds=value)

    def subtract_second(self) -> Self:
        return self.subtract_seconds(1)

    def set_microsecond(self, value: int) -> Self:
        return self.replace(microsecond=value)

    set_microseconds = set_microsecond

    def add_microseconds(self, value: int | float) -> Self:
        return self + timedelta(microseconds=value)

    def add_microsecond(self) -> Self:
        return self.add_microseconds(1)

    def subtract_microseconds(self, value: int | float) -> Self:
        return self - timedelta(microseconds=value)

    def subtract_microsecond(self) -> Self:
        return self.subtract_microseconds(1)

    def start_of(self, part: DatePart | TimePart) -> Self:
        if isinstance(part, DatePart):
            if part in [DatePart.DAY, DatePart.DAYS]:
                return self.replace(hour=0, minute=0, second=0, microsecond=0)
            return super().start_of(part)
        elif part in [TimePart.HOUR, TimePart.HOURS]:
            return self.replace(minute=0, second=0, microsecond=0)
        elif part in [TimePart.MINUTE, TimePart.MINUTES]:
            return self.replace(second=0, microsecond=0)
        elif part in [TimePart.SECOND, TimePart.SECONDS]:
            return self.replace(microsecond=0)
        elif part in [TimePart.MICROSECOND, TimePart.MICROSECONDS]:
            return self
        else:
            raise KeyError(f'Unsupported start_of part {part}')

    def end_of(self, part: DatePart | TimePart) -> Self:
        if isinstance(part, DatePart):
            if part in [DatePart.DAY, DatePart.DAYS]:
                return self.replace(hour=23, minute=59, second=59, microsecond=999)
            return super().end_of(part)
        elif part in [TimePart.HOUR, TimePart.HOURS]:
            return self.replace(minute=59, second=59, microsecond=999)
        elif part in [TimePart.MINUTE, TimePart.MINUTES]:
            return self.replace(second=59, microsecond=999)
        elif part in [TimePart.SECOND, TimePart.SECONDS]:
            return self.replace(microsecond=999)
        elif part in [TimePart.MICROSECOND, TimePart.MICROSECONDS]:
            return self
        else:
            raise KeyError(f'Unsupported end_of part {part}')

    def is_before(self, other: datetime | str, granularity: DatePart | TimePart = TimePart.MICROSECOND) -> bool:
        if not isinstance(other, PyDateTime):
            other = PyDateTime.from_value(other)
        return self.start_of(granularity) < other.start_of(granularity)

    def is_same_or_before(self, other: datetime | str, granularity: DatePart | TimePart = TimePart.MICROSECOND) -> bool:
        if not isinstance(other, PyDateTime):
            other = PyDateTime(other)
        return self.start_of(granularity) <= other.start_of(granularity)

    def is_same(self, other: datetime | str, granularity: DatePart | TimePart = TimePart.MICROSECOND) -> bool:
        if not isinstance(other, PyDateTime):
            other = PyDateTime(other)
        return self.start_of(granularity) == other.start_of(granularity)

    def is_same_or_after(self, other: datetime | str, granularity: DatePart | TimePart = TimePart.MICROSECOND) -> bool:
        if not isinstance(other, PyDateTime):
            other = PyDateTime.from_value(other)
        return self.start_of(granularity) >= other.start_of(granularity)

    def is_after(self, other: datetime | str, granularity: DatePart | TimePart = TimePart.MICROSECOND) -> bool:
        if not isinstance(other, PyDateTime):
            other = PyDateTime.from_value(other)
        return self.start_of(granularity) > other.start_of(granularity)

    def is_between(self, other1: date | str, other2: date | str, *,
                   granularity: DatePart | TimePart = TimePart.MICROSECOND,
                   from_inclusive: bool = True, to_inclusive: bool = True) -> bool:
        if not isinstance(other1, PyDateTime):
            other1 = PyDateTime.from_value(other1)
        if not isinstance(other2, PyDateTime):
            other2 = PyDateTime.from_value(other2)
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

    def py_date(self) -> PyDate:
        return PyDate(self.year, self.month, self.day)


def _determine_key_and_value(arg1: CommonArg, arg2: CommonArg) -> tuple[DatePart | TimePart, int]:
    arg1 = _number_or_date_time_part(arg1)
    arg2 = _number_or_date_time_part(arg2)
    key = value = None
    if isinstance(arg1, (int, float)):
        value = arg1
    elif isinstance(arg1, (DatePart, TimePart)):
        key = arg1

    if isinstance(arg2, (int, float)):
        value = arg2
    elif isinstance(arg2, (DatePart, TimePart)):
        key = arg2

    if key is None or value is None:
        raise ValueError('Key and/or value cannot be None')
    return key, value


def _number_or_date_time_part(arg: CommonArg) -> int | float | DatePart | TimePart:
    if isinstance(arg, str):
        return DatePart.get_item(arg) or TimePart.get_item(arg)
    return arg
