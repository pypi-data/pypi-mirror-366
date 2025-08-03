import unittest
from shamsinox import date, timedelta
from shamsinox import PersianDate

class TestPersianDate(unittest.TestCase):
    def test_valid_date(self):
        """Test creation of a valid Persian date."""
        pd = PersianDate(1404, 5, 12)
        self.assertEqual(str(pd), "1404/05/12 (Mordad)")

    def test_invalid_date(self):
        """Test invalid date raises ValueError."""
        with self.assertRaises(ValueError):
            PersianDate(1404, 12, 30)  # Non-leap year Esfand has 29 days
        with self.assertRaises(ValueError):
            PersianDate(1404, 13, 1)   # Invalid month

    def test_gregorian_conversion(self):
        """Test conversion to Gregorian date."""
        pd = PersianDate(1404, 5, 12)
        gd = pd.to_gregorian()
        self.assertEqual(gd, date(2025, 8, 3))

    def test_from_gregorian(self):
        """Test conversion from Gregorian to Persian date."""
        gd = date(2025, 8, 3)
        pd = PersianDate.from_gregorian(gd)
        self.assertEqual(pd.year, 1404)
        self.assertEqual(pd.month, 5)
        self.assertEqual(pd.day, 12)

    def test_leap_year(self):
        """Test leap year calculations."""
        self.assertTrue(PersianDate._is_leap_year(1399))
        self.assertFalse(PersianDate._is_leap_year(1404))

    def test_date_arithmetic(self):
        """Test adding and subtracting days."""
        pd = PersianDate(1404, 5, 12)
        future = pd + timedelta(days=10)
        self.assertIsInstance(future, PersianDate)
        diff = future - pd
        self.assertEqual(diff, 10)

if __name__ == "__main__":
    unittest.main()