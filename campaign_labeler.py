#!/usr/bin/env python3
"""Exporta datos científicos con etiquetas del diseño 3x2 sin alterar SQLite."""
from __future__ import annotations

import argparse
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

from campaign_orchestrator import load_config, schedule

SOURCES = {
    "active_throughput_6g": "timestamp_start_local",
    "scientific_campaign_6g_integrated": "rf_timestamp_local",
}

LABEL_FIELDS = [
    "design_campaign_id", "design_phase", "design_sequence", "design_block",
    "design_scenario_id", "design_frequency_mhz", "design_bandwidth_mhz",
    "configuration_match",
]


def label_for(rows, timestamp):
    instant = datetime.fromisoformat(timestamp)
    for row in rows:
        if datetime.fromisoformat(row["start_local"]) <= instant < datetime.fromisoformat(row["end_local"]):
            return row
    return None


def configuration_match(row, label, table, active_test):
    if label is None:
        return "OUTSIDE_SCHEDULE"

    frequency = row.get("operating_frequency_mhz")
    bandwidth = row.get("channel_bandwidth_mhz")

    if frequency is None or bandwidth is None:
        return "MISSING_CONFIGURATION"

    radio_match = (
        int(float(frequency)) == int(label["frequency_mhz"])
        and int(float(bandwidth)) == int(label["bandwidth_mhz"])
    )

    if not radio_match:
        return "NO"

    if table == "active_throughput_6g":
        protocol = str(row.get("protocol") or "").upper()
        duration = row.get("duration_seconds")
        omit = row.get("omit_seconds")
        parallel = row.get("parallel_streams")

        if None in (duration, omit, parallel):
            return "MISSING_TEST_CONFIGURATION"

        test_match = (
            protocol == str(active_test["protocol"]).upper()
            and int(duration) == int(active_test["duration_seconds"])
            and int(omit) == int(active_test["omit_seconds"])
            and int(parallel) == int(active_test["parallel_streams"])
        )

        return "YES" if test_match else "NO_TEST_PROTOCOL"

    return "YES"


def export_table(
    connection,
    table,
    timestamp_field,
    rows,
    campaign_id,
    active_test,
    output,
):
    cursor = connection.execute(f'SELECT * FROM "{table}" ORDER BY "{timestamp_field}"')
    original = [item[0] for item in cursor.description]
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = {"rows": 0, "match_yes": 0, "match_no": 0, "outside": 0}
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LABEL_FIELDS + original, lineterminator="\n")
        writer.writeheader()
        for values in cursor:
            source = dict(zip(original, values))
            timestamp = source.get(timestamp_field)
            label = label_for(rows, timestamp) if timestamp else None
            match = configuration_match(
                source,
                label,
                table,
                active_test,
            )
            record = {
                "design_campaign_id": campaign_id,
                "design_phase": label["phase"] if label else "OUTSIDE_SCHEDULE",
                "design_sequence": label["sequence"] if label else "",
                "design_block": label.get("block", "") if label else "",
                "design_scenario_id": label["scenario_id"] if label else "",
                "design_frequency_mhz": label["frequency_mhz"] if label else "",
                "design_bandwidth_mhz": label["bandwidth_mhz"] if label else "",
                "configuration_match": match,
                **source,
            }
            writer.writerow(record)
            counts["rows"] += 1
            if match == "YES": counts["match_yes"] += 1
            elif match == "NO": counts["match_no"] += 1
            elif match == "OUTSIDE_SCHEDULE": counts["outside"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    rows = schedule(config)
    connection = sqlite3.connect(f"file:{args.database.resolve()}?mode=ro", uri=True)
    try:
        existing = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table, timestamp_field in SOURCES.items():
            if table not in existing:
                raise SystemExit(f"ERROR: falta la tabla {table}.")
            output = args.output_directory / f"{table}_3x2_labeled.csv"
            counts = export_table(
                connection,
                table,
                timestamp_field,
                rows,
                config["campaign_id"],
                config["active_test"],
                output,
            )
            print(f"{output}: {counts}")
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
