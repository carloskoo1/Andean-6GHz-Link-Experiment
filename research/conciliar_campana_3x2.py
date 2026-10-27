#!/usr/bin/env python3
"""Conciliación no intrusiva 3x2 sobre instantánea verificada."""
from pathlib import Path
from datetime import datetime,timedelta
from collections import Counter,defaultdict
import sqlite3,csv,json,hashlib

import sys
if len(sys.argv)!=2:
    raise SystemExit("Uso: python3 conciliar_campana_3x2.py /ruta/a/respaldo_privado")
ROOT=Path(sys.argv[1]).resolve()
SNAP=ROOT/"weather_local_CU01_cierre.sqlite3"
def dt(s): return datetime.fromisoformat(s)
schedule=list(csv.DictReader((ROOT/"campaign_schedule.csv").open()))
experimental=[r for r in schedule if r["phase"]=="EXPERIMENT"]
assert len(experimental)==18
db=sqlite3.connect(SNAP.as_uri()+"?mode=ro",uri=True)
db.execute("PRAGMA query_only=ON")
data=db.execute("""SELECT timestamp_start_local,direction,status,
    operating_frequency_mhz,channel_bandwidth_mhz,
    route_verified,ping_status,measured_throughput_mbps
    FROM active_throughput_6g WHERE timestamp_start_local >= ?
    AND timestamp_start_local < ? ORDER BY timestamp_start_local""",
    (experimental[0]["start_local"],experimental[-1]["end_local"])).fetchall()
db.close()
blocks=[]
allstats=Counter()
for r in experimental:
    begin,end=dt(r["start_local"]),dt(r["end_local"])
    sub=[x for x in data if begin<=dt(x[0])<end]
    freq,bw=int(r["frequency_mhz"]),int(r["bandwidth_mhz"])
    counters=Counter()
    for ts,direction,status,rf,bwidth,route,ping,mbps in sub:
        counters["measured"]+=1
        counters[direction+"_total"]+=1
        counters[status+"_total"]+=1
        counters[direction+"_"+status]+=1
        if rf is None or bwidth is None:
            counters["unknown_config"]+=1
        elif int(rf)!=freq or int(bwidth)!=bw:
            counters["config_mismatch"]+=1
            if dt(ts)>=begin+timedelta(minutes=45):
                counters["mismatch_after_45min"]+=1
        if status=="OK" and (route!=1 or ping!="OK"):
            counters["ok_but_check_issue"]+=1
    expectation=int(r["days"])*96*2
    allstats.update(counters)
    blocks.append({
        "sequence":int(r["sequence"]),"block":int(r["block"]),
        "scenario":r["scenario_id"],"planned_start_local":r["start_local"],
        "planned_end_local":r["end_local"],
        "nominal_tests":expectation,"recorded_tests":len(sub),
        "nominal_coverage_pct":round(100*len(sub)/expectation,2),
        "DL_OK":counters["DL_OK"],"UL_OK":counters["UL_OK"],
        "DL_ERROR":counters["DL_ERROR"],"UL_ERROR":counters["UL_ERROR"],
        "config_unknown":counters["unknown_config"],
        "config_mismatch":counters["config_mismatch"],
        "mismatch_after_45min":counters["mismatch_after_45min"],
        "ok_but_check_issue":counters["ok_but_check_issue"],
    })
counts=Counter()
with (ROOT/"campaign_events.jsonl").open() as f:
    for line in f:
        try:ev=json.loads(line)
        except:continue
        counts[(ev.get("event"),ev.get("result"))]+=1
summary={
    "basis":"locally verified SQLite snapshot at closure; read-only",
    "campaign_start":experimental[0]["start_local"],
    "campaign_end":experimental[-1]["end_local"],
    "experimental_days":42,
    "blocks":18,
    "scenarios_per_combination":dict(Counter(r["scenario_id"] for r in experimental)),
    "nominal_tests_per_direction":42*96,
    "nominal_tests_both":42*96*2,
    "actual_tests_both":len(data),
    "nominal_coverage_pct":round(100*len(data)/(42*96*2),2),
    "totals":dict(allstats),
    "blocks_detail":blocks,
    "event_types":[{"event":k[0],"result":k[1],"count":v} for k,v in counts.most_common()],
    "warnings":[
        "Nominal cadence assumes DL and UL each 15 min; not measured uptime or end-to-end availability",
        "Formal throughput campaign timer errors separately audit; active measurements might be another pipeline",
        "Configuration mismatch in first 45 minutes can reflect transition; later mismatches require review",
        "Snapshot captured after scheduled end with acquisition continuing; never rewrite post-end records as experimental",
        "No independent validation of cloud backup."
    ]
}
outfile=ROOT/"conciliation_3x2.json"
outfile.write_text(json.dumps(summary,ensure_ascii=False,indent=2))
outfile.chmod(0o600)
print(json.dumps({k:v for k,v in summary.items() if k not in ("blocks_detail","event_types")},ensure_ascii=False,indent=2))
print("BLOCKS",json.dumps([{k:z[k] for k in ("sequence","scenario","nominal_coverage_pct","DL_OK","UL_OK","DL_ERROR","UL_ERROR","config_mismatch","mismatch_after_45min")} for z in blocks],ensure_ascii=False))
