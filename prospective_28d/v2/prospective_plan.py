#!/usr/bin/env python3
"""Planificador offline y simulador de la fase prospectiva 28 d.

SEGURIDAD: NO contiene conectividad a radios, clientes API, SSH ni ejecucion
RF. Solo escribe dentro de 'salidas_offline' en su propio directorio.
NO ES UN EJECUTOR. No puede habilitar campañas ni servicios systemd.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "plan_prospectivo_BORRADOR.json"
OUT = ROOT / "salidas_offline"
COLUMNS = (
    "sequence", "cycle", "slot", "phase", "scenario_id", "frequency_mhz",
    "bandwidth_mhz", "start_local", "end_local", "hours", "daypart",
    "study_eligible", "reference_requested"
)


def read_plan():
    p = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_plan(p)
    return p


def validate_plan(p):
    required = {"DRAFT_NOT_AUTHORIZED"}
    if p.get("status") not in required:
        raise ValueError("El paquete offline requiere estado DRAFT_NOT_AUTHORIZED")
    if p.get("timezone") != "America/Lima":
        raise ValueError("La zona horaria planificada debe ser America/Lima")
    if [p.get("cycle_count"), p.get("cycle_hours"), p.get("slot_hours"),
        p.get("treatment_hours_per_cycle"), p.get("reserve_hours_per_cycle")] != [7, 96, 12, 72, 24]:
        raise ValueError("Esquema 7x(6*12h+24h) obligatorio para este borrador")
    if len(p.get("frequency_levels_mhz", [])) != 3 or len(p.get("bandwidth_levels_mhz", [])) != 2:
        raise ValueError("Niveles duplicados o ausentes")
    if set(p.get("frequency_levels_mhz", [])) != {6475, 6655, 7000}:
        raise ValueError("Frecuencias no corresponden al factorial")
    if set(p.get("bandwidth_levels_mhz", [])) != {20, 40}:
        raise ValueError("Anchos no corresponden al factorial")
    start = datetime.fromisoformat(p["proposed_start_local"])
    if (start.hour, start.minute, start.second, start.microsecond) != (0,0,0,0):
        raise ValueError("Inicio debe ser medianoche para el balance de franjas")
    if p.get("reference_configuration") != {"frequency_mhz":7000,"bandwidth_mhz":20}:
        raise ValueError("Referencia modificada: requiere revisión del protocolo")
    if start.tzinfo is None or start.utcoffset() != timedelta(hours=-5):
        raise ValueError("Inicio requiere desplazamiento UTC-05:00")
    if start.astimezone(ZoneInfo("America/Lima")).replace(tzinfo=None) != start.replace(tzinfo=None):
        raise ValueError("Inicio inconsistente con hora local de Perú")
    if not p.get("preconditions") or any(v is not False for v in p["preconditions"].values()):
        raise ValueError("El paquete BORRADOR no debe declarar condiciones aprobadas")
    return True


def scenarios(p):
    a = [(f, b) for f in p["frequency_levels_mhz"] for b in p["bandwidth_levels_mhz"]]
    random.Random(p["permutation_seed"]).shuffle(a)
    return a


def generate(p):
    validate_plan(p)
    first = datetime.fromisoformat(p["proposed_start_local"])
    base = scenarios(p)
    rows = []
    seq = 1
    for cycle in range(1, 8):
        start = first + timedelta(hours=(cycle-1)*96)
        # Ciclos 1..6: cada escenario ocupa cada uno de los seis turnos una vez.
        # El septimo ciclo usa una permutacion reversa PRELIMINAR.
        order = base[(cycle-1):] + base[:(cycle-1)] if cycle <= 6 else list(reversed(base))
        for slot, (f, bw) in enumerate(order, 1):
            a = start + timedelta(hours=(slot-1)*12)
            b = a + timedelta(hours=12)
            rows.append(dict(sequence=seq, cycle=cycle, slot=slot,
                             phase="TREATMENT", scenario_id=f"F{f}_B{bw}",
                             frequency_mhz=f, bandwidth_mhz=bw,
                             start_local=a.isoformat(), end_local=b.isoformat(),
                             hours=12, daypart="NIGHT" if a.hour==0 else "DAY",
                             study_eligible="TO_BE_QC_VERIFIED",
                             reference_requested="NO"))
            seq += 1
        rstart = start + timedelta(hours=72)
        f = p["reference_configuration"]["frequency_mhz"]
        bw = p["reference_configuration"]["bandwidth_mhz"]
        rows.append(dict(sequence=seq, cycle=cycle, slot="RESERVE",phase="RESERVE",
                         scenario_id=f"REFERENCE_{f}_{bw}_RESERVE",
                         frequency_mhz=f, bandwidth_mhz=bw,
                         start_local=rstart.isoformat(),
                         end_local=(rstart+timedelta(hours=24)).isoformat(),
                         hours=24, daypart="BOTH", study_eligible="NO",
                         reference_requested="YES_PENDING_RF_EXECUTION"))
        seq += 1
    validate_schedule(p, rows)
    return rows


def validate_schedule(p, rows):
    validate_plan(p)
    first = datetime.fromisoformat(p["proposed_start_local"])
    end = first + timedelta(days=28)
    if not (len(rows) == 49):
        raise ValueError('Se requieren 42 exposiciones y 7 reservas')
    if not (datetime.fromisoformat(rows[0]['start_local']) == first):
        raise ValueError('Calendario inválido')
    if not (datetime.fromisoformat(rows[-1]['end_local']) == end):
        raise ValueError('Calendario inválido')
    for prev, row in zip(rows, rows[1:]):
        if not (prev['end_local'] == row['start_local']):
            raise ValueError('Hueco o solape temporal')
    treat = [r for r in rows if r["phase"] == "TREATMENT"]
    reserve = [r for r in rows if r["phase"] == "RESERVE"]
    if not (len(treat) == 42 and len(reserve) == 7):
        raise ValueError('Calendario inválido')
    if not (all((r['hours'] == 12 for r in treat))):
        raise ValueError('Calendario inválido')
    if not (all((r['hours'] == 24 for r in reserve))):
        raise ValueError('Calendario inválido')
    counts = Counter(r["scenario_id"] for r in treat)
    if not (len(counts) == 6 and set(counts.values()) == {7}):
        raise ValueError('Calendario inválido')
    for cycle in range(1, 8):
        sample = [r for r in treat if r["cycle"] == cycle]
        if not (len(sample) == 6 and len(set((r['scenario_id'] for r in sample))) == 6):
            raise ValueError('Calendario inválido')
        if not (len([r for r in reserve if r['cycle'] == cycle]) == 1):
            raise ValueError('Calendario inválido')
    for sid in counts:
        sample = [r for r in treat[:36] if r["scenario_id"] == sid]
        if not ({r['slot'] for r in sample} == set(range(1, 7))):
            raise ValueError('Orden no balanceado en primeros seis ciclos')
        if not (sum((r['daypart'] == 'DAY' for r in sample)) == 3):
            raise ValueError('Calendario inválido')
        if not (sum((r['daypart'] == 'NIGHT' for r in sample)) == 3):
            raise ValueError('Calendario inválido')
    return True


def simulate(rows, failure_sequence=None):
    """Simula estados sin acceso a dispositivos ni cambios reales."""
    states=[]
    count_success = Counter()
    for row in rows:
        if row["phase"] == "RESERVE":
            states.append((row["sequence"],"REFERENCE_REQUEST_PLANNED_NOT_EXECUTED"))
        elif failure_sequence == row["sequence"]:
            states.append((row["sequence"],"SIMULATED_FAILURE_NEEDS_OPERATOR"))
        else:
            states.append((row["sequence"],"SIMULATED_ONLY"))
            count_success[row["scenario_id"]]+=1
    return states, count_success


def report(p, rows):
    s, counts=simulate(rows)
    t=[r for r in rows if r["phase"]=="TREATMENT"]
    report={
        "campaign_id":p["campaign_id"], "status":"DRAFT_NOT_AUTHORIZED",
        "mode":"PURE_OFFLINE_NO_RF", "original_campaign_untouched":True,
        "expected_start_local":rows[0]["start_local"],
        "expected_end_local":rows[-1]["end_local"],
        "cycles":7, "total_calendar_hours":672,
        "treatment_slots":len(t), "treatment_hours":sum(x["hours"] for x in t),
        "reserve_slots":7, "reserve_hours":168,
        "counts_per_scenario":dict(sorted(counts.items())),
        "first_six_cycles_day_night_balanced":True,
        "seventh_cycle_extra_daypart_imbalance_note":"La séptima observación por escenario añade un turno día o noche; controlar en el análisis.",
        "study_eligibility_assessed":False,
        "expert_approval":False,"operator_authorization":False,
        "rf_actuation_available":False,
        "notes":[
            "Horario provisional; congelar antes de la ejecución y documentar aceptación metodológica.",
            "Las reservas de 24 h proponen referencia 7000/20; todavía NO existe módulo RF de aplicación de referencia.",
            "No ejecutar esta fase durante la campaña original; cualquier paso a producción requiere aprobación independiente.",
            "Mantener separados los datos de ambas fases y controlar el régimen de throughput TCP."
        ]
    }
    return report


def build():
    p=read_plan()
    rows=generate(p)
    OUT.mkdir(exist_ok=True)
    path=OUT / "calendario_28d_BORRADOR.csv"
    with path.open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=COLUMNS)
        wr.writeheader();wr.writerows(rows)
    m=report(p,rows)
    m["calendar_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT/"informe_simulacion_offline.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":m["status"],"inicio":m["expected_start_local"],"fin":m["expected_end_local"],"escenarios":m["counts_per_scenario"],"simulation":"PASS_OFFLINE","rf_changes":0},indent=2,ensure_ascii=False))


def validate_file():
    p=read_plan()
    file=OUT / "calendario_28d_BORRADOR.csv"
    with file.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    for row in rows:
        for k in ("sequence","cycle","hours","frequency_mhz","bandwidth_mhz"):
            row[k]=int(row[k])
        if row["slot"] != "RESERVE": row["slot"]=int(row["slot"])
    validate_schedule(p,rows)
    if rows != generate(p):
        raise ValueError("CSV no coincide exactamente con el plan reproducible")
    print("VALIDACION OFFLINE OK: calendario sin solapes, 42 tratamientos, 7 reservas y balance temporal")


def main():
    parser=argparse.ArgumentParser(description="Solo planificacion y simulacion offline; no existe comando de activacion RF")
    parser.add_argument("action",choices=["build","validate"])
    a=parser.parse_args()
    if a.action=="build":build()
    else:validate_file()

if __name__ == "__main__":
    main()
