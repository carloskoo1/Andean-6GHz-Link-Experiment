#!/usr/bin/env python3
"""Validador documental NO OPERATIVO: no habilita ni modifica transiciones RF."""
import argparse
import csv
import json
from pathlib import Path

REQUIRED = ("C01","C02","RF01","RF02","RF03","SI01","SI02",
            "SI03","SI04","ME01","ME02","ME03","CU01")
def check_manifest(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_id = {r["condition_id"]: r for r in rows}
    missing = [x for x in REQUIRED if x not in by_id]
    incomplete = [x for x in REQUIRED if x in by_id and (
        by_id[x].get("status") != "CUMPLIDA"
        or not by_id[x].get("evidence_location")
        or not by_id[x].get("verified_at")
        or not by_id[x].get("verified_by"))]
    return {"documentary_complete":not (missing or incomplete),
            "missing":missing,"incomplete":incomplete,
            "rf_execution_authorized":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    args=p.parse_args()
    result=check_manifest(args.manifest)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    print("SIN CAPACIDAD DE ACTIVAR RF — autorización técnica externa imprescindible")
if __name__=="__main__":
    main()
