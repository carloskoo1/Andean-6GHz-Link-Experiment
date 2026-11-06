import argparse
import collections
import json
import sqlite3
import statistics
import subprocess
from pathlib import Path

from sys import path
path.insert(0, str(Path("prospective_28d/analysis_retrospective")))
from reconcile_weather import CAMPAIGN, DB, stamp

RF = "dl_rssi_dbm ul_rssi_dbm dl_snr_db ul_snr_db ap_tx_power_dbm sm_tx_power_dbm".split()
WX = "temp_avg_C hum_avg_pct pres_avg_hPa rain_1min_mm rain_1h_mm wind_speed_ms".split()
COUNTERS = "sysRebootCounter sysHardRebootCounter sysSoftRebootCounter sysWDTRebootCounter".split()
CHAIN = "rssi_c0p rssi_c0e rssi_c1p rssi_c1e".split()


def describe(values):
    values = [v for v in values if v is not None]
    if not values:
        return {"n": 0}
    return dict(n=len(values), min=min(values), median=statistics.median(values), max=max(values))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("weather", type=Path)
    args = parser.parse_args()
    weather = args.weather
    snapshot = json.loads((weather / "snapshot.json").read_text())
    paired = json.loads((weather / "pairing.json").read_text())
    matches = {r["tcp_id"]: r for r in paired["rows"]}
    station_rows = {s: {r["source_id"]: r for r in rows} for s, rows in snapshot["weather"].items()}
    plan = json.loads(Path("prospective_28d/field_v3/plan.json").read_text())
    assert plan["campaign_id"] == snapshot["campaign_id"] == CAMPAIGN
    cutoff = stamp(snapshot["observed_at_utc"])
    runtime = Path("prospective_runtime")
    operational = {}
    for k in ["STATUS", "state", "HALT", "PENDING"]:
        file = runtime / (k + ".json")
        if file.exists():
            data = json.loads(file.read_text())
            allowed = "status observed_at_utc segment_id segment cycle slot verified_at analysis_start last_measurement_slot reason".split()
            operational[k] = {k: data[k] for k in allowed if k in data}
        else:
            operational[k] = None
    events = [json.loads(line) for line in (runtime / "events.jsonl").read_text().splitlines()]
    events = [e for e in events if stamp(e["timestamp_utc"]) <= cutoff]
    verified = {e["state"]["segment_id"]: e["state"] for e in events if e["event"] == "WINDOW_VERIFIED"}
    event_counts = collections.Counter(e["event"] for e in events)
    halt = next((e["timestamp_utc"] for e in events if e["event"] == "MISSED_WINDOW_HALT"), None)
    errors = collections.Counter()
    for e in events:
        if e["event"] != "CONTROLLER_ERROR" or (halt and stamp(e["timestamp_utc"]) >= stamp(halt)):
            continue
        error = e["error"]
        for pattern, label in [
            ("Remote endpoint unreachable", "endpoint remoto inaccesible"),
            ("No route to host", "SSH sin ruta"),
            ("Connection timed out", "SSH timeout"),
            ("Power/gain changed", "alerta potencia/ganancia"),
            ("Radio identity mismatch", "identidad RF no coincide"),
            ("faltan variables", "variables obligatorias ausentes"),
        ]:
            if pattern in error:
                errors[label] += 1
                break
        else:
            errors["otro error"] += 1
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    c.execute("BEGIN")
    verifications = collections.defaultdict(list)
    for row in c.execute("SELECT * FROM prospective_rf_verification WHERE campaign_id=?", (CAMPAIGN,)):
        verifications[(row["test_id"], row["direction"])].append(json.loads(row["verification_json"]))
    cols = "id test_id direction timestamp_start_local status protocol duration_seconds omit_seconds parallel_streams measured_throughput_mbps rf_telemetry_id rf_time_delta_seconds".split() + RF
    tests = [dict(r) for r in c.execute("SELECT " + ",".join(cols) + " FROM active_throughput_6g WHERE campaign_id=? ORDER BY timestamp_start_utc,id", (CAMPAIGN,))]
    assert {r["id"] for r in tests} == set(matches), "TCP cambió entre las dos lecturas"
    chain_counts = {}
    for name in CHAIN:
        total, n = c.execute(
            "SELECT count(*), count(NULLIF(TRIM(" + name + "), '')) FROM radio_link_local WHERE timestamp_utc>=? AND timestamp_utc<?",
            ("2026-11-02T05:00", "2026-11-03T05:00")).fetchone()
        chain_counts[name] = dict(rows=total, nonempty=n)
    result = []
    for w in plan["windows"]:
        if stamp(w["start_local"]) > cutoff:
            continue
        sid = w["segment_id"]
        rows = [r for r in tests if stamp(w["start_local"]) <= stamp(r["timestamp_start_local"]) < stamp(w["end_local"])]
        details = []
        radio_rows = {}
        expected = (w["frequency_mhz"], w["bandwidth_mhz"])
        for r in rows:
            candidates = verifications[r["test_id"], r["direction"]]
            live = candidates[0] if len(candidates) == 1 else {}
            live_ok = (live.get("ap_f"), live.get("ap_b")) == (live.get("sm_f"), live.get("sm_b")) == expected and live.get("sm_connection_state") == 3
            eligible = (live_ok and r["status"] == "OK" and (r["protocol"] or "").upper() == "TCP" and
                        (r["duration_seconds"], r["omit_seconds"], r["parallel_streams"]) == (8, 1, 1)
                        and r["measured_throughput_mbps"] is not None and sid in verified
                        and stamp(r["timestamp_start_local"]) >= stamp(verified[sid]["analysis_start"]))
            rf_ok = eligible and r["rf_time_delta_seconds"] is not None and abs(r["rf_time_delta_seconds"]) <= 300
            if rf_ok and r["rf_telemetry_id"] not in radio_rows:
                raw = c.execute("SELECT dashboard_raw_json,sm_dashboard_raw_json FROM radio_link_config_telemetry WHERE id=?", (r["rf_telemetry_id"],)).fetchone()
                if raw:
                    radio_rows[r["rf_telemetry_id"]] = [json.loads(v or "{}") for v in raw]
            details.append({**r, "eligible": eligible, "rf_recent": rf_ok, "live_ok": live_ok,
                            "live_rf": {k: live[k] for k in ("ap_f", "ap_b", "sm_f", "sm_b", "sm_connection_state", "ap_frequency_source", "sm_frequency_source") if k in live},
                            "sm_dashboard_differs": live_ok and (live.get("sm_dashboard_f"), live.get("sm_dashboard_b")) != expected})
        eligible = [r for r in details if r["eligible"]]
        by_hour = {}
        for hour in sorted({r["timestamp_start_local"][11:13] for r in eligible}):
            subset = [r for r in eligible if r["timestamp_start_local"][11:13] == hour]
            by_hour[hour] = {
                d: {"mbps": describe(r["measured_throughput_mbps"] for r in subset if r["direction"] == d),
                    **{k: describe(r[k] for r in subset if r["direction"] == d and r["rf_recent"]) for k in RF}}
                for d in ["DL", "UL"]}
        wx = {}
        for station in station_rows:
            ps = [matches[r["id"]][station] for r in eligible]
            good = [p for p in ps if p["within_120s"] and all(p[k] == 1 for k in ["bme_ok", "rain_ok", "wind_ok"])]
            samples = [station_rows[station][i] for i in sorted({p["source_id"] for p in good})]
            wx[station] = dict(original=sum(p["original_within_120s"] for p in ps), matched=len(good),
                later=sum(p["signed_delta_seconds"] > 0 for p in good), max_gap=max((p["delta_seconds"] for p in good), default=None),
                unique=len(samples), metrics={k: describe(r[k] for r in samples) for k in WX},
                wet_minutes=sum((r["rain_1min_mm"] or 0) > 0 for r in samples))
        dl = [r for r in eligible if r["direction"] == "DL"]
        ul = [r for r in eligible if r["direction"] == "UL"]
        hours_dl = len({r["timestamp_start_local"][:13] for r in dl})
        result.append(dict(window=w, opportunities=sum(e["event"] == "MEASUREMENT_OPPORTUNITY" and e.get("segment") == sid for e in events),
            verified=verified.get(sid), dl_hours=hours_dl, meets_DL_coverage=(len(dl) >= plan["coverage_rule"]["valid_DL_min"] and hours_dl >= plan["coverage_rule"]["hours_with_DL_min"]) if w["phase"] == "PROSPECTIVE" else None,
            counts=dict(collections.Counter(r["direction"] + "_" + r["status"] for r in details)),
            dl=describe(r["measured_throughput_mbps"] for r in dl), ul=describe(r["measured_throughput_mbps"] for r in ul),
            missing_live=sum(not r["live_ok"] for r in details), stale_dashboard=sum(r["sm_dashboard_differs"] for r in details),
            rf={k: describe(r[k] for r in eligible if r["rf_recent"] and r["direction"] == ("UL" if k.startswith("ul_") else "DL")) for k in RF},
            reboot_counters={role: {k: sorted({r[i][k] for r in radio_rows.values() if r[i].get(k) is not None}) for k in COUNTERS} for i, role in enumerate(["AP", "SM"])},
            by_hour=by_hour, weather=wx, tests=details))
    c.close()
    output = dict(cutoff=snapshot["observed_at_utc"], campaign=CAMPAIGN, start=plan["windows"][0]["start_local"],
        end=plan["windows"][-1]["end_local"], plan_windows=len(plan["windows"]), operational=operational, event_counts=dict(event_counts),
        halt_event=halt, errors_before_halt=dict(errors), controller_boot=subprocess.check_output(["uptime", "-s"], text=True).strip(),
        weather_audit=paired["summary"], weather_snapshot_sha256=paired["snapshot_sha256"], chains=chain_counts, segments=result)
    print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
