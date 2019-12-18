"""Unittests for the functions in the time module."""

import datetime
import unittest

from mrfreeze import time


class TimeUnitTest(unittest.TestCase):
    """Test the time module."""

    def test_extract_time_returns_none_none_with_invalid_time_expression(self):
        """
        Test the return value for an invalid time expression.

        Should return None and None.
        """
        test_args = ("hello", "minutes")
        test_expression = time.extract_time(test_args)

        self.assertEqual(test_expression, (None, None))

    def test_extract_time_return_value_for_1_second_singular(self):
        """
        Test the return value for ("1", "second").

        Should return a one second timedelta and a datetime object.
        """
        test_args = ("1", "second")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(seconds=1)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_seconds_plural(self):
        """
        Test the return value for ("2", "seconds").

        Should return a two second timedelta and a datetime object.
        """
        test_args = ("2", "seconds")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(seconds=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_minute_singular(self):
        """
        Test the return value for ("1", "minute").

        Should return a one minute timedelta and a datetime object.
        """
        test_args = ("1", "minute")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(minutes=1)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_minutes_plural(self):
        """
        Test the return value for ("2", "minutes").

        Should return a two minute timedelta and a datetime object.
        """
        test_args = ("2", "minutes")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(minutes=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_hour_singular(self):
        """
        Test the return value for ("1", "hour").

        Should return a one hour timedelta and a datetime object.
        """
        test_args = ("1", "hour")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(hours=1)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_hours_plural(self):
        """
        Test the return value for ("2", "hours").

        Should return a two hour timedelta and a datetime object.
        """
        test_args = ("2", "hours")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(hours=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_day_singular(self):
        """
        Test the return value for ("1", "day").

        Should return a one day timedelta and a datetime object.
        """
        test_args = ("1", "day")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=1)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_days_plural(self):
        """
        Test the return value for ("2", "days").

        Should return a two day timedelta and a datetime object.
        """
        test_args = ("2", "days")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_week_singular(self):
        """
        Test the return value for ("1", "week").

        Should return a one week timedelta and a datetime object.
        """
        test_args = ("1", "week")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(weeks=1)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_weeks_plural(self):
        """
        Test the return value for ("2", "weeks").

        Should return a two week timedelta and a datetime object.
        """
        test_args = ("2", "weeks")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(weeks=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_month_singular(self):
        """
        Test the return value for ("1", "month").

        Should return a 30 day timedelta and a datetime object.
        """
        test_args = ("1", "month")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=30)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_months_plural(self):
        """
        Test the return value for ("2", "months").

        Should return a 60 day timedelta and a datetime object.
        """
        test_args = ("2", "months")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=60)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_1_year_singular(self):
        """
        Test the return value for ("1", "year").

        Should return a 365 day timedelta and a datetime object.
        """
        test_args = ("1", "year")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=365)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_2_years_plural(self):
        """
        Test the return value for ("2", "years").

        Should return a 730 day timedelta and a datetime object.
        """
        test_args = ("2", "years")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=730)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_multiple_units(self):
        """
        Test the return value for a compound time statement.

        Input is ("3", "days", "2", "seconds", "1", "year").
        Should return a 368 day + 2 second timedelta and a datetime object.
        """
        test_args = ("3", "days", "2", "seconds", "1", "year")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=368, seconds=2)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    def test_extract_time_return_value_for_absurdly_high_numbers(self):
        """
        Test the return value for numbers so high the datetime overflows.

        Should return a timedelta and datetime.datetime.max.
        """
        test_args = ("9999999999999999", "years")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.datetime.max

        self.assertTrue(isinstance(first, datetime.timedelta))
        self.assertEqual(second, should_be)

    def test_extract_time_return_value_for_negative_numbers(self):
        """
        Test the return value for negative numbers.

        Should return a -730 day timedelta and a datetime object.
        """
        test_args = ("-2", "years")
        (first, second) = time.extract_time(test_args)
        should_be = datetime.timedelta(days=-730)

        self.assertEqual(first, should_be)
        self.assertTrue(isinstance(second, datetime.datetime))

    # Possible future update, not implemented yet.
    #
    # def test_extract_time_return_value_for_absurdly_low_numbers(self):
    #     """
    #     Test the return value for negative numbers.

    #     Should return a timedelta and datetime.datetime.min.
    #     """
    #     test_args = ("-999999999999999999", "years")
    #     (first, second) = time.extract_time(test_args)
    #     should_be = datetime.datetime.min

    #     self.assertTrue(isinstance(first, datetime.timedelta))
    #     self.assertEqual(second, should_be)
