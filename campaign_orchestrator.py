#!/usr/bin/env python3
"""Orquestador seguro para una campaña experimental de radioenlace andino en 6 GHz."""
from __future__ import annotations
import argparse, csv, itertools, json, os, random, subprocess, sys, time
import ssl
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

class CampaignError(RuntimeError): pass
def load_config(p: Path): return json.loads(p.read_text(encoding="utf-8"))
def now(): return datetime.now(timezone.utc).isoformat()
def parse_iso(v, name):
    if not v: raise CampaignError(f"Falta {name}.")
    d=datetime.fromisoformat(v)
    if d.tzinfo is None: raise CampaignError(f"{name} debe incluir zona horaria.")
    return d
def bw_code(mhz):
    try: return {20:"1",40:"2"}[int(mhz)]
    except KeyError as e: raise CampaignError(f"Ancho no validado: {mhz}") from e

def validate_config(c, complete=False):
    e=[]; x=c.get("experiment",{}); f=x.get("frequency_levels_mhz",[]); b=x.get("bandwidth_levels_mhz",[])
    if len(f)!=3 or set(f)!={6475,6655,7000}: e.append("Frecuencias requeridas: 6475, 6655 y 7000 MHz.")
    if len(b)!=2 or set(b)!={20,40}: e.append("Anchos requeridos: 20 y 40 MHz.")
    if complete and any(v is None for v in [*f,*b]): e.append("Hay niveles null.")
    if x.get("days_per_treatment")!=7 or x.get("block_lengths_days")!=[3,2,2]: e.append("Diseño temporal requerido: siete días en bloques 3+2+2.")
    q=c.get("baseline",{})
    if q.get("days")!=14: e.append("La línea base debe durar 14 días.")
    try: parse_iso(q.get("start_local"),"baseline.start_local"); parse_iso(q.get("analysis_start_local"),"baseline.analysis_start_local")
    except CampaignError as z: e.append(str(z))
    s=c.get("safety",{}); trial=int(s.get("trial_timeout_seconds",0)); assoc=int(s.get("association_timeout_seconds",0)); margin=int(s.get("confirmation_margin_seconds",0))
    if trial!=300: e.append("La prueba temporal validada dura 300 s.")
    if assoc<120 or assoc+margin>=trial: e.append("Ventana de reasociación/margen inválida.")
    if int(s.get("minimum_successful_probes",0))<5: e.append("Se requieren al menos cinco sondeos consecutivos.")
    if c.get("api",{}).get("auth_mode")!="stok_env": e.append("auth_mode debe ser stok_env.")
    return e

def scenarios(c):
    x=c["experiment"]; a=[{"scenario_id":f"F{f}_B{b}","frequency_mhz":f,"bandwidth_mhz":b,"days":7,"phase":"EXPERIMENT"} for f,b in itertools.product(x["frequency_levels_mhz"],x["bandwidth_levels_mhz"])]
    random.Random(x["order_seed"]).shuffle(a); return a
def baseline(c):
    b=c["baseline"]; return {"scenario_id":f"BASE_{b['frequency_mhz']}_{b['bandwidth_mhz']}","frequency_mhz":b["frequency_mhz"],"bandwidth_mhz":b["bandwidth_mhz"],"days":b["days"],"phase":"BASELINE","block":0}
def scenario(c,sid):
    for s in [baseline(c),*scenarios(c)]:
        if s["scenario_id"]==sid:return s
    raise CampaignError(f"Escenario desconocido: {sid}")
def schedule(c):
    b = c["baseline"]
    start = parse_iso(
        b["analysis_start_local"],
        "analysis_start",
    )
    baseline_end = start + timedelta(days=b["days"])
    rows = [{
        **baseline(c),
        "sequence": 0,
        "start_local": start.isoformat(),
        "end_local": baseline_end.isoformat(),
        "deployment_start_local": b["start_local"],
    }]
    configured_start = c["experiment"].get("start_local")
    cursor = (
        parse_iso(configured_start, "experiment.start_local")
        if configured_start
        else baseline_end
    )
    if cursor < baseline_end:
        raise CampaignError(
            "El experimento no puede comenzar antes de finalizar la línea base."
        )
    seq = 1
    for block,days in enumerate(c["experiment"]["block_lengths_days"],1):
        a=[dict(v) for v in scenarios(c)]; random.Random(c["experiment"]["order_seed"]+block).shuffle(a)
        for s in a:
            end=cursor+timedelta(days=days); rows.append({**s,"sequence":seq,"block":block,"days":days,"start_local":cursor.isoformat(),"end_local":end.isoformat()}); cursor=end; seq+=1
    return rows

