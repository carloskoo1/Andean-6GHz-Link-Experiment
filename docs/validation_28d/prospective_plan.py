#!/usr/bin/env python3
"""Generador OFFLINE de calendario prospectivo. No controla equipos RF."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path

FREQUENCIES = (6475, 6655, 7000)
BANDWIDTHS = (20, 40)
CYCLES = 7
TREATMENTS = tuple((f, b) for f in FREQUENCIES for b in BANDWIDTHS)
# Candidate chosen by reproducible seeded search (seed=20261027);
# balanced day/night 3:4 or 4:3 per treatment; not yet approved.
PERMUTATIONS = (
    (3, 4, 5, 2, 1, 0),
    (4, 2, 1, 0, 5, 3),
    (0, 5, 3, 4, 2, 1),
    (1, 0, 4, 3, 5, 2),
    (2, 3, 0, 1, 4, 5),
    (4, 1, 0, 5, 3, 2),
    (0, 1, 2, 5, 3, 4),
)

def make_schedule(start):
    if start.tzinfo is None or start.utcoffset() != dt.timedelta(hours=-5):
        raise ValueError("Inicio debe incluir zona -05:00 (America/Lima)")
    if start.minute or start.second or start.microsecond or start.hour not in (0, 12):
        raise ValueError("Inicio debe ser 00:00 o 12:00 exactas")
    rows = []
    for cycle, order in enumerate(PERMUTATIONS, 1):
        anchor = start + dt.timedelta(days=(cycle - 1) * 4)
        for slot, treatment_index in enumerate(order, 1):
            f, b = TREATMENTS[treatment_index]
            begin = anchor + dt.timedelta(hours=12 * (slot - 1))
            end = begin + dt.timedelta(hours=12)
            rows.append(dict(campaign_id="LUISITA_PROSPECTIVE_28D_2026", phase="PROSPECTIVE",
                cycle=cycle, slot=slot, segment_id=f"P{cycle:02d}_S{slot:02d}",
                scenario_id=f"F{f}_B{b}", frequency_mhz=f, bandwidth_mhz=b,
                start_local=begin.isoformat(), end_local=end.isoformat(),
                status="PLANNED_NOT_AUTHORIZED"))
        reserve_start = anchor + dt.timedelta(hours=72)
        rows.append(dict(campaign_id="LUISITA_PROSPECTIVE_28D_2026", phase="RESERVE",
            cycle=cycle, slot=7, segment_id=f"P{cycle:02d}_RESERVE",
            scenario_id="NO_RF_CHANGE", frequency_mhz="", bandwidth_mhz="",
            start_local=reserve_start.isoformat(),
            end_local=(reserve_start + dt.timedelta(hours=24)).isoformat(),
            status="PLANNED_NOT_AUTHORIZED"))
    validate(rows)
    return rows

def validate(rows):
    assert len(rows) == 49
    for cycle in range(1, 8):
        batch = [r for r in rows if r["cycle"] == cycle]
        assert len(batch) == 7
        assert set(r["scenario_id"] for r in batch[:6]) == {
            f"F{f}_B{b}" for f, b in TREATMENTS}
        for first, second in zip(batch, batch[1:]):
            assert first["end_local"] == second["start_local"]
        assert batch[-1]["phase"] == "RESERVE"
    for first, second in zip(rows, rows[1:]):
        assert first["end_local"] == second["start_local"]
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="ISO local con -05:00; NO autoriza ejecución")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    start = dt.datetime.fromisoformat(args.start)
    data = make_schedule(start)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    print(json.dumps({"mode":"OFFLINE_ONLY","authorized":False,"cycles":7,
        "treatments":42,"reserve_windows":7,"rows":len(data),
        "start":data[0]["start_local"],"end":data[-1]["end_local"]},indent=2))

if __name__ == "__main__":
    main()
