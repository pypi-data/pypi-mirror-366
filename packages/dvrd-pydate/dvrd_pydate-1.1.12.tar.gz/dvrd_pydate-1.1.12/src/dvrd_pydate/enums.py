from enum import Enum


class BaseEnum(Enum):
    @classmethod
    def get_item(cls, value: str):
        return next((item for item in cls if item.value == value), None)


class DatePart(BaseEnum):
    YEAR = 'year'
    YEARS = 'years'
    MONTH = 'month'
    MONTHS = 'months'
    DAY = 'day'
    DAYS = 'days'
    WEEK = 'week'
    WEEKS = 'weeks'


class TimePart(BaseEnum):
    HOUR = 'hour'
    HOURS = 'hours'
    MINUTE = 'minute'
    MINUTES = 'minutes'
    SECOND = 'second'
    SECONDS = 'seconds'
    MICROSECOND = 'microsecond'
    MICROSECONDS = 'microseconds'