class CambiumAPI:
    def __init__(self,c,stok): self.c,self.stok,self.config_id=c,stok,None
    def post(self,endpoint,form):
        a=self.c["api"]; ip=self.c["network"]["ap_ip"]; token=urllib.parse.quote(self.stok,safe=""); url=f"{a.get('scheme','http')}://{ip}/cgi-bin/luci/;stok={token}/admin/{endpoint}"
        req=urllib.request.Request(url,data=urllib.parse.urlencode(form).encode(),method="POST",headers={"Content-Type":"application/x-www-form-urlencoded","Accept":"application/json"})
        tls_context = None
        if url.startswith("https://") and not a.get(
            "tls_verify",
            True,
        ):
            tls_context = ssl.create_default_context()
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req,timeout=a["request_timeout_seconds"],context=tls_context) as r: p=json.loads(r.read().decode())
        except Exception as z: raise CampaignError(f"Fallo API {endpoint}: {z}") from z
        if str(p.get("success")).lower() not in {"1","true"} or p.get("err"): raise CampaignError(f"API rechazó {endpoint}: {p}")
        return p
    def read(self):
        p=self.post("get_param",{"act":"config_regular","debug":"true"}); d=p.get("device_props"); t=p.get("template_props",{})
        if not isinstance(d,dict): raise CampaignError("get_param no devolvió device_props.")
        if t.get("config_id") is None: raise CampaignError("get_param no devolvió template_props.config_id.")
        self.config_id=str(t["config_id"])
        return d
    def trial(self,s):
        if self.config_id is None: raise CampaignError("Debe leerse config_id antes de aplicar el cambio.")
        change={"device_props":{"centerFrequency":str(s["frequency_mhz"]),"wirelessInterfaceHTMode":bw_code(s["bandwidth_mhz"])},"template_props":{"config_id":self.config_id}}
        self.post("set_param",{"changed_elements":json.dumps(change,separators=(",",":")),"trial":"1","debug":"true"})
    def finish(self,apply): self.post("set_trial_param",{"apply":"true" if apply else "false","debug":"true"})

