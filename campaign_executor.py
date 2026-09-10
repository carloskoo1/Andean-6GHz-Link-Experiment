#!/usr/bin/env python3
"""Idempotent scheduled executor for the Andean 6 GHz campaign."""
from __future__ import annotations

import argparse
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from campaign_orchestrator import CampaignError, load_config, schedule


def active_row(rows, instant):
    for row in rows:
        start = datetime.fromisoformat(row["start_local"])
        end = datetime.fromisoformat(row["end_local"])
        if start <= instant < end:
            return row
    return None


def target_row(rows, instant, baseline_config):
    row = active_row(rows, instant)
    if row is not None:
        return row if row["phase"] == "EXPERIMENT" else None
    experiment_rows = [r for r in rows if r["phase"] == "EXPERIMENT"]
    if experiment_rows and instant >= datetime.fromisoformat(experiment_rows[-1]["end_local"]):
        return {
            "sequence": "FINAL_BASELINE",
            "scenario_id": "BASE_7000_20",
            "phase": "FINAL_BASELINE",
            "frequency_mhz": baseline_config["frequency_mhz"],
            "bandwidth_mhz": baseline_config["bandwidth_mhz"],
        }
    return None


def load_executor_state(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"Estado del ejecutor ilegible: {exc}") from exc


def save_executor_state(path, row, instant):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "sequence": row["sequence"],
        "scenario_id": row["scenario_id"],
        "applied_local": instant.isoformat(),
    }, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def save_failure(path, row, instant, message, attempts):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "failed_sequence": row["sequence"],
        "failed_scenario_id": row["scenario_id"],
        "last_failure_local": instant.isoformat(),
        "attempts": attempts,
        "error": message,
    }, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def run_once(config_path, instant=None, dry_run=False, runner=subprocess.run):
    config_path = config_path.resolve()
    config = load_config(config_path)
    rows = schedule(config)
    instant = instant or datetime.now().astimezone()
    row = target_row(rows, instant, config["baseline"])
    if row is None:
        print("Sin transición: fuera del periodo experimental.")
        return 0

    output = Path(config["outputs"]["directory"])
    if not output.is_absolute():
        output = config_path.parent / output
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "executor_state.json"
    failure_path = output / "executor_failure.json"
    lock_path = output / "executor.lock"

    with lock_path.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Otro ejecutor ya está activo.")
            return 0

        state = load_executor_state(state_path)
        if state.get("sequence") == row["sequence"]:
            print(f"Sin transición: {row['scenario_id']} ya fue aplicado.")
            return 0

        failure = load_executor_state(failure_path)
        retry_seconds = int(config.get("safety", {}).get("executor_retry_seconds", 1800))
        if failure.get("failed_sequence") == row["sequence"]:
            last_failure = datetime.fromisoformat(failure["last_failure_local"])
            if instant < last_failure + timedelta(seconds=retry_seconds):
                print(f"Reintento aplazado para {row['scenario_id']}.")
                return 0

        command = [sys.executable, str(config_path.parent / "campaign_orchestrator.py"),
                   "switch", "--config", str(config_path),
                   "--scenario", row["scenario_id"]]
        if dry_run:
            command.append("--dry-run")
        result = runner(command, cwd=config_path.parent, check=False)
        if result.returncode:
            message = f"Falló la transición a {row['scenario_id']} (rc={result.returncode})."
            if not dry_run:
                attempts = int(failure.get("attempts", 0)) + 1
                save_failure(failure_path, row, instant, message, attempts)
            raise CampaignError(message)
        if not dry_run:
            save_executor_state(state_path, row, instant)
            if failure_path.exists():
                failure_path.unlink()
        print(f"Transición {'simulada' if dry_run else 'aplicada'}: {row['scenario_id']}")
        return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--at", help="Instante ISO 8601 para pruebas")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        instant = datetime.fromisoformat(args.at) if args.at else None
        return run_once(args.config, instant, args.dry_run)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
