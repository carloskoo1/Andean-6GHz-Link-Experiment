import unittest
from datetime import datetime
from pathlib import Path

from campaign_labeler import configuration_match, label_for
from campaign_orchestrator import load_config, schedule

HERE = Path(__file__).parent


class LabelerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = schedule(load_config(HERE / "campaign_plan.template.json"))

    def test_baseline_label(self):
        row = label_for(self.rows, "2026-09-10T09:30:00-05:00")
        self.assertEqual("BASELINE", row["phase"])
        self.assertEqual("BASE_7000_20", row["scenario_id"])

    def test_gap_is_outside_schedule(self):
        self.assertIsNone(label_for(self.rows, "2026-08-31T23:59:59-05:00"))

    def test_first_treatment(self):
        row = label_for(self.rows, "2026-09-16T00:01:00-05:00")
        self.assertEqual("F6655_B20", row["scenario_id"])

    def test_configuration_match(self):
        label = {"frequency_mhz": 6655, "bandwidth_mhz": 20}
        active_test = {
            "protocol": "TCP",
            "duration_seconds": 15,
            "omit_seconds": 2,
            "parallel_streams": 1,
        }
        self.assertEqual(
            "YES",
            configuration_match(
                {
                    "operating_frequency_mhz": 6655.0,
                    "channel_bandwidth_mhz": 20.0,
                },
                label,
                "radio_link_local",
                active_test,
            ),
        )
        self.assertEqual(
            "NO",
            configuration_match(
                {
                    "operating_frequency_mhz": 7000.0,
                    "channel_bandwidth_mhz": 20.0,
                },
                label,
                "radio_link_local",
                active_test,
            ),
        )


if __name__ == "__main__":
    unittest.main()
