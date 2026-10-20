"""Exclusión y recuperación candidatas, exclusivamente laboratorio, sin red."""
from __future__ import annotations
import fcntl
import hashlib
from datetime import datetime
from prospective_28d.v2 import prospective_plan as planner
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from campaign_orchestrator import bw_code
from campaign_executor import run_once

LINK = 'CU01-SJ01-6G'
class Blocked(RuntimeError):pass
class Busy(Blocked):pass
class Uncertain(Blocked):pass

class Guard:
    """Un único directorio por enlace, en disco local. Nunca borrar el lock."""
    def __init__(self, directory, *, live=False):
        if live:raise Blocked('LIVE_DISABLED')
        self.directory=Path(directory).resolve();self.directory.mkdir(parents=True,exist_ok=True)
    @contextmanager
    def lease(self, role, *, recovery=False):
        if role not in ('original','prospective'):raise Blocked('Rol inválido')
        with (self.directory/'link.lock').open('a') as handle:
            try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as exc:raise Busy('Enlace ocupado por otro proceso') from exc
            try:
                with sqlite3.connect(self.directory/'guard.sqlite') as db:
                    db.execute('PRAGMA synchronous=FULL')
                    db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)')
                    db.execute('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, event TEXT NOT NULL, data TEXT NOT NULL)')
                    db.execute('INSERT OR IGNORE INTO state VALUES (1,?)',(json.dumps({'link':LINK,'owner':'original','pending':None,'review_required':False}),));db.commit()
                    state=json.loads(db.execute('SELECT data FROM state WHERE id=1').fetchone()[0])
                    if state['link']!=LINK:raise Blocked('Identidad de enlace incompatible')
                    if state['owner']!=role:raise Blocked('La otra fase conserva la titularidad')
                    if not recovery and (state['pending'] or state['review_required']):
                        raise Blocked('Incidencia pendiente: nuevas operaciones bloqueadas')
                    yield Session(db,state)
            finally:fcntl.flock(handle,fcntl.LOCK_UN)
    def handover_lab(self, evidence):
        required={'mode','original_closed','original_timer_disabled','stability_48h','expert_conditions'}
        if set(evidence)!=required or evidence['mode']!='LAB_ONLY' or any(evidence[k] is not True for k in required-{'mode'}):
            raise Blocked('Evidencia de relevo de laboratorio incompleta')
        with self.lease('original') as s:
            s.data['owner']='prospective';s.save('LAB_HANDOVER',evidence)
    def acknowledge_lab(self, role, incident_id):
        # Reconoce únicamente una recuperación ya comprobada; no borra el historial.
        with self.lease(role,recovery=True) as s:
            if s.data['pending'] or not s.data['review_required'] or s.data.get('last_incident')!=incident_id:
                raise Blocked('No hay recuperación conciliada para reconocer')
            s.data['review_required']=False;s.save('LAB_REVIEW_ACK',{'incident_id':incident_id})

class Session:
    def __init__(self,db,data):self.db,self.data=db,data
    def save(self,event,detail):
        self.db.execute('UPDATE state SET data=? WHERE id=1',(json.dumps(self.data),))
        self.db.execute('INSERT INTO audit(event,data) VALUES (?,?)',(event,json.dumps(detail)))
        self.db.commit()

class Clock:
    def __init__(self,now=0):self.now=now
    def advance(self,seconds):
        if seconds<0:raise ValueError('El reloj no retrocede')
        self.now+=seconds

class Radio:
    """AP ficticio; timeout de trial ficticio. No existe transporte HTTP."""
    def __init__(self,clock):
        self.clock=clock;self.current=(7000,20);self.pending=None;self.calls=[]
        self.fault=None;self.reachable=True;self.read_override=None;self.trial_delay_seconds=0
    def expire(self):
        if self.pending and self.clock.now>=self.pending['deadline']:
            self.current=self.pending['before'];self.pending=None
    def read(self):
        self.calls.append('read')
        if not self.reachable:raise OSError('LAB_UNREACHABLE')
        self.expire();return self.read_override or self.current
    def probes(self):return self.reachable
    def trial(self,target):
        self.expire();self.calls.append(('trial',target));fault=self.fault
        if fault=='trial_before':self.fault=None;raise TimeoutError('LAB_TRIAL_NOT_ACCEPTED')
        self.pending={'before':self.current,'deadline':self.clock.now+300};self.current=target
        self.clock.advance(self.trial_delay_seconds)
        if fault=='trial_after':self.fault=None;raise TimeoutError('LAB_TRIAL_ACCEPTED_ACK_LOST')
    def finish(self,apply):
        self.expire();self.calls.append(('finish',apply));fault=self.fault
        if fault=='confirm_before':self.fault=None;raise TimeoutError('LAB_CONFIRM_NOT_ACCEPTED')
        if self.pending:
            if not apply:self.current=self.pending['before']
            self.pending=None
        if fault=='confirm_after':self.fault=None;raise TimeoutError('LAB_CONFIRM_ACCEPTED_ACK_LOST')

