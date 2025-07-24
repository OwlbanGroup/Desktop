import unittest
from datetime import datetime, timedelta
from revenue_tracking import RevenueTracker, RevenueRecord

class TestRevenueTracker(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite database for testing
        self.tracker = RevenueTracker("sqlite:///:memory:")

    def test_add_record(self):
        record = self.tracker.add_record("Test Sale", 100.0)
        self.assertEqual(record.description, "Test Sale")
        self.assertEqual(record.amount, 100.0)
        self.assertIsNotNone(record.date)

    def test_add_record_negative_amount(self):
        with self.assertRaises(ValueError):
            self.tracker.add_record("Invalid Sale", -50.0)

    def test_add_record_empty_description(self):
        with self.assertRaises(ValueError):
            self.tracker.add_record("", 50.0)

    def test_get_all_records(self):
        self.tracker.add_record("Sale 1", 100.0)
        self.tracker.add_record("Sale 2", 200.0)
        records = self.tracker.get_all_records()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].description, "Sale 2")  # Most recent first
        self.assertEqual(records[1].description, "Sale 1")

    def test_get_total_revenue(self):
        self.tracker.add_record("Sale 1", 100.0)
        self.tracker.add_record("Sale 2", 200.0)
        total = self.tracker.get_total_revenue()
        self.assertEqual(total, 300.0)

    def test_generate_report(self):
        self.tracker.add_record("Sale 1", 100.0, datetime.utcnow() - timedelta(days=1))
        self.tracker.add_record("Sale 2", 200.0, datetime.utcnow())
        report = self.tracker.generate_report()
        self.assertIn("Sale 1", report)
        self.assertIn("Sale 2", report)
        self.assertIn("Total Revenue: $300.00", report)

if __name__ == "__main__":
    unittest.main()
