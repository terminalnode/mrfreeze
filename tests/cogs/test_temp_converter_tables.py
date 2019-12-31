"""Unittest for conversion tables in the TemperatureConverter cog."""

import unittest

from mrfreeze.cogs.temp_converter import TempUnit
from mrfreeze.cogs.temp_converter import TemperatureConverter

from tests import helpers


class TemperatureConverterCogConversionTablesUnitTest(unittest.TestCase):
    """Test the conversion tables in the TemperatureConverter cog."""

    def setUp(self):
        """Set up a clean environment for each test."""
        self.bot = helpers.MockMrFreeze()
        self.cog = TemperatureConverter(self.bot)

    def test_celsius_table_to_celsius(self):
        """
        Test celsius_table() with TempUnit.C as dest.

        Should return the same as input.
        """
        result = self.cog.celsius_table(50, TempUnit.C)
        self.assertEqual(50, result)

    def test_celsius_table_to_fahrenheit(self):
        """
        Test celsius_table() with TempUnit.F as dest.

        Should return 122 F with temp = 50.
        """
        result = self.cog.celsius_table(50, TempUnit.F)
        self.assertEqual(122, result)

    def test_celsius_table_to_kelvin(self):
        """
        Test celsius_table() with TempUnit.K as dest.

        Should return 323.15 with temp = 50.
        """
        result = self.cog.celsius_table(50, TempUnit.K)
        self.assertEqual(323.15, result)

    def test_celsius_table_to_rankine(self):
        """
        Test celsius_table() with TempUnit.R as dest.

        Should return 581.67 with temp = 50.
        """
        result = self.cog.celsius_table(50, TempUnit.R)
        self.assertEqual(581.67, result)

    def test_fahrenheit_table_to_celsius(self):
        """
        Test fahrenheit_table() with TempUnit.C as dest.

        Should return 10 with temp = 50.
        """
        result = self.cog.fahrenheit_table(50, TempUnit.C)
        self.assertEqual(10, result)

    def test_fahrenheit_table_to_fahrenheit(self):
        """
        Test fahrenheit_table() with TempUnit.F as dest.

        Should return same as input.
        """
        result = self.cog.fahrenheit_table(50, TempUnit.F)
        self.assertEqual(50, result)

    def test_fahrenheit_table_to_kelvin(self):
        """
        Test fahrenheit_table() with TempUnit.K as dest.

        Should return 283.15 with temp = 50.
        """
        result = self.cog.fahrenheit_table(50, TempUnit.K)
        self.assertEqual(283.15, result)

    def test_fahrenheit_table_to_rankine(self):
        """
        Test fahrenheit_table() with TempUnit.R as dest.

        Should return 509.67 with temp = 50.
        """
        result = self.cog.fahrenheit_table(50, TempUnit.R)
        self.assertEqual(509.67, result)

    def test_kelvin_table_to_celsius(self):
        """
        Test kelvin_table() with TempUnit.C as dest.

        Should return 50 with temp = 323.15.
        No further testing necessary since kelvin_table just calls
        celsius_table with temperature converted to celsius.
        """
        result = self.cog.kelvin_table(323.15, TempUnit.C)
        self.assertEqual(50, result)

    def test_rankine_table_to_fahrenheit(self):
        """
        Test rankine_table() with TempUnit.F as dest.

        Should return 50 with temp = 509.67.
        No further testing necessary since rankine_table just calls
        fahrenheit_table with temperature converted to fahrenheit.
        """
        result = self.cog.rankine_table(509.67, TempUnit.F)
        self.assertEqual(50, result)
