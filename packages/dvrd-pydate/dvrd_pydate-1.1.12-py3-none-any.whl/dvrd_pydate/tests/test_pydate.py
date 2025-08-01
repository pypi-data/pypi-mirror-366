import unittest
from calendar import monthrange
from datetime import date, timedelta

from dvrd_pydate import PyDateTime
from dvrd_pydate.enums import DatePart, TimePart
from dvrd_pydate.pydate import PyDate


class TestPyDate(unittest.TestCase):
    def setUp(self):
        self.test_date = PyDate(2023, 1, 15)

    def test_constructors(self):
        self.assertEqual(date(2023, 1, 15), PyDate.from_value("2023-01-15"))
        self.assertEqual(date(2023, 1, 15), PyDate("2023-01-15"))
        self.assertIsInstance(PyDate(1753260200339 / 1000), PyDate)
        self.assertEqual(date(2023, 1, 15), PyDate(2023, 1, 15))
        self.assertEqual(date(2023, 1, 15), PyDate(date(2023, 1, 15)))
        self.assertEqual(date(2023, 1, 15), PyDate.parse_date(value='15-01-2023', fmt='%d-%m-%Y'))
        self.assertEqual(date.today(), PyDate.from_value())
        self.assertEqual(date.today(), PyDate())
        self.assertEqual(date.today(), PyDate(None))

    def test_add_operations(self):
        test_date = PyDate(2023, 1, 15)

        # Test adding years
        date_copy = PyDate.from_value(test_date).add(1, DatePart.YEAR)
        self.assertEqual(date(2024, 1, 15), date_copy)

        # Test adding months
        date_copy = PyDate.from_value(test_date).add(2, DatePart.MONTHS)
        self.assertEqual(date_copy, date(2023, 3, 15))

        # Test adding weeks
        date_copy = PyDate.from_value(test_date).add(1, DatePart.WEEKS)
        self.assertEqual(date_copy, date(2023, 1, 22))

        # Test adding days
        date_copy = PyDate.from_value(test_date).add(5, DatePart.DAYS)
        self.assertEqual(date_copy, date(2023, 1, 20))

        self.assertRaises(TypeError, date_copy.add, 5, TimePart.HOURS)

    def test_add_overflow_operations(self):
        test_date = PyDate.from_value('2023-12-31')

        # Test adding years
        date_copy = test_date.clone().add(1, DatePart.YEAR)
        self.assertEqual(date_copy, date(2024, 12, 31))

        date_copy = test_date.clone().add_year()
        self.assertEqual(date_copy, date(2024, 12, 31))

        # Test adding months
        date_copy = test_date.clone().add(1, DatePart.MONTH)
        self.assertEqual(date_copy, date(2024, 1, 31))

        date_copy = test_date.clone().add_month()
        self.assertEqual(date_copy, date(2024, 1, 31))

        # Test adding month to less max days
        date_copy = PyDate.from_value('2023-03-31').add(1, DatePart.MONTH)
        self.assertEqual(date_copy, date(2023, 4, 30))

        date_copy = PyDate.from_value('2023-03-31').add_month()
        self.assertEqual(date_copy, date(2023, 4, 30))

        # Test adding weeks
        date_copy = test_date.clone().add(1, DatePart.WEEK)
        self.assertEqual(date_copy, date(2024, 1, 7))

        date_copy = test_date.clone().add_week()
        self.assertEqual(date_copy, date(2024, 1, 7))

        # Test adding days
        date_copy = test_date.clone().add(1, DatePart.DAY)
        self.assertEqual(date_copy, date(2024, 1, 1))

        date_copy = test_date.clone().add_day()
        self.assertEqual(date_copy, date(2024, 1, 1))

    def test_subtract_operations(self):
        # Test subtracting years
        test_date = PyDate(2023, 1, 15)

        date_copy = PyDate.from_value(test_date).subtract(1, DatePart.YEAR)
        self.assertEqual(date_copy, date(2022, 1, 15))

        date_copy = PyDate.from_value(test_date).subtract_year()
        self.assertEqual(date_copy, date(2022, 1, 15))

        # Test subtracting months
        date_copy = PyDate.from_value(test_date).subtract(2, DatePart.MONTHS)
        self.assertEqual(date(2022, 11, 15), date_copy)

        date_copy = PyDate.from_value(test_date).subtract_month()
        self.assertEqual(date_copy, date(2022, 12, 15))

        # Test subtracting 37 in months
        date_copy = PyDate.from_value(test_date).subtract(37, DatePart.MONTHS)
        self.assertEqual(date_copy, date(2019, 12, 15))

        # Test subtracting weeks
        date_copy = PyDate.from_value(test_date).subtract(1, DatePart.WEEK)
        self.assertEqual(date_copy, date(2023, 1, 8))

        date_copy = PyDate.from_value(test_date).subtract_week()
        self.assertEqual(date_copy, date(2023, 1, 8))

        # Test subtracting days
        date_copy = PyDate.from_value(test_date).subtract(1, DatePart.DAY)
        self.assertEqual(date(2023, 1, 14), date_copy)

        date_copy = PyDate.from_value(test_date).subtract_day()
        self.assertEqual(date(2023, 1, 14), date_copy)

        self.assertRaises(TypeError, date_copy.subtract, 5, TimePart.HOURS)

    def test_subtract_overflow_operations(self):
        test_date = PyDate.from_value('2023-01-31')

        # Test subtracting years
        date_copy = test_date.clone().subtract(1, DatePart.YEAR)
        self.assertEqual(date(2022, 1, 31), date_copy)

        # Test subtracting months
        date_copy = test_date.clone().subtract(1, DatePart.MONTH)
        self.assertEqual(date(2022, 12, 31), date_copy)

        # Test subtracting months to less max days
        date_copy = PyDate.from_value('2023-07-31').subtract(1, DatePart.MONTH)
        self.assertEqual(date(2023, 6, 30), date_copy)

    def test_clone(self):
        cloned = self.test_date.clone()
        self.assertEqual(cloned, self.test_date)
        self.assertIsNot(cloned, self.test_date)

    def test_iter(self):
        # Default iter, with end date
        end = PyDate.today().add(1, DatePart.MONTHS)
        expect_date = date.today()
        for value in PyDate.iter(end=end):
            self.assertEqual(expect_date, value)
            expect_date += timedelta(days=1)

        # Specifying start
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        expect_date = date(2024, 1, 1)
        for value in PyDate.iter(start=start, end=end):
            self.assertEqual(expect_date, value)
            expect_date += timedelta(days=1)

        # 2-days interval
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        expect_date = date(2024, 1, 1)
        for value in PyDate.iter(start=start, end=end, step=(2, DatePart.DAYS)):
            self.assertEqual(expect_date, value)
            expect_date += timedelta(days=2)

        # 1-month interval
        start = date(2024, 1, 1)
        end = date(2025, 7, 31)
        expect_date = date(2024, 1, 1)
        last_value = None
        for value in PyDate.iter(start=start, end=end, step=DatePart.MONTH):
            self.assertEqual(expect_date, value)
            next_month = expect_date.month + 1
            add_year, month_value = divmod(next_month, 13)
            if add_year:
                month_value += 1
            expect_date = expect_date.replace(year=expect_date.year + add_year, month=month_value)
            last_value = value
        self.assertLess(last_value, end)

        # Max steps argument
        result = PyDate.iter(max_steps=5)
        self.assertEqual(len(list(result)), 5)
        self.assertRaises(StopIteration, lambda: next(PyDate.iter(max_steps=0)))

        # Max steps + end
        result = PyDate.iter(end=PyDate.today().add(4, DatePart.DAYS), max_steps=5)
        self.assertEqual(len(list(result)), 4)

        result = PyDate.iter(end=PyDate.today().add(6, DatePart.DAYS), max_steps=5)
        self.assertEqual(len(list(result)), 5)

        # Invalid interval
        self.assertRaises(KeyError,
                          lambda: next(PyDate.iter(start=PyDate.today(), end=PyDate.today(), step=TimePart.HOURS)))
        self.assertRaises(KeyError,
                          lambda: next(PyDate.iter(start=PyDate.today(), end=PyDate.today(), step=(1, TimePart.HOURS))))

    def test_start_of(self):
        test_date = PyDate.today()
        start_of = test_date.start_of(DatePart.YEAR)
        self.assertTupleEqual((start_of.month, start_of.day), (1, 1))

        start_of = test_date.start_of(DatePart.MONTH)
        self.assertTupleEqual((start_of.month, start_of.day), (date.today().month, 1))

        test_date = PyDate.fromisoformat('2024-11-24')  # Sunday
        self.assertEqual(date(2024, 11, 18), test_date.start_of(DatePart.WEEK))

        self.assertIs(test_date, test_date.start_of(DatePart.DAY))
        self.assertRaises(KeyError, test_date.start_of, TimePart.HOURS)
        self.assertRaises(KeyError, test_date.start_of, 'not_a_key')

    def test_end_of(self):
        test_date = PyDate.today()

        # Year
        end_of = test_date.end_of(DatePart.YEAR)
        self.assertTupleEqual((end_of.month, end_of.day), (12, 31))

        # Month
        end_of = test_date.end_of(DatePart.MONTH)
        today = date.today()
        max_date = monthrange(today.year, today.month)[1]
        self.assertTupleEqual((end_of.month, end_of.day), (today.month, max_date))

        # Week
        test_date = PyDate.fromisoformat('2024-11-20')  # Wednesday
        end_of = test_date.end_of(DatePart.WEEK)
        self.assertEqual(date(2024, 11, 24), end_of)

        self.assertIs(test_date, test_date.end_of(DatePart.DAY))
        self.assertRaises(KeyError, test_date.end_of, TimePart.HOURS)
        self.assertRaises(KeyError, test_date.end_of, 'not_a_key')

    def test_is_before(self):
        # Full date check
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 11, 25)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)

        self.assertTrue(date1.is_before(date2))
        self.assertTrue(date1.is_before(date2_value))
        self.assertFalse(date2.is_before(date1))
        self.assertFalse(date2.is_before(date1_value))

        # Month check
        date3 = PyDate(2024, 10, 24)
        self.assertFalse(date1.is_before(date2, DatePart.MONTH))
        self.assertFalse(date2.is_before(date1, DatePart.MONTH))

        self.assertTrue(date3.is_before(date1, DatePart.MONTH))
        self.assertTrue(date3.is_before(date2, DatePart.MONTH))

        # Year check
        date4 = PyDate(2023, 11, 24)
        self.assertFalse(date1.is_before(date2, DatePart.YEAR))
        self.assertFalse(date2.is_before(date1, DatePart.YEAR))
        self.assertFalse(date1.is_before(date3, DatePart.YEAR))
        self.assertFalse(date2.is_before(date1, DatePart.YEAR))
        self.assertFalse(date1.is_before(date4, DatePart.YEAR))

        self.assertTrue(date4.is_before(date1, DatePart.YEAR))
        self.assertTrue(date4.is_before(date2, DatePart.YEAR))
        self.assertTrue(date4.is_before(date3, DatePart.YEAR))

    def test_is_same_or_before(self):
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 11, 25)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)
        date3 = date2.clone()

        # Full date check
        self.assertTrue(date1.is_same_or_before(date2))
        self.assertTrue(date1.is_same_or_before(date2_value))
        self.assertTrue(date2.is_same_or_before(date3))
        self.assertTrue(date3.is_same_or_before(date2))

        self.assertFalse(date2.is_same_or_before(date1))
        self.assertFalse(date2.is_same_or_before(date1_value))
        self.assertFalse(date2.is_same_or_before(date1))
        self.assertFalse(date3.is_same_or_before(date1))

        # Month check
        date4 = PyDate(2023, 10, 24)
        self.assertTrue(date1.is_same_or_before(date2, DatePart.MONTH))
        self.assertTrue(date2.is_same_or_before(date1, DatePart.MONTH))
        self.assertTrue(date1.is_same_or_before(date3, DatePart.MONTH))
        self.assertTrue(date3.is_same_or_before(date1, DatePart.MONTH))

        self.assertFalse(date1.is_same_or_before(date4, DatePart.MONTH))

        # Day check
        self.assertTrue(date1.is_same_or_before(date2, DatePart.DAY))
        self.assertTrue(date2.is_same_or_before(date3, DatePart.DAY))
        self.assertTrue(date3.is_same_or_before(date2, DatePart.DAY))
        self.assertTrue(date4.is_same_or_before(date1, DatePart.DAY))
        self.assertTrue(date4.is_same_or_before(date2, DatePart.DAY))
        self.assertTrue(date4.is_same_or_before(date3, DatePart.DAY))

        self.assertFalse(date2.is_same_or_before(date1, DatePart.DAY))
        self.assertFalse(date3.is_same_or_before(date1, DatePart.DAY))

    def test_is_same(self):
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 11, 25)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)

        # Full check
        self.assertFalse(date1.is_same(date2))
        self.assertFalse(date1.is_same(date2_value))
        self.assertFalse(date2.is_same(date1))

        # Year
        self.assertTrue(date1.is_same(date2, DatePart.YEAR))
        self.assertTrue(date2.is_same(date1, DatePart.YEAR))

        # Month
        self.assertTrue(date1.is_same(date2, DatePart.MONTH))
        self.assertTrue(date2.is_same(date1, DatePart.MONTH))

        # Day
        self.assertFalse(date1.is_same(date2, DatePart.DAY))
        self.assertFalse(date2.is_same(date1, DatePart.DAY))

    def test_is_same_or_after(self):
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 11, 25)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)

        # Full check
        self.assertTrue(date1.is_same_or_after(date1.clone()))
        self.assertTrue(date1.is_same_or_after(date1_value))
        self.assertTrue(date2.is_same_or_after(date1))

        self.assertFalse(date1.is_same_or_after(date2))

        # Year check
        date3 = PyDate(2023, 11, 25)
        self.assertTrue(date1.is_same_or_after(date2, DatePart.YEAR))
        self.assertTrue(date2.is_same_or_after(date1, DatePart.YEAR))

        self.assertFalse(date3.is_same_or_after(date1, DatePart.YEAR))

        # Month check
        self.assertTrue(date1.is_same_or_after(date2, DatePart.MONTH))
        self.assertTrue(date2.is_same_or_after(date1, DatePart.MONTH))

        self.assertFalse(date3.is_same_or_after(date1, DatePart.MONTH))

        # Day check
        self.assertTrue(date1.is_same_or_after(date1.clone(), DatePart.DAY))
        self.assertTrue(date2.is_same_or_after(date1, DatePart.DAY))

        self.assertFalse(date1.is_same_or_after(date2, DatePart.DAY))

    def test_is_after(self):
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 11, 25)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)

        # Full check
        self.assertTrue(date2.is_after(date1))
        self.assertTrue(date2.is_after(date1_value))

        self.assertFalse(date1.is_after(date2))
        self.assertFalse(date1.is_after(date1.clone()))

        # Year
        date3 = PyDate(2023, 11, 24)
        self.assertTrue(date1.is_after(date3, DatePart.YEAR))

        self.assertFalse(date1.is_after(date2, DatePart.YEAR))
        self.assertFalse(date2.is_after(date1, DatePart.YEAR))

        # Month
        self.assertTrue(date1.is_after(date3, DatePart.MONTH))

        self.assertFalse(date1.is_after(date2, DatePart.MONTH))
        self.assertFalse(date2.is_after(date1, DatePart.MONTH))

        # Day
        self.assertTrue(date2.is_after(date1, DatePart.DAY))

        self.assertFalse(date1.is_after(date2, DatePart.DAY))
        self.assertFalse(date1.is_after(date1.clone(), DatePart.DAY))

    def test_is_between(self):
        date1_value = date(2024, 11, 24)
        date2_value = date(2024, 12, 24)
        date3_value = date(2024, 10, 24)
        date1 = PyDate.from_value(date1_value)
        date2 = PyDate.from_value(date2_value)
        date3 = PyDate.from_value(date3_value)

        # Intentionally give arguments in reverse order to make sure the determination of the `from_date`
        # and `to_date` works correctly
        self.assertTrue(date1.is_between(date2, date3))
        self.assertTrue(date1.is_between(date2_value, date3_value))
        self.assertFalse(date2.is_between(date1, date3))
        self.assertFalse(date3.is_between(date1, date2))

        # Test to date not inclusive
        date4 = date1.clone()
        self.assertTrue(date1.is_between(date3, date4, to_inclusive=True))
        self.assertFalse(date1.is_between(date3, date4, to_inclusive=False))

        # Test from date not inclusive
        self.assertTrue(date1.is_between(date4, date2, from_inclusive=True))
        self.assertFalse(date1.is_between(date4, date2, from_inclusive=False))

        # Granularity
        date2 = PyDate(2024, 11, 12)
        date3 = PyDate(2024, 11, 25)
        self.assertTrue(date1.is_between(date2, date3))
        self.assertTrue(date1.is_between(date3, date2, granularity=DatePart.MONTH))
        self.assertFalse(date1.is_between(date2, date3, granularity=DatePart.MONTH, from_inclusive=False))
        self.assertFalse(date1.is_between(date2, date3, granularity=DatePart.MONTH, to_inclusive=False))

        self.assertTrue(date1.is_between(date3, date2, granularity=DatePart.YEAR))
        self.assertFalse(date1.is_between(date2, date3, granularity=DatePart.YEAR, from_inclusive=False))
        self.assertFalse(date1.is_between(date2, date3, granularity=DatePart.YEAR, to_inclusive=False))

    def test_set_operations(self):
        pydate = PyDate(2024, 1, 1)
        self.assertEqual(date(2024, 2, 1), pydate.set(DatePart.MONTH, 2))
        self.assertEqual(date(2024, 2, 1), pydate.set(2, DatePart.MONTH))
        self.assertEqual(date(2024, 2, 1), pydate.set(2, 'month'))
        self.assertEqual(date(2024, 2, 1), pydate.set('months', 2))
        self.assertEqual(date(2024, 2, 1), pydate.set(2, 'months'))
        self.assertEqual(date(2024, 2, 1), pydate.set_month(2))
        self.assertEqual(date(2024, 2, 1), pydate.set_months(2))

        self.assertEqual(date(2024, 1, 2), pydate.set(DatePart.DAY, 2))
        self.assertEqual(date(2024, 1, 2), pydate.set(2, DatePart.DAYS))
        self.assertEqual(date(2024, 1, 2), pydate.set_day(2))
        self.assertEqual(date(2024, 1, 2), pydate.set_days(2))

        self.assertEqual(date(2025, 1, 1), pydate.set(DatePart.YEAR, 2025))
        self.assertEqual(date(2025, 1, 1), pydate.set(2025, DatePart.YEARS))
        self.assertEqual(date(2025, 1, 1), pydate.set_year(2025))
        self.assertEqual(date(2025, 1, 1), pydate.set_years(2025))

        self.assertRaises(TypeError, pydate.set, TimePart.HOURS, 2025)
        self.assertRaises(ValueError, pydate.set, None, 2025)
        self.assertRaises(ValueError, pydate.set, DatePart.DAY, None)

    def test_py_datetime(self):
        self.assertEqual(PyDateTime(2024, 1, 1, 0, 0, 0), PyDate(2024, 1, 1).py_datetime())


if __name__ == '__main__':
    unittest.main()
