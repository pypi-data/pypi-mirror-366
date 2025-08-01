# dvrd_pydate

This package provides `date` and `datetime` extensions with useful extra utility functions.
The extensions are provided as the `PyDate(date)` and `PyDateTime(datetime, PyDate)` classes. All built-in `date` and
`datetime` functions are still available through inheritance.

## Initialization

### from_value

`PyDate` and `PyDateTime` objects can be constructed using the default `date`/`datetime` constructors or initializing
functions. They can also easily be constructed from existing `date`/`datetime` objects or their `Py*` variants, using
the staticmethod `from_value`.

```python
from datetime import datetime, date
from dvrd_pydate import PyDate, PyDateTime

date_value = date(2024, 1, 1)
datetime_value = datetime(2024, 1, 1, 12, 0, 0, 0)

# All valid initializers
pydate_value = PyDate(2024, 1, 1)
pydate_value = PyDate.fromisoformat('2024-01-01')
pydate_value = PyDate.from_value(date_value)
pydate_value = PyDate(pydate_value)

pydatetime_value = PyDateTime(2024, 1, 1, 12, 0, 0, 0)
pydatetime_value = PyDateTime.fromisoformat('2024-01-01:12:00:00.000')
pydatetime_value = PyDateTime.from_value(datetime_value)
pydatetime_value = PyDateTime.from_value(pydatetime_value)
```

| **Argument** | Type          | Required | Default | **Description**                                                                                                                   |
|--------------|---------------|----------|---------|-----------------------------------------------------------------------------------------------------------------------------------|
| value        | `date \| str` | No       | `None`  | Construct a new PyDate(Time) object from the given value. If value is `None`, `date.today()` or `datetime.now()` is used instead. |

### clone

Both classes provide a `clone` function, which simply clones the object into a new one. This function takes no
arguments.

## Iteration

Both classes provide a staticmethod `iter` which returns a generator. The generator generates PyDate(Time)s with given
interval. It is possible to supply a start date, end date and max amounts of steps to take. If both `end` and
`max_steps` are given, the generator stops at whichever argument is reached first.

```python
from dvrd_pydate import PyDate, DatePart

for date_value in PyDate.iter(end=PyDate.now().add(7, DatePart.DAYS)):
    pass
for date_value in PyDate.iter(max_steps=7):
    # Does the same as the loop above
    pass
```

| **Argument** | Type                                                       | Required | Default        | **Description**                                                                                                                             |
|--------------|------------------------------------------------------------|----------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| start        | `date \| str`                                              | No       | `None`         | Start iterating from date(time). If `None`, uses date.today()` or `datetime.now()`                                                          |
| end          | `date \| str`                                              | No       | `None`         | Optional date(time) to end the iteration at.                                                                                                |
| step         | `DatePart \| TimePart \| tuple[int, DatePart \| TimePart]` | No       | `DatePart.DAY` | Interval to determine each new date(time) with. `PyDate` can only use `DatePart`, while `PyDateTime` can use both `DatePart` as `TimePart`. |
| max_steps    | `int`                                                      | No       | None           | Max amount of date(time)s to generate.                                                                                                      |

## Mutations

Both classes provide functions to alter the date or time. All functions return a new instance, mutations are not done
in-place. All functions can therefore also be chained together.

### Set
Set a specific part of the date/time to given value.

```python
from dvrd_pydate import PyDate, PyDateTime, DatePart, TimePart

date_value = PyDate.today()
date_value = date_value.set(DatePart.DAY, 3)

datetime_value = PyDateTime.now()
datetime_value = datetime_value.set(TimePart.SECONDS, 30)
```

### Add

Add an amount of date/time part. `PyDate` only supports `DatePart` parts, while `PyDateTime` supports both `DatePart` (
through inheritance) and `TimePart`.

```python
from dvrd_pydate import PyDate, PyDateTime, DatePart, TimePart

date_value = PyDate.today()
date_value = date_value.add(7, DatePart.DAYS)
date_value = date_value.add(1, DatePart.WEEK)  # Same as above

datetime_value = PyDateTime.now()
datetime_value = datetime_value.add(1, DatePart.MONTH).add(30, TimePart.SECONDS)
```

| **Argument** | Type                   | Required | Default | **Description**                            |
|--------------|------------------------|----------|---------|--------------------------------------------|
| value        | `int`                  | Yes      | N/A     | The value to add to the current date(time) |
| key          | `DatePart \| TimePart` | Yes      | N/A     | The part to add the value to               |

### Subtract

Subtract an amount of date/time part. `PyDate` only supports `DatePart` parts, while `PyDateTime` supports both
`DatePart` (through inheritance) and `TimePart`.

```python
from dvrd_pydate import PyDate, PyDateTime, DatePart, TimePart

date_value = PyDate.today()
date_value = date_value.subtract(7, DatePart.DAYS)
date_value = date_value.subtract(1, DatePart.WEEK)  # Does the same as above

datetime_value = PyDateTime.now()
datetime_value = datetime_value.subtract(1, DatePart.MONTH).subtract(30, TimePart.SECONDS)
```

#### Add/Subtract parts

Each part also has its own `add` and `subtract` function. E.g. `add_days(2)`, `add_hours(3)`, `subtract_months(4)`, etc.
Adding or subtracting with value `1` can also be achieved by using the utility functions `add_day()`, `add_hour()`,
`subtract_month()`, etc. which calls the `add`/`subtract` functions with value `1`.

## start_of / end_of

Both classes provide the `start_of` and `end_of` functions to conveniently set the date(time) to the start of the given
date/time part.

```python
from dvrd_pydate import PyDate, DatePart

date_value = PyDate(2024, 2, 5)  # 5th of February 2024
start_of_month = date_value.start_of(DatePart.MONTH)  # 1st of February 2024
end_of_month = date_value.end_of(DatePart.MONTH)  # 29th of February 2024
```

| **Argument** | Type                   | Required | Default | Description                                           |
|--------------|------------------------|----------|---------|-------------------------------------------------------|
| part         | `DatePart \| TimePart` | Yes      | N/A     | Determines to which part the date(time) is mutated to |

## Comparison

Both classes provide convenient function to compare itself to another date(time). The following functions can be used:

- `is_before`
- `is_same_or_before`
- `is_same`
- `is_same_or_after`
- `is_after`
- `is_between`

```python
from dvrd_pydate import PyDate, DatePart

date1 = PyDate(2024, 1, 1)
date2 = PyDate(2024, 1, 15)

date1.is_same(date2)  # Granularity defaults to DatePart.DAY, returns False
date1.is_same(date2, DatePart.MONTH)  # True
```

All function return a `bool`. All functions except `is_between` take the following arguments:

| **Argument** | Type                   | Required | Default        | Description                                                                                                                              |
|--------------|------------------------|----------|----------------|------------------------------------------------------------------------------------------------------------------------------------------|
| other        | `date(time) \| str`    | Yes      | N/A            | Date(time) to compare to. Can also be a ISO date(time) string                                                                            |
| granularity  | `DatePart \| TimePart` | No       | `DatePart.DAY` | Determines the exactness of the comparison. For example, this makes it easy to test if two dates are in the same month of the same year. |

The `is_between` function tests if the object is in between given date(time)s. It is possible to exclude the given start
and end date.

```python
from dvrd_pydate import PyDate, DatePart
date1 = PyDate(2024, 1, 1)
date2 = PyDate(2024, 1, 15)
date3 = PyDate(2024, 1, 12)

date3.is_between(date1, date2)  # True
date2.is_between(date1, date2)  # True
date2.is_between(date1, date2, to_inclusive=False)  # False
```