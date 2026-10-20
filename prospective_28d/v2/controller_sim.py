"""Controlador de transiciones EXCLUSIVAMENTE SIMULADO. Sin adaptador RF."""
import fcntl
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
import prospective_plan as plan

class Halt(RuntimeError):
    pass

class SimulatedPair:
    """AP/SM ficticios; apply nunca accede a la red."""
    def __init__(self, fault=None):
        self.fault = fault
        self.calls = 0
        self.ap = self.sm = (7000, 20)
    def read(self):
        if self.fault == 'unreachable':
            raise Halt('AP/SM inaccesibles (simulado)')
        return {'ap': self.ap, 'sm': self.sm, 'linked': self.fault != 'unlinked'}
    def apply(self, target):
        self.calls += 1
        self.ap = target
        if self.fault == 'partial':
            raise Halt('Cambio parcial AP; SM no confirmado (simulado)')
        self.sm = target
    def verify(self, target):
        s = self.read()
        return s['ap'] == s['sm'] == target and s['linked']

@contextmanager
def lock(path):
    with open(path, 'a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Halt('Otro controlador posee el bloqueo') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)

def fingerprint(p):
    return hashlib.sha256(json.dumps(p, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def tick(p, rows, now, state_dir, radio, *, settle_seconds=300, max_lateness_seconds=60):
    """Un tick simulado por transición; ventana tardía cerrada, sin catch-up.

    Un proceso muerto después de INTENT exige conciliación manual. No se
    repite apply ni se presume éxito. La reserva también se verifica.
    """
    if type(radio) is not SimulatedPair:
        raise Halt('Solo se admite el simulador incluido')
    plan.validate_schedule(p, rows)
    if rows != plan.generate(p):
        raise Halt('Calendario alterado respecto del plan')
    if now.tzinfo is None or now.utcoffset() is None:
        raise Halt('Reloj sin zona horaria')
    if type(settle_seconds) is not int or settle_seconds < 0:
        raise Halt('Estabilización inválida')
    if type(max_lateness_seconds) is not int or max_lateness_seconds < 0:
        raise Halt('Tolerancia inválida')
    directory = Path(state_dir)
    directory.mkdir(parents=True, exist_ok=True)
    with lock(directory / 'controller.lock'):
        with sqlite3.connect(directory / 'events.sqlite') as db:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('CREATE TABLE IF NOT EXISTS meta (id INTEGER PRIMARY KEY CHECK(id=1), digest TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, status TEXT, detail TEXT)')
            digest = fingerprint(p)
            prior = db.execute('SELECT digest FROM meta WHERE id=1').fetchone()
            if prior and prior[0] != digest:
                raise Halt('Plan cambiado tras inicializar estado')
            db.execute('INSERT OR IGNORE INTO meta VALUES (1, ?)', (digest,))
            db.commit()
            if db.execute("SELECT 1 FROM events WHERE status IN ('INTENT','HALTED')").fetchone():
                raise Halt('Incidencia pendiente: conciliación manual requerida')
            first = datetime.fromisoformat(rows[0]['start_local'])
            last = datetime.fromisoformat(rows[-1]['end_local'])
            if now < first:
                return {'status':'WAITING'}
            if now >= last:
                return {'status':'FINISHED_NO_RF', 'final_reference_verified':False}
            row = next(r for r in rows if datetime.fromisoformat(r['start_local']) <= now < datetime.fromisoformat(r['end_local']))
            seq = row['sequence']
            event = db.execute('SELECT status,detail FROM events WHERE seq=?', (seq,)).fetchone()
            if event:
                return {'status':'ALREADY_RECORDED','recorded':json.loads(event[1])}
            # No replay de tratamientos perdidos; exige revisar cualquier salto.
            done = db.execute('SELECT COALESCE(MAX(seq),0) FROM events').fetchone()[0]
            start = datetime.fromisoformat(row['start_local'])
            if seq != done + 1 or (now-start).total_seconds() > max_lateness_seconds:
                detail = json.dumps({'reason':'transición perdida o tardía','at':now.isoformat()})
                db.execute('INSERT INTO events VALUES (?, ?, ?)', (seq,'HALTED',detail)); db.commit()
                raise Halt('Transición perdida/tardía; no se recupera automáticamente')
            target = (row['frequency_mhz'],row['bandwidth_mhz'])
            db.execute('INSERT INTO events VALUES (?, ?, ?)', (seq,'INTENT',json.dumps({'target':target,'at':now.isoformat()})))
            db.commit()  # intención durable ANTES de aplicar
            try:
                before = radio.read()
                if not before['linked'] or before['ap'] != before['sm']:
                    raise Halt('Precheck AP/SM incoherente')
                radio.apply(target)
                if not radio.verify(target):
                    raise Halt('Verificación AP/SM fallida')
                eligible = now + timedelta(seconds=settle_seconds)
                if eligible >= datetime.fromisoformat(row['end_local']):
                    raise Halt('Estabilización excede la ventana')
                result = {'status':'SIMULATED_VERIFIED','sequence':seq,'phase':row['phase'],
                          'requested_at':now.isoformat(),'before':before,'target':target,
                          'simulated_eligible_after':eligible.isoformat(),
                          'study_eligible':False,'reason':'Simulación; falta QC de datos reales'}
                db.execute('UPDATE events SET status=?, detail=? WHERE seq=?', ('VERIFIED',json.dumps(result),seq)); db.commit()
                return result
            except Exception as exc:
                db.execute('UPDATE events SET status=?, detail=? WHERE seq=?', ('HALTED',json.dumps({'error':str(exc),'automatic_rollback':False}),seq)); db.commit()
                raise Halt('Detenido; estado AP/SM requiere conciliación. Sin rollback ciego') from exc
