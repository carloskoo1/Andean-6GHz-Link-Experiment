#!/usr/bin/env python3
"""Pruebas locales, sin red ni radioenlaces."""
import datetime as dt
import unittest
from prospective_plan import make_schedule, validate

class ProspectivePlanTests(unittest.TestCase):
    def test_full_campaign(self):
        start = dt.datetime.fromisoformat("2026-11-01T00:00:00-05:00")
        rows = make_schedule(start)
        self.assertTrue(validate(rows))
        self.assertEqual(len([r for r in rows if r["phase"]=="PROSPECTIVE"]),42)
        self.assertEqual(len([r for r in rows if r["phase"]=="RESERVE"]),7)
        self.assertEqual(rows[-1]["end_local"],"2026-11-29T00:00:00-05:00")
    def test_reject_naive_time(self):
        with self.assertRaises(ValueError):
            make_schedule(dt.datetime(2026,11,1))
    def test_reject_misaligned_start(self):
        with self.assertRaises(ValueError):
            make_schedule(dt.datetime.fromisoformat("2026-11-01T08:00:00-05:00"))
    def test_no_authorization(self):
        rows = make_schedule(dt.datetime.fromisoformat("2026-11-01T00:00:00-05:00"))
        self.assertTrue(all(r["status"]=="PLANNED_NOT_AUTHORIZED" for r in rows))

if __name__ == "__main__":
    unittest.main()
