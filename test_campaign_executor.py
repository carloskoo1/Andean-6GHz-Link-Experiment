import copy
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from campaign_executor import active_row, run_once, target_row
from campaign_orchestrator import load_config, schedule

HERE = Path(__file__).parent


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(HERE / "campaign_plan.template.json")
        self.rows = schedule(self.config)

    def test_before_experiment_has_no_active_experiment(self):
        row = active_row(self.rows, datetime.fromisoformat("2026-09-15T10:00:00-05:00"))
        self.assertIsNone(row)

    def test_first_experimental_row(self):
        row = active_row(self.rows, datetime.fromisoformat("2026-09-16T00:00:00-05:00"))
        self.assertEqual(1, row["sequence"])
        self.assertEqual("EXPERIMENT", row["phase"])

    def test_final_return_to_baseline(self):
        row = target_row(
            self.rows,
            datetime.fromisoformat("2026-10-28T00:01:00-05:00"),
            self.config["baseline"],
        )
        self.assertEqual("FINAL_BASELINE", row["sequence"])
        self.assertEqual((7000, 20), (row["frequency_mhz"], row["bandwidth_mhz"]))

    def test_dry_run_does_not_persist_state(self):
        with tempfile.TemporaryDirectory() as directory:
            config = copy.deepcopy(self.config)
            config["outputs"]["directory"] = directory
            cfg = Path(directory) / "campaign_plan.template.json"
            import json
            cfg.write_text(json.dumps(config), encoding="utf-8")
            (Path(directory) / "campaign_orchestrator.py").write_text("", encoding="utf-8")
            runner = Mock(return_value=Mock(returncode=0))
            run_once(cfg, datetime.fromisoformat("2026-09-16T00:01:00-05:00"), True, runner)
            self.assertFalse((Path(directory) / "executor_state.json").exists())
            self.assertIn("--dry-run", runner.call_args.args[0])

    def test_success_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            config = copy.deepcopy(self.config)
            config["outputs"]["directory"] = directory
            cfg = Path(directory) / "campaign_plan.template.json"
            import json
            cfg.write_text(json.dumps(config), encoding="utf-8")
            (Path(directory) / "campaign_orchestrator.py").write_text("", encoding="utf-8")
            runner = Mock(return_value=Mock(returncode=0))
            instant = datetime.fromisoformat("2026-09-16T00:01:00-05:00")
            run_once(cfg, instant, False, runner)
            run_once(cfg, instant, False, runner)
            self.assertEqual(1, runner.call_count)

    def test_failure_has_retry_cooldown(self):
        with tempfile.TemporaryDirectory() as directory:
            config = copy.deepcopy(self.config)
            config["outputs"]["directory"] = directory
            cfg = Path(directory) / "campaign_plan.template.json"
            import json
            cfg.write_text(json.dumps(config), encoding="utf-8")
            (Path(directory) / "campaign_orchestrator.py").write_text("", encoding="utf-8")
            runner = Mock(return_value=Mock(returncode=2))
            instant = datetime.fromisoformat("2026-09-16T00:01:00-05:00")
            with self.assertRaises(Exception):
                run_once(cfg, instant, False, runner)
            run_once(cfg, instant, False, runner)
            self.assertEqual(1, runner.call_count)


if __name__ == "__main__":
    unittest.main()
