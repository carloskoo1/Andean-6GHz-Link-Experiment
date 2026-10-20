"""Adaptador candidato para el Orchestrator existente. Solo laboratorio.

Ejercita switch() real (dry=False) con API y sondeos ficticios. No construye
CambiumAPI, no autentica y no contiene una ruta habilitada a equipos reales.
"""
from __future__ import annotations
import copy
import fcntl
from contextlib import contextmanager
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from campaign_orchestrator import Orchestrator, CampaignError, bw_code, validate_config
from prospective_28d.v2 import prospective_plan as plan

class AdapterError(RuntimeError):
    pass

@contextmanager
def lock(path):
    with open(path, 'a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise AdapterError('Otro adaptador posee el bloqueo') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)

class LabAPI:
    """Contrato read/trial/finish del orquestador, sin transporte."""
    def __init__(self, fault=None):
        self.props = {'centerFrequency':'7000','wirelessInterfaceHTMode':'1',
                      'centerFrequency2':'0'}
        self.previous = None
        self.calls = []
        self.fault = fault
    def read(self):
        self.calls.append('read')
        if self.fault == 'read':
            raise CampaignError('SIMULATED_READ_FAILURE')
        result = dict(self.props)
        if self.fault == 'wrong_readback' and self.previous is not None:
            result['centerFrequency'] = '9999'
        return result
    def trial(self, target):
        self.calls.append(('trial',target['frequency_mhz'],target['bandwidth_mhz']))
        self.previous = dict(self.props)
        self.props.update(centerFrequency=str(target['frequency_mhz']),
                          wirelessInterfaceHTMode=bw_code(target['bandwidth_mhz']))
        if self.fault == 'trial_ack_lost':
            raise CampaignError('SIMULATED_TRIAL_ACK_LOST')
    def finish(self, apply):
        self.calls.append(('finish',apply))
        if self.fault == 'cancel' and not apply:
            raise CampaignError('SIMULATED_CANCEL_FAILURE')
        if not apply and self.previous is not None:
            self.props = self.previous
        self.previous = None
        if self.fault == 'confirm_ack_lost' and apply:
            raise CampaignError('SIMULATED_CONFIRM_ACK_LOST')

class LabOrchestrator(Orchestrator):
    """Mantiene switch/verify/event originales; sustituye red y esperas."""
    def __init__(self, config, path, api, *, fail_stable_call=None, reachable=True):
        super().__init__(config,path,api,dry=False)
        self.fail_stable_call = fail_stable_call
        self.stable_calls = 0
        self.reachable = reachable
    def probes(self):
        return self.reachable
    def stable(self, target, deadline):
        self.stable_calls += 1
        return self.reachable and self.stable_calls != self.fail_stable_call

class ProspectiveAdapter:
    def __init__(self, prospective_plan, orchestrator, *, settle_seconds=300,
                 lateness_seconds=60, live=False):
        if live:
            raise AdapterError('LIVE_DISABLED: falta validación de campo y habilitación')
        if type(orchestrator) is not LabOrchestrator or type(orchestrator.api) is not LabAPI:
            raise AdapterError('Solo se admite el laboratorio sin transporte')
        plan.validate_plan(prospective_plan)
        errors = validate_config(orchestrator.c, True)
        if errors:
            raise AdapterError('Configuración del orquestador inválida: '+'; '.join(errors))
        for value in (settle_seconds,lateness_seconds):
            if type(value) is not int or value < 0:
                raise AdapterError('Tiempos inválidos')
        if settle_seconds >= prospective_plan['slot_hours']*3600:
            raise AdapterError('Estabilización excede el tratamiento')
        self.plan = copy.deepcopy(prospective_plan)
        self.rows = plan.generate(self.plan)
        self.orch = orchestrator
        self.settle = settle_seconds
        self.lateness = lateness_seconds
        # Fija también tiempos y configuración: no permite continuar con controles distintos.
        self.digest = self.contract_digest()

    def contract_digest(self):
        source = Path(__file__).resolve().parents[2]/'campaign_orchestrator.py'
        frozen = {'plan':self.plan,'orchestrator':self.orch.c,
                  'settle_seconds':self.settle,'lateness_seconds':self.lateness,
                  'orchestrator_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        return hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()

    def transition(self, row, instant):
        if self.contract_digest() != self.digest or self.rows != plan.generate(self.plan):
            raise AdapterError("Plan, código o configuración cambiaron después de construir el adaptador")
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise AdapterError('Instante sin zona horaria')
        if row not in self.rows:
            raise AdapterError('Fila ajena al calendario congelado')
        start = datetime.fromisoformat(row['start_local'])
        end = datetime.fromisoformat(row['end_local'])
        if not start <= instant < end:
            raise AdapterError('Fuera de la ventana; no se aplica RF')
        out = self.orch.out
        with lock(out/'prospective.lock'):
            with sqlite3.connect(out/'prospective.sqlite') as db:
                db.execute('PRAGMA synchronous=FULL')
                db.execute('CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY CHECK(id=1), digest TEXT)')
                db.execute('CREATE TABLE IF NOT EXISTS transitions (seq INTEGER PRIMARY KEY, status TEXT, detail TEXT)')
                found = db.execute('SELECT digest FROM meta WHERE id=1').fetchone()
                if found and found[0] != self.digest:
                    raise AdapterError('Configuración modificada: conciliación requerida')
                db.execute('INSERT OR IGNORE INTO meta VALUES (1,?)',(self.digest,)); db.commit()
                if (out/'SAFE_ABORT.json').exists():
                    raise AdapterError('SAFE_ABORT del orquestador activo')
                if db.execute("SELECT 1 FROM transitions WHERE status IN ('INTENT','HALTED')").fetchone():
                    raise AdapterError('Incidencia pendiente: no reintentar automáticamente')
                seq = row['sequence']
                previous = db.execute('SELECT status FROM transitions WHERE seq=?',(seq,)).fetchone()
                if previous:
                    # No afirma RF actual, solo evita repetir la transacción registrada.
                    return {'status':'ALREADY_RECORDED','sequence':seq,'current_rf_verified':False}
                last = db.execute('SELECT COALESCE(MAX(seq),0) FROM transitions').fetchone()[0]
                late = (instant-start).total_seconds() > self.lateness
                if late or seq != last+1:
                    db.execute('INSERT INTO transitions VALUES (?,?,?)',
                               (seq,'HALTED',json.dumps({'reason':'MISSED_OR_LATE','at':instant.isoformat()})))
                    db.commit()
                    raise AdapterError('Transición perdida/tardía: bloqueada sin catch-up')
                target = {'scenario_id':f"F{row['frequency_mhz']}_B{row['bandwidth_mhz']}",
                          'frequency_mhz':row['frequency_mhz'],'bandwidth_mhz':row['bandwidth_mhz'],
                          'phase':'PROSPECTIVE_RESERVE' if row['phase']=='RESERVE' else 'PROSPECTIVE_TREATMENT',
                          'sequence':seq,'cycle':row['cycle'],'days':0.5 if row['phase']=='TREATMENT' else 1}
                db.execute('INSERT INTO transitions VALUES (?,?,?)',
                           (seq,'INTENT',json.dumps({'target':target,'requested_at':instant.isoformat()})))
                db.commit()
                try:
                    self.orch.switch(target)
                    # switch no devuelve éxito estructurado: exigir estado persistido y readback.
                    state = json.loads(self.orch.state.read_text())
                    if state.get('active_scenario') != target:
                        raise AdapterError('Estado confirmado no coincide con la solicitud')
                    self.orch.verify(target)
                    if not self.orch.probes():
                        raise AdapterError('Conectividad final fallida')
                    result = {'status':'LAB_VERIFIED','sequence':seq,'phase':row['phase'],
                              'requested_at':instant.isoformat(),
                              'lab_eligible_after':(instant+timedelta(seconds=self.settle)).isoformat(),
                              'ap_rf_readback':True,'sm_rf_readback':False,
                              'ap_sm_rpi_connectivity':'SIMULATED','real_rf_changes':0,
                              'study_eligible':False,'execution_contract_sha256':self.digest}
                    db.execute('UPDATE transitions SET status=?,detail=? WHERE seq=?',
                               ('VERIFIED',json.dumps(result),seq)); db.commit()
                    return result
                except Exception as exc:
                    # No duplicar rollback: pertenece al orquestador original.
                    # Solo registrar clase para evitar propagar respuestas que contengan secretos.
                    db.execute('UPDATE transitions SET status=?,detail=? WHERE seq=?',
                               ('HALTED',json.dumps({'error_type':type(exc).__name__,
                               'review_orchestrator_logs':True,'automatic_retry':False}),seq)); db.commit()
                    raise AdapterError('Transición detenida; revisar evidencia del orquestador') from exc
