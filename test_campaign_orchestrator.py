import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campaign_orchestrator import (
    Orchestrator,
    bw_code,
    load_config,
    scenarios,
    schedule,
    validate_config,
)

HERE = Path(__file__).parent


class FakeAPI:
    def __init__(self):
        self.calls = []
        self.props = {
            "centerFrequency": "7000",
            "wirelessInterfaceHTMode": "1",
        }
        self.pending_previous = None

    def read(self):
        self.calls.append("read")
        return dict(self.props)

    def trial(self, scenario):
        self.calls.append(
            (
                "trial",
                scenario["frequency_mhz"],
                scenario["bandwidth_mhz"],
            )
        )
        self.pending_previous = dict(self.props)
        self.props = {
            "centerFrequency": str(scenario["frequency_mhz"]),
            "wirelessInterfaceHTMode": bw_code(
                scenario["bandwidth_mhz"]
            ),
        }

    def finish(self, apply):
        self.calls.append(("finish", apply))

        if not apply and self.pending_previous is not None:
            self.props = dict(self.pending_previous)

        self.pending_previous = None


class ControlledOrchestrator(Orchestrator):
    def __init__(self, *args, fail_stable_call=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_stable_call = fail_stable_call
        self.stable_calls = 0

    def probes(self):
        return True

    def stable(self, scenario, deadline):
        self.stable_calls += 1
        return self.stable_calls != self.fail_stable_call


class Tests(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config(
            HERE / "campaign_plan.template.json"
        )

    def make_scenario(self):
        return next(
            item
            for item in scenarios(self.cfg)
            if item["scenario_id"] == "F7000_B40"
        )

    def test_config(self):
        self.assertEqual(
            [],
            validate_config(self.cfg, True),
        )

    def test_codes(self):
        self.assertEqual(
            ("1", "2"),
            (bw_code(20), bw_code(40)),
        )

    def test_six_treatments(self):
        self.assertEqual(
            6,
            len(
                {
                    item["scenario_id"]
                    for item in scenarios(self.cfg)
                }
            ),
        )

    def test_schedule(self):
        rows = schedule(self.cfg)

        self.assertEqual(19, len(rows))
        self.assertEqual(63, sum(item["days"] for item in rows))

        totals = {}
        for item in rows[1:]:
            scenario_id = item["scenario_id"]
            totals[scenario_id] = (
                totals.get(scenario_id, 0)
                + item["days"]
            )

        self.assertEqual({7}, set(totals.values()))

    @patch("campaign_orchestrator.time.sleep", lambda _: None)
    @patch("campaign_orchestrator.ping", lambda _: True)
    def test_trial_then_confirm(self):
        config = copy.deepcopy(self.cfg)
        config["safety"]["minimum_successful_probes"] = 5

        with tempfile.TemporaryDirectory() as directory:
            config["outputs"]["directory"] = directory
            api = FakeAPI()
            orchestrator = Orchestrator(
                config,
                HERE / "x",
                api,
            )

            orchestrator.switch(self.make_scenario())

            self.assertIn(("trial", 7000, 40), api.calls)
            self.assertIn(("finish", True), api.calls)
            self.assertNotIn(("finish", False), api.calls)
            self.assertEqual(
                {
                    "centerFrequency": "7000",
                    "wirelessInterfaceHTMode": "2",
                },
                api.props,
            )

    def test_failure_before_confirmation_cancels_trial(self):
        config = copy.deepcopy(self.cfg)

        with tempfile.TemporaryDirectory() as directory:
            config["outputs"]["directory"] = directory
            api = FakeAPI()
            orchestrator = ControlledOrchestrator(
                config,
                HERE / "x",
                api,
                fail_stable_call=1,
            )

            with self.assertRaises(Exception):
                orchestrator.switch(self.make_scenario())

            self.assertIn(("trial", 7000, 40), api.calls)
            self.assertIn(("finish", False), api.calls)
            self.assertEqual(
                {
                    "centerFrequency": "7000",
                    "wirelessInterfaceHTMode": "1",
                },
                api.props,
            )

    def test_failure_after_confirmation_reapplies_previous(self):
        config = copy.deepcopy(self.cfg)

        with tempfile.TemporaryDirectory() as directory:
            config["outputs"]["directory"] = directory
            api = FakeAPI()
            orchestrator = ControlledOrchestrator(
                config,
                HERE / "x",
                api,
                fail_stable_call=2,
            )

            with self.assertRaises(Exception):
                orchestrator.switch(self.make_scenario())

            self.assertEqual(
                [
                    ("trial", 7000, 40),
                    ("trial", 7000, 20),
                ],
                [
                    call
                    for call in api.calls
                    if isinstance(call, tuple)
                    and call[0] == "trial"
                ],
            )
            self.assertEqual(
                2,
                api.calls.count(("finish", True)),
            )
            self.assertEqual(
                {
                    "centerFrequency": "7000",
                    "wirelessInterfaceHTMode": "1",
                },
                api.props,
            )


if __name__ == "__main__":
    unittest.main()
