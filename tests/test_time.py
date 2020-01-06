"""Unittests for the functions in the time module."""

import datetime

from mrfreeze import time


def test_extract_time_return_value_for_no_fallback_minutes():
    """
    Test the return for numerical expressions without fallback minutes.

    Should return None and None.
    """
    test_args = ("10", "hello")
    test_expression = time.extract_time(test_args, fallback_minutes=False)

    assert test_expression, (None, None)


def test_extract_time_return_value_for_fallback_minutes():
    """
    Test the return for numerical expressions without fallback minutes.

    Should return None and None.
    """
    test_args = ("10", "hello")
    (first, second) = time.extract_time(test_args, fallback_minutes=True)
    should_be = datetime.timedelta(minutes=10)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_returns_none_none_with_invalid_time_expression():
    """
    Test the return value for an invalid time expression.

    Should return None and None.
    """
    test_args = ("hello", "minutes")
    test_expression = time.extract_time(test_args)

    assert test_expression, (None, None)


def test_extract_time_return_value_for_1_second_singular():
    """
    Test the return value for ("1", "second").

    Should return a one second timedelta and a datetime object.
    """
    test_args = ("1", "second")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(seconds=1)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_seconds_plural():
    """
    Test the return value for ("2", "seconds").

    Should return a two second timedelta and a datetime object.
    """
    test_args = ("2", "seconds")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(seconds=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_minute_singular():
    """
    Test the return value for ("1", "minute").

    Should return a one minute timedelta and a datetime object.
    """
    test_args = ("1", "minute")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(minutes=1)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_minutes_plural():
    """
    Test the return value for ("2", "minutes").

    Should return a two minute timedelta and a datetime object.
    """
    test_args = ("2", "minutes")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(minutes=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_hour_singular():
    """
    Test the return value for ("1", "hour").

    Should return a one hour timedelta and a datetime object.
    """
    test_args = ("1", "hour")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(hours=1)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_hours_plural():
    """
    Test the return value for ("2", "hours").

    Should return a two hour timedelta and a datetime object.
    """
    test_args = ("2", "hours")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(hours=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_day_singular():
    """
    Test the return value for ("1", "day").

    Should return a one day timedelta and a datetime object.
    """
    test_args = ("1", "day")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=1)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_days_plural():
    """
    Test the return value for ("2", "days").

    Should return a two day timedelta and a datetime object.
    """
    test_args = ("2", "days")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_week_singular():
    """
    Test the return value for ("1", "week").

    Should return a one week timedelta and a datetime object.
    """
    test_args = ("1", "week")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(weeks=1)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_weeks_plural():
    """
    Test the return value for ("2", "weeks").

    Should return a two week timedelta and a datetime object.
    """
    test_args = ("2", "weeks")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(weeks=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_month_singular():
    """
    Test the return value for ("1", "month").

    Should return a 30 day timedelta and a datetime object.
    """
    test_args = ("1", "month")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=30)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_months_plural():
    """
    Test the return value for ("2", "months").

    Should return a 60 day timedelta and a datetime object.
    """
    test_args = ("2", "months")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=60)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_1_year_singular():
    """
    Test the return value for ("1", "year").

    Should return a 365 day timedelta and a datetime object.
    """
    test_args = ("1", "year")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=365)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_2_years_plural():
    """
    Test the return value for ("2", "years").

    Should return a 730 day timedelta and a datetime object.
    """
    test_args = ("2", "years")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=730)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_multiple_units():
    """
    Test the return value for a compound time statement.

    Input is ("3", "days", "2", "seconds", "1", "year").
    Should return a 368 day + 2 second timedelta and a datetime object.
    """
    test_args = ("3", "days", "2", "seconds", "1", "year")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=368, seconds=2)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_extract_time_return_value_for_absurdly_high_numbers():
    """
    Test the return value for numbers so high the datetime overflows.

    Should return a timedelta and datetime.datetime.max.
    """
    test_args = ("9999999999999999", "years")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.datetime.max

    assert isinstance(first, datetime.timedelta)
    assert second, should_be


def test_extract_time_return_value_for_negative_numbers():
    """
    Test the return value for negative numbers.

    Should return a -730 day timedelta and a datetime object.
    """
    test_args = ("-2", "years")
    (first, second) = time.extract_time(test_args)
    should_be = datetime.timedelta(days=-730)

    assert first, should_be
    assert isinstance(second, datetime.datetime)