def ping(ip): return subprocess.run(["ping","-n","-c","1","-W","1",ip],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
class Orchestrator:
    def __init__(self,c,path,api,dry=False):
        self.c,self.api,self.dry=c,api,dry; out=Path(c["outputs"]["directory"]); self.out=out if out.is_absolute() else path.parent/out; self.out.mkdir(parents=True,exist_ok=True); self.log=self.out/c["outputs"]["event_log"]; self.state=self.out/c["outputs"]["state"]; self.csv=self.out/c["outputs"]["schedule"]
    def event(self,name,s,result,detail=""):
        row={"timestamp_utc":now(),"event":name,"result":result,"detail":detail,**s}; print(json.dumps(row,ensure_ascii=False),flush=True)
        if not self.dry:
            with self.log.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    def probes(self):
        n=self.c["network"]; return all(ping(n[k]) for k in ("ap_ip","sm_ip","rpi_ip"))
    def stable(self,s,deadline):
        need=self.c["safety"]["minimum_successful_probes"]; good=0
        while time.monotonic()<deadline:
            ok=self.probes(); good=good+1 if ok else 0; self.event("CONNECTIVITY_PROBE",s,"OK" if ok else "WAITING",f"consecutive={good}/{need}")
            if good>=need:return True
            time.sleep(self.c["safety"]["probe_interval_seconds"])
        return False
    def verify(self,s):
        d=self.api.read()
        if str(d.get("centerFrequency"))!=str(s["frequency_mhz"]) or str(d.get("wirelessInterfaceHTMode"))!=bw_code(s["bandwidth_mhz"]): raise CampaignError(f"Configuración inesperada: {d.get('centerFrequency')}/{d.get('wirelessInterfaceHTMode')}")
    def switch(self,s):
        self.event("SWITCH_START",s,"STARTED")

        if self.dry:
            self.event("SWITCH_COMMITTED",s,"DRY_RUN")
            return

        if not self.probes():
            raise CampaignError(
                "Preflight falló: AP, SM y RPi deben responder."
            )

        before = self.api.read()
        previous = {
            "scenario_id": "ROLLBACK_PREVIOUS",
            "frequency_mhz": int(before["centerFrequency"]),
            "bandwidth_mhz": {
                "1": 20,
                "2": 40,
            }.get(str(before["wirelessInterfaceHTMode"])),
            "days": 0,
            "phase": "ROLLBACK",
        }

        if previous["bandwidth_mhz"] is None:
            raise CampaignError(
                "No se pudo interpretar el ancho de canal anterior: "
                f"{before.get('wirelessInterfaceHTMode')}"
            )

        confirmed = False
        trial_started = False
        t = time.monotonic()

        try:
            self.api.trial(s)
            trial_started = True
            self.event(
                "TRIAL_APPLIED",
                s,
                "OK",
                "rollback_automatico=300s",
            )

            deadline = (
                t
                + self.c["safety"]["association_timeout_seconds"]
            )
            if not self.stable(s, deadline):
                raise CampaignError("No se recuperó el enlace.")

            self.verify(s)

            remain = (
                self.c["safety"]["trial_timeout_seconds"]
                - (time.monotonic() - t)
            )
            if remain < self.c["safety"]["confirmation_margin_seconds"]:
                raise CampaignError(
                    f"Margen insuficiente: {remain:.1f}s"
                )

            self.api.finish(True)
            confirmed = True
            self.event(
                "TRIAL_CONFIRMED",
                s,
                "OK",
                f"remaining={remain:.1f}s",
            )

            deadline = (
                time.monotonic()
                + self.c["safety"]["association_timeout_seconds"]
            )
            if not self.stable(s, deadline):
                raise CampaignError(
                    "Inestable después de confirmar."
                )

            self.verify(s)

        except Exception as original_error:
            self.event(
                "SWITCH_FAILED",
                s,
                "ERROR",
                str(original_error),
            )

            try:
                if confirmed:
                    self.event(
                        "ROLLBACK_START",
                        previous,
                        "STARTED",
                        "reaplicacion_explicita",
                    )

                    self.api.read()
                    self.api.trial(previous)

                    deadline = (
                        time.monotonic()
                        + self.c["safety"]["association_timeout_seconds"]
                    )
                    if not self.stable(previous, deadline):
                        raise CampaignError(
                            "No se recuperó el enlace durante rollback."
                        )

                    self.verify(previous)
                    self.api.finish(True)

                elif trial_started:
                    self.event(
                        "ROLLBACK_START",
                        previous,
                        "STARTED",
                        "cancelacion_del_trial",
                    )
                    self.api.finish(False)

                    deadline = (
                        time.monotonic()
                        + self.c["safety"]["association_timeout_seconds"]
                    )
                    if not self.stable(previous, deadline):
                        raise CampaignError(
                            "No se recuperó el enlace tras cancelar trial."
                        )

                    self.verify(previous)

                self.event(
                    "ROLLBACK_COMMITTED",
                    previous,
                    "OK",
                    f"causa={original_error}",
                )

            except Exception as rollback_error:
                self.event(
                    "ROLLBACK_FAILED",
                    previous,
                    "AUTO_ROLLBACK",
                    str(rollback_error),
                )

            raise

        self.event("SWITCH_COMMITTED",s,"OK")

        tmp = self.state.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(
                {
                    "updated_utc": now(),
                    "previous_scenario": previous,
                    "active_scenario": s,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        tmp.replace(self.state)

    def plan(self):
        rows=schedule(self.c); fields=["sequence","scenario_id","phase","block","frequency_mhz","bandwidth_mhz","start_local","end_local","days","deployment_start_local"]
        with self.csv.open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore",lineterminator="\n");w.writeheader();w.writerows(rows)
        print(self.csv)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="action",required=True)
    for a in ("validate","plan"):q=sub.add_parser(a);q.add_argument("--config",required=True,type=Path)
    q=sub.add_parser("switch");q.add_argument("--config",required=True,type=Path);q.add_argument("--scenario",required=True);q.add_argument("--dry-run",action="store_true"); a=p.parse_args()
    try:
        c=load_config(a.config); errs=validate_config(c,a.action!="validate")
        if errs:raise CampaignError(" | ".join(errs))
        if a.action=="validate":print("Configuración válida: AP-only, trial/confirm y factorial 3x2.");return 0
        if a.action=="plan": Orchestrator(c,a.config,CambiumAPI(c,"DRY"),True).plan(); return 0
        dry=getattr(a,"dry_run",False); token="DRY" if dry else os.environ.get(c["api"]["stok_env"],"").strip()
        if not token:raise CampaignError(f"Falta {c['api']['stok_env']}.")
        o=Orchestrator(c,a.config,CambiumAPI(c,token),dry)
        o.switch(scenario(c,a.scenario))
        return 0
    except Exception as e:print(f"ERROR: {e}",file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