class Candidate:
    """Trial/confirm conservador. Todo fallo conserva una intención durable."""
    def __init__(self,guard,radio,clock,role='prospective',*,live=False):
        if live or type(radio) is not Radio or type(clock) is not Clock or type(guard) is not Guard:
            raise Blocked('Solo backend de laboratorio; LIVE_DISABLED')
        if role not in ('original','prospective'):raise Blocked('Rol inválido')
        self.guard,self.radio,self.clock,self.role=guard,radio,clock,role
    def observe(self):
        values=[self.radio.read() for _ in range(3)]
        if len(set(values))!=1 or not self.radio.probes():raise Uncertain('Readback o conectividad inestable')
        return values[0]
    def switch(self,target,incident_id):
        if type(target) is not tuple or len(target)!=2 or target[0] not in (6475,6655,7000) or target[1] not in (20,40):
            raise Blocked('Tratamiento fuera del factorial')
        if not isinstance(incident_id,str) or not incident_id:raise Blocked('Falta identificador')
        with self.guard.lease(self.role) as s:
            return self._switch(s,target,incident_id)

    def _switch(self,s,target,incident_id):
        completed=s.data.get('completed',{})
        if incident_id in completed:
            if tuple(completed[incident_id])!=target:raise Blocked('Identificador reutilizado con otro tratamiento')
            return 'ALREADY_RECORDED'
        before=self.observe()
        if before[0] not in (6475,6655,7000) or before[1] not in (20,40):
            raise Blocked('Estado previo fuera del conjunto validado')
        if before==target:
            s.data.setdefault('completed',{})[incident_id]=target
            s.save('LAB_NO_CHANGE',{'id':incident_id,'target':target});return 'LAB_NO_CHANGE'
        pending={'id':incident_id,'before':before,'target':target,'stage':'TRIAL_INTENT',
                 'started':self.clock.now,'not_before':self.clock.now+360}
        s.data['pending']=pending;s.save('TRIAL_INTENT',pending)
        try:
            self.radio.trial(target)
            if self.observe()!=target:raise Uncertain('Trial no verificado')
            if self.clock.now-pending['started']>=240:raise Uncertain('Margen de confirmación insuficiente')
            pending['stage']='CONFIRM_INTENT';s.save('CONFIRM_INTENT',pending)
            self.radio.finish(True)
            if self.observe()!=target:raise Uncertain('Confirmación no verificada')
            s.data['pending']=None;s.data.setdefault('completed',{})[incident_id]=target
            s.save('LAB_COMMITTED',{'id':incident_id,'target':target});return 'LAB_COMMITTED'
        except Exception as exc:
            # No cancelar ni repetir una escritura cuyo resultado se desconoce.
            pending['not_before']=self.clock.now+360
            s.data['review_required']=True
            s.save('UNCERTAIN',{'id':incident_id,'error_type':type(exc).__name__})
            raise Uncertain('Esperar vencimiento y conciliar; sin reintento automático') from exc

    def recover(self,*,clock_trusted=False):
        if clock_trusted is not True:raise Blocked('Tiempo no confiable: no conciliar automáticamente')
        with self.guard.lease(self.role,recovery=True) as s:
            p=s.data['pending']
            if not p:raise Blocked('No hay transición pendiente')
            if self.clock.now<p['started']:raise Blocked('Reloj anterior al incidente')
            if self.clock.now<p['not_before']:return 'WAIT_NO_WRITES'
            try:observed=self.observe()
            except Exception:
                s.save('RECOVERY_UNREADABLE',{'id':p['id']});return 'MANUAL_REQUIRED'
            before=tuple(p['before']);target=tuple(p['target'])
            if observed==before:
                s.data['pending']=None;s.data['review_required']=True;s.data['last_incident']=p['id']
                s.save('RECOVERED_PREVIOUS',{'id':p['id'],'before':before})
                return 'RECOVERED_PREVIOUS_REVIEW_REQUIRED'
            if observed!=target:
                s.save('RECOVERY_UNKNOWN_RF',{'id':p['id']});return 'MANUAL_REQUIRED'
            if p['stage'].startswith('RESTORE_'):
                # Ya se intentó restaurar; no entrar en bucle de escrituras.
                s.save('RECOVERY_RESTORE_UNRESOLVED',{'id':p['id']});return 'MANUAL_REQUIRED'
            # Target persiste tras el vencimiento: restauración única al estado previo conocido.
            # Aun con ACK se verifica de nuevo DESPUÉS de su propio plazo de trial.
            p['stage']='RESTORE_TRIAL_INTENT';p['started']=self.clock.now;p['not_before']=self.clock.now+360
            s.save('RESTORE_TRIAL_INTENT',p)
            try:
                self.radio.trial(before)
                if self.observe()!=before:raise Uncertain('Restauración no verificada')
                if self.clock.now-p['started']>=240:raise Uncertain('Restauración sin margen')
                p['stage']='RESTORE_CONFIRM_INTENT';s.save('RESTORE_CONFIRM_INTENT',p)
                self.radio.finish(True)
                s.save('RESTORE_SENT_AWAITING_RECHECK',{'id':p['id']})
            except Exception as exc:
                p['not_before']=self.clock.now+360
                s.save('RESTORE_UNCERTAIN',{'id':p['id'],'error_type':type(exc).__name__})
            return 'RESTORE_PENDING_RECHECK'