def test_parse_timedelta_one_second_singular():
    """
    Test the return value for timedelta(seconds=1).

    Should return "1 second".
    """
    timedelta = datetime.timedelta(seconds=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 second"

    assert test_value, expected


def test_parse_timedelta_two_seconds_plural():
    """
    Test the return value for timedelta(seconds=2).

    Should return "2 seconds".
    """
    timedelta = datetime.timedelta(seconds=2)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 seconds"

    assert test_value, expected


def test_parse_timedelta_one_minute_singular():
    """
    Test the return value for timedelta(minutes=1).

    Should return "1 minute".
    """
    timedelta = datetime.timedelta(minutes=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 minute"

    assert test_value, expected


def test_parse_timedelta_two_minutes_plural():
    """
    Test the return value for timedelta(minutes=2).

    Should return "2 minutes".
    """
    timedelta = datetime.timedelta(minutes=2)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 minutes"

    assert test_value, expected


def test_parse_timedelta_one_hour_singular():
    """
    Test the return value for timedelta(hours=1).

    Should return "1 hour".
    """
    timedelta = datetime.timedelta(hours=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 hour"

    assert test_value, expected


def test_parse_timedelta_two_hours_plural():
    """
    Test the return value for timedelta(hours=2).

    Should return "2 hours".
    """
    timedelta = datetime.timedelta(hours=2)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 hours"

    assert test_value, expected


def test_parse_timedelta_one_day_singular():
    """
    Test the return value for timedelta(day=1).

    Should return "1 day".
    """
    timedelta = datetime.timedelta(days=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 day"

    assert test_value, expected


def test_parse_timedelta_two_days_plural():
    """
    Test the return value for timedelta(days=2).

    Should return "2 days".
    """
    timedelta = datetime.timedelta(days=2)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 days"

    assert test_value, expected


def test_parse_timedelta_one_week_singular():
    """
    Test the return value for timedelta(weeks=1).

    Should return "1 week".
    """
    timedelta = datetime.timedelta(weeks=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 week"

    assert test_value, expected


def test_parse_timedelta_two_weeks_plural():
    """
    Test the return value for timedelta(weeks=2).

    Should return "2 weeks".
    """
    timedelta = datetime.timedelta(weeks=2)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 weeks"

    assert test_value, expected


def test_parse_timedelta_one_month_singular():
    """
    Test the return value for timedelta(days=30).

    Should return "1 month".
    """
    timedelta = datetime.timedelta(days=30)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 month"

    assert test_value, expected


def test_parse_timedelta_two_months_plural():
    """
    Test the return value for timedelta(days=60).

    Should return "2 months".
    """
    timedelta = datetime.timedelta(days=60)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 months"

    assert test_value, expected


def test_parse_timedelta_one_year_singular():
    """
    Test the return value for timedelta(seconds=365).

    Should return "1 year".
    """
    timedelta = datetime.timedelta(days=365)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 year"

    assert test_value, expected


def test_parse_timedelta_two_years_plural():
    """
    Test the return value for timedelta(days=730).

    Should return "2 years".
    """
    timedelta = datetime.timedelta(days=730)
    test_value = time.parse_timedelta(timedelta)
    expected = "2 years"

    assert test_value, expected


def test_parse_timedelta_none():
    """
    Test the return value for None.

    Should return "an eternity".
    """
    timedelta = None
    test_value = time.parse_timedelta(timedelta)
    expected = "an eternity"

    assert test_value, expected


def test_parse_timedelta_compound_time_expression():
    """
    Test the return value for timedelta(days=425, seconds=1).

    Should return "1 year, 2 months and 1 second".
    """
    timedelta = datetime.timedelta(days=425, seconds=1)
    test_value = time.parse_timedelta(timedelta)
    expected = "1 year, 2 months and 1 second"

    assert test_value, expected

# Possible future update, not implemented yet.
#
# def test_extract_time_return_value_for_absurdly_low_numbers():
#     """
#     Test the return value for negative numbers.

#     Should return a timedelta and datetime.datetime.min.
#     """
#     test_args = ("-999999999999999999", "years")
#     (first, second) = time.extract_time(test_args)
#     should_be = datetime.datetime.min

#     self.assertTrue(isinstance(first, datetime.timedelta))
#     self.assertEqual(second, should_be)
