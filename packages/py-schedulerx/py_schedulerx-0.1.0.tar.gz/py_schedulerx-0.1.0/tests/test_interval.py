import unittest
from py_schedulerx.interval import IntervalParser


class TestIntervalParser(unittest.TestCase):
    
    def test_parse_seconds(self):
        self.assertEqual(IntervalParser.parse("30s"), 30.0)
        self.assertEqual(IntervalParser.parse("5sec"), 5.0)
        self.assertEqual(IntervalParser.parse("10 seconds"), 10.0)
    
    def test_parse_minutes(self):
        self.assertEqual(IntervalParser.parse("5m"), 300.0)
        self.assertEqual(IntervalParser.parse("2min"), 120.0)
        self.assertEqual(IntervalParser.parse("1 minute"), 60.0)
    
    def test_parse_hours(self):
        self.assertEqual(IntervalParser.parse("2h"), 7200.0)
        self.assertEqual(IntervalParser.parse("1hour"), 3600.0)
        self.assertEqual(IntervalParser.parse("3 hours"), 10800.0)
    
    def test_parse_days(self):
        self.assertEqual(IntervalParser.parse("1d"), 86400.0)
        self.assertEqual(IntervalParser.parse("2day"), 172800.0)
        self.assertEqual(IntervalParser.parse("1 days"), 86400.0)
    
    def test_parse_numeric(self):
        self.assertEqual(IntervalParser.parse(60), 60.0)
        self.assertEqual(IntervalParser.parse(30.5), 30.5)
    
    def test_parse_float_string(self):
        self.assertEqual(IntervalParser.parse("30.5s"), 30.5)
        self.assertEqual(IntervalParser.parse("1.5m"), 90.0)
    
    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            IntervalParser.parse("invalid")
        
        with self.assertRaises(ValueError):
            IntervalParser.parse("30x")
        
        with self.assertRaises(ValueError):
            IntervalParser.parse("")


if __name__ == "__main__":
    unittest.main()
