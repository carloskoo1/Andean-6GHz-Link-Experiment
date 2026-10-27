#!/usr/bin/env python3
"""Simulador prospectivo aislado. NO contiene actuadores RF ni red."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path

def parse_rows(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=49 or len({r["segment_id"] for r in rows})!=49:
        raise ValueError("Calendario invalido: 49 filas e IDs unicos requeridos")
    for row in rows:
        if row["status"]!="PLANNED_NOT_AUTHORIZED":
            raise ValueError("Solo calendario no autorizado en simulador")
    return rows

class FakeRadio:
    def __init__(self):
        self.current="BASE_7000_20"
        self.history=[]
        self.fail_next=False
    def apply(self,target):
        self.history.append(target)
        if self.fail_next:
            self.fail_next=False
            raise RuntimeError("Fallo simulado de confirmacion")
        self.current=target
        return True

class Simulation:
    def __init__(self,rows,radio=None):
        self.rows=rows
        self.radio=radio or FakeRadio()
        self.confirmed=set()
        self.events=[]
        self.halted=False
    def step(self,instant):
        if self.halted:
            self.events.append(("BLOCKED","SAFE_ABORT"))
            return "BLOCKED"
        active=next((r for r in self.rows
          if dt.datetime.fromisoformat(r["start_local"])<=instant<
             dt.datetime.fromisoformat(r["end_local"])),None)
        if active is None:
            return "NO_WINDOW"
        sid=active["segment_id"]
        if sid in self.confirmed:
            return "NO_OP_ALREADY_APPLIED"
        if active["phase"]=="RESERVE":
            self.confirmed.add(sid)
            self.events.append(("RESERVE",sid))
            return "RESERVE_NO_RF_CHANGE"
        old=self.radio.current
        try:
            self.radio.apply(active["scenario_id"])
        except RuntimeError:
            self.radio.current=old
            self.halted=True
            self.events.append(("SAFE_ABORT",sid))
            return "SAFE_ABORT"
        self.confirmed.add(sid)
        self.events.append(("SIMULATED_COMMIT",sid))
        return "SIMULATED_COMMIT"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--schedule",required=True)
    parser.add_argument("--at",required=True)
    a=parser.parse_args()
    sim=Simulation(parse_rows(a.schedule))
    at=dt.datetime.fromisoformat(a.at)
    result=sim.step(at)
    print(json.dumps({"mode":"FAKE_RADIO_ONLY","result":result,"events":sim.events,
                      "rf_execution_authorized":False},ensure_ascii=False))
if __name__=="__main__":
    main()
