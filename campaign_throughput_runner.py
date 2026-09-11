#!/usr/bin/env python3
"""Ejecutor de mediciones activas formales de la campaña Andean 6 GHz 3x2."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from campaign_orchestrator import load_config, schedule


ATMOSLINK_ROOT = Path("/home/carlos/Proyectos/EstacionMeteorologica")
ATMOSLINK_PYTHON = ATMOSLINK_ROOT / "venv/bin/python"
ATMOSLINK_DATABASE = ATMOSLINK_ROOT / "SQLite/CU01/weather_local.db"
ATMOSLINK_CSV = ATMOSLINK_ROOT / "Data/exports/active_throughput_6g.csv"


def active_row(rows, instant):
    for row in rows:
        start = datetime.fromisoformat(row["start_local"])
        end = datetime.fromisoformat(row["end_local"])
        if start <= instant < end:
            return row
    return None


def load_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_once(config_path, instant=None, dry_run=False):
    config_path = config_path.resolve()
    config = load_config(config_path)
    rows = schedule(config)

    instant = instant or datetime.now().astimezone()
    row = active_row(rows, instant)

    if row is None or row.get("phase") != "EXPERIMENT":
        print("Sin medición formal: fuera de fase EXPERIMENT.")
        return 0

    output_dir = Path(config["outputs"]["directory"])
    if not output_dir.is_absolute():
        output_dir = config_path.parent / output_dir

    state_path = output_dir / "executor_state.json"
    state = load_json(state_path)

    if state.get("sequence") != row.get("sequence"):
        print(
            "Escenario programado aún no confirmado por el ejecutor."
        )
        print(
            f"Programado={row.get('scenario_id')} "
            f"Aplicado={state.get('scenario_id', 'DESCONOCIDO')}"
        )
        if not dry_run:
            print("Sin medición formal por seguridad.")
            return 0
        print("DRY-RUN: se continúa únicamente para validar el comando.")

    test = config["active_test"]

    command = [
        str(ATMOSLINK_PYTHON),
        "-m",
        "weather_station.telemetry.active_throughput_6g",
        "--database",
        str(ATMOSLINK_DATABASE),
        "--output-csv",
        str(ATMOSLINK_CSV),
        "--direction",
        "BOTH",
        "--campaign-id",
        str(config["campaign_id"]),
        "--duration",
        str(test["duration_seconds"]),
        "--omit",
        str(test["omit_seconds"]),
        "--parallel",
        str(test["parallel_streams"]),
    ]

    print(
        f"Campaña formal: {row['scenario_id']} | "
        f"{row['frequency_mhz']} MHz / {row['bandwidth_mhz']} MHz | "
        f"{test['protocol']} "
        f"{test['duration_seconds']}/{test['omit_seconds']}/"
        f"{test['parallel_streams']}"
    )

    if dry_run:
        print("DRY-RUN:", " ".join(command))
        return 0

    result = subprocess.run(
        command,
        cwd=ATMOSLINK_ROOT,
        check=False,
    )

    if result.returncode != 0:
        print(
            f"ERROR: medición formal terminó con rc={result.returncode}",
            file=sys.stderr,
        )
        return result.returncode

    print("Medición formal completada.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--at", help="Instante ISO 8601 para pruebas")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    instant = datetime.fromisoformat(args.at) if args.at else None
    return run_once(args.config, instant, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