class OriginalRunner:
    """Runner ficticio; no ejecuta comandos del ejecutor original."""
    def __init__(self):self.calls=[]
    def __call__(self,command,**kwargs):
        self.calls.append(command);return SimpleNamespace(returncode=0)

def run_original_lab(config_path,instant,guard,runner):
    if type(guard) is not Guard or type(runner) is not OriginalRunner:
        raise Blocked('Wrapper exclusivo de laboratorio')
    with guard.lease('original'):
        return run_once(Path(config_path),instant,dry_run=False,runner=runner)


class ScheduledProspective:
    """Calendario V2 + transacción V4, guardia única compartida con original."""
    def __init__(self,plan,candidate):
        planner.validate_plan(plan)
        if type(candidate) is not Candidate or candidate.role!='prospective':
            raise Blocked('Candidato prospectivo de laboratorio requerido')
        self.plan=json.loads(json.dumps(plan));self.rows=planner.generate(self.plan)
        self.candidate=candidate
        self.digest=hashlib.sha256(json.dumps(self.plan,sort_keys=True).encode()).hexdigest()
    def tick(self,instant):
        if instant.tzinfo is None or instant.utcoffset() is None:raise Blocked('Instante sin zona')
        if abs(self.candidate.clock.now-instant.timestamp())>1:raise Blocked('Relojes de calendario y transacción no coinciden')
        if self.rows!=planner.generate(self.plan) or hashlib.sha256(json.dumps(self.plan,sort_keys=True).encode()).hexdigest()!=self.digest:
            raise Blocked('Plan modificado')
        row=next((r for r in self.rows if datetime.fromisoformat(r['start_local'])<=instant<datetime.fromisoformat(r['end_local'])),None)
        if row is None:return 'OUTSIDE_SCHEDULE'
        with self.candidate.guard.lease('prospective') as s:
            frozen=s.data.get('schedule_digest')
            if frozen and frozen!=self.digest:raise Blocked('Calendario diferente del registrado')
            if s.data.get('schedule_halted'):raise Blocked('Calendario detenido: falta decisión metodológica')
            seq=row['sequence'];last=s.data.get('last_sequence',0)
            if seq==last:return 'ALREADY_RECORDED'
            if seq!=last+1 or (instant-datetime.fromisoformat(row['start_local'])).total_seconds()>60:
                s.data['schedule_halted']=True;s.save('MISSED_SLOT',{'sequence':seq})
                raise Blocked('Transición perdida o tardía; sin catch-up')
            s.data['schedule_digest']=self.digest
            # Persistencia previa: un fallo o muerte abrupta conserva schedule_halted.
            s.data['schedule_halted']=True;s.save('SCHEDULE_INTENT',{'sequence':seq})
            result=self.candidate._switch(s,(row['frequency_mhz'],row['bandwidth_mhz']),f'prospective-{seq}')
            s.data['last_sequence']=seq;s.data['schedule_halted']=False
            s.save('SCHEDULE_COMMITTED',{'sequence':seq,'phase':row['phase'],'study_eligible':False})
            return result
