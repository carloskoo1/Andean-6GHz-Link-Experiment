"""Ejecutor integrado candidato, sin red ni mediciones reales.

CambiumAPI original procesa el contrato HTTP a través de un opener ficticio.
Candidate V4 es la única máquina de transacción/recuperación.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs
from campaign_orchestrator import CambiumAPI,bw_code
from prospective_28d.v2 import prospective_plan as planner
from prospective_28d.v4.safety import Guard,Clock,Radio,Candidate,Blocked

ROOT=Path(__file__).resolve().parents[2]
TCP=Path(__file__).with_name('tcp_protocol.pending.json')

def stamp(value):return datetime.fromtimestamp(value,timezone.utc).isoformat()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def instant(value):
    if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise Blocked('Tiempo requiere zona horaria')
    return value.timestamp()

def validate_tcp(config):
    if config.get('status')!='PENDING_EXPERT_REVIEW' or config.get('active_profile_id') is not None or config.get('measurement_execution_enabled') is not False:
        raise Blocked('Este candidato requiere TCP pendiente y deshabilitado')
    if config.get('protocol')!='TCP' or config.get('directions')!=['DL','UL'] or config.get('execution_mode')!='sequential':
        raise Blocked('Protocolo TCP inválido')
    if config.get('route_verified') is not False or config.get('clock_verified') is not False:
        raise Blocked('No declarar verificaciones de campo desde laboratorio')
    profiles=config.get('profiles_for_comparison',{})
    if set(profiles)!={'tcp_8s_omit1','tcp_15s_omit2'}:raise Blocked('Perfiles comparativos incompletos')
    if config.get('interval_minutes') is not None or config.get('minute_offset') is not None:
        raise Blocked('Cadencia pendiente: no congelarla implícitamente')
    expected={'tcp_8s_omit1':(8,1,1),'tcp_15s_omit2':(15,2,1)}
    for profile_id,profile in profiles.items():
        if any(type(profile.get(k)) is not int for k in ('duration_seconds','omit_seconds','parallel_streams')):
            raise Blocked('Parámetros TCP no enteros')
        if not 0<=profile['omit_seconds']<profile['duration_seconds'] or profile['parallel_streams']!=1:
            raise Blocked('Parámetros TCP inválidos')
        if tuple(profile[k] for k in ('duration_seconds','omit_seconds','parallel_streams'))!=expected[profile_id]:
            raise Blocked('Identificador y parámetros TCP no coinciden')

class Response:
    def __init__(self,payload):self.payload=payload
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self):return json.dumps(self.payload).encode()

class SimulatedLuci:
    """Servidor en memoria del contrato get_param/set_param/set_trial_param."""
    def __init__(self,clock):
        self.clock=clock;self.radio=Radio(clock);self.events=[];self.config_id=1
        self.read_delay=1;self.trial_delay=5;self.confirm_delay=2
        self.secondary_frequency='0';self.unexpected_payload=False
    def open(self,request,timeout=None):
        endpoint=request.full_url.rsplit('/',1)[-1]
        form={k:v[0] for k,v in parse_qs(request.data.decode()).items()}
        event={'endpoint':endpoint,'requested_at':stamp(self.clock.now),'result':'INTENT'}
        self.events.append(event)
        try:
            if endpoint=='get_param':
                self.clock.advance(self.read_delay);f,b=self.radio.read()
                payload={'success':True,'device_props':{'centerFrequency':str(f),
                         'wirelessInterfaceHTMode':bw_code(b),'centerFrequency2':self.secondary_frequency},
                         'template_props':{'config_id':str(self.config_id)}}
                if self.unexpected_payload:payload.pop('device_props')
            elif endpoint=='set_param':
                change=json.loads(form['changed_elements']);props=change['device_props']
                if set(props)!={'centerFrequency','wirelessInterfaceHTMode'} or form['trial']!='1':
                    raise Blocked('Payload RF inesperado')
                if change['template_props']['config_id']!=str(self.config_id):raise Blocked('config_id obsoleto')
                self.clock.advance(self.trial_delay)
                self.radio.trial((int(props['centerFrequency']),{'1':20,'2':40}[props['wirelessInterfaceHTMode']]))
                self.config_id+=1;payload={'success':True}
            elif endpoint=='set_trial_param':
                self.clock.advance(self.confirm_delay);self.radio.finish(form['apply']=='true')
                payload={'success':True}
            else:raise Blocked('Endpoint no habilitado en laboratorio')
            event.update(result='ACK',completed_at=stamp(self.clock.now));return Response(payload)
        except Exception as exc:
            event.update(result='UNCERTAIN',completed_at=stamp(self.clock.now),error_type=type(exc).__name__)
            raise

class APIBridge:
    """Traduce el contrato de CambiumAPI al contrato de la recuperación V4."""
    def __init__(self,server):
        if type(server) is not SimulatedLuci:raise Blocked('Solo servidor en memoria')
        self.server=server
        cfg={'api':{'scheme':'https','tls_verify':True,'request_timeout_seconds':15},
             'network':{'ap_ip':'lab-ap.invalid'}}
        self.api=CambiumAPI(cfg,stok='LAB_SESSION_NOT_A_CREDENTIAL',opener=server)
    def read(self):
        props=self.api.read()
        try:return (int(props['centerFrequency']),{'1':20,'2':40}[str(props['wirelessInterfaceHTMode'])])
        except (KeyError,ValueError,TypeError) as exc:raise Blocked('Readback RF inválido') from exc
    def trial(self,target):
        self.api.trial({'frequency_mhz':target[0],'bandwidth_mhz':target[1]})
    def finish(self,apply):self.api.finish(apply)
    def probes(self):return self.server.radio.probes()

class IntegratedCandidate(Candidate):
    def __init__(self,guard,server,clock):
        # Inicializar la base con objetos estrictamente ficticios; sustituir solo
        # por el puente al MISMO radio ficticio. Nunca admitir un opener externo.
        if type(server) is not SimulatedLuci or server.clock is not clock:
            raise Blocked('Backend o reloj no corresponde al laboratorio')
        super().__init__(guard,server.radio,clock)
        self.radio=APIBridge(server)

class UnifiedExecutor:
    def __init__(self,plan,guard,server,clock,*,settle_seconds=300,tcp=None,live=False):
        if live:raise Blocked('LIVE_DISABLED')
        planner.validate_plan(plan)
        if type(clock) is not Clock or type(guard) is not Guard or type(server) is not SimulatedLuci:
            raise Blocked('Backend no simulado rechazado')
        if type(settle_seconds) is not int or not 0<=settle_seconds<43200:
            raise Blocked('Estabilización inválida')
        self.plan=copy.deepcopy(plan);self.rows=planner.generate(self.plan)
        self.tcp=copy.deepcopy(tcp if tcp is not None else json.loads(TCP.read_text()))
        validate_tcp(self.tcp)
        self.guard,self.server,self.clock=guard,server,clock
        self.settle=settle_seconds;self.candidate=IntegratedCandidate(guard,server,clock)
        self.frozen=self.contract()
    def contract(self):
        source_files=['campaign_orchestrator.py','prospective_28d/v4/safety.py',
                      'prospective_28d/v5/executor.py']
        return digest({'plan':self.plan,'tcp':self.tcp,'settle':self.settle,
                       'source':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_files}})
    def bind(self,s):
        if self.contract()!=self.frozen or self.rows!=planner.generate(self.plan):raise Blocked('Contrato modificado')
        if s.data.get('v5_contract',self.frozen)!=self.frozen:raise Blocked('Contrato distinto del registrado')
        s.data['v5_contract']=self.frozen
    def tick(self,at):
        ts=instant(at)
        if not math.isfinite(self.clock.now) or abs(self.clock.now-ts)>1:raise Blocked('Relojes no coinciden')
        row=next((r for r in self.rows if instant(datetime.fromisoformat(r['start_local']))<=ts<instant(datetime.fromisoformat(r['end_local']))),None)
        if row is None:return {'status':'OUTSIDE_SCHEDULE','study_eligible':False}
        with self.guard.lease('prospective') as s:
            self.bind(s)
            if s.data.get('schedule_halted'):raise Blocked('Calendario detenido')
            seq=row['sequence'];last=s.data.get('last_sequence',0)
            if seq==last:return {'status':'ALREADY_RECORDED','current_rf_verified':False,'study_eligible':False}
            if seq!=last+1 or ts-instant(datetime.fromisoformat(row['start_local']))>60:
                s.data['schedule_halted']=True;s.data['v5_halt_at']=ts;s.save('V5_MISSED_SLOT',{'sequence':seq,'at':stamp(ts)})
                raise Blocked('Ventana perdida/tardía; sin catch-up')
            window={'sequence':seq,'cycle':row['cycle'],'phase':row['phase'],
                    'scenario_id':row['scenario_id'],'target':[row['frequency_mhz'],row['bandwidth_mhz']],
                    'scheduled_start':row['start_local'],'scheduled_end':row['end_local'],
                    'requested_at':stamp(ts),'trial_requested_at':None,'confirm_requested_at':None,
                    'confirm_ack_at':None,'verified_at':None,'analysis_start':None,
                    'status':'INTENT','study_eligible':False,'mode':'LAB_ONLY'}
            s.data['schedule_halted']=True;s.data['v5_halt_at']=ts
            s.data.setdefault('v5_windows',{})[str(seq)]=window
            s.save('V5_WINDOW_INTENT',window)
            event_offset=len(self.server.events)
            try:
                outcome=self.candidate._switch(s,tuple(window['target']),f'v5-{seq}')
                verified=self.clock.now
                self.capture_api_times(window,event_offset)
                window.update(verified_at=stamp(verified),analysis_start=stamp(verified+self.settle),status=outcome)
                if verified+self.settle>=instant(datetime.fromisoformat(row['end_local'])):
                    raise Blocked('No queda ventana después de estabilizar')
                s.data['last_sequence']=seq;s.data['schedule_halted']=False;s.data.pop('v5_halt_at',None)
                s.save('V5_WINDOW_VERIFIED',window)
                return copy.deepcopy(window)
            except Exception as exc:
                self.capture_api_times(window,event_offset)
                window.update(status='INCIDENT',analysis_start=None,error_type=type(exc).__name__,
                              incident_at=stamp(self.clock.now))
                s.data['review_required']=True;s.data['schedule_halted']=True
                s.save('V5_WINDOW_INCIDENT',window)
                raise
    def capture_api_times(self,window,offset):
        for event in self.server.events[offset:]:
            if event['endpoint']=='set_param':window['trial_requested_at']=event['requested_at']
            elif event['endpoint']=='set_trial_param':
                window['confirm_requested_at']=event['requested_at']
                if event['result']=='ACK':window['confirm_ack_at']=event['completed_at']
    def recover(self,*,clock_trusted=False):
        with self.guard.lease('prospective',recovery=True) as s:
            self.bind(s)
        result=self.candidate.recover(clock_trusted=clock_trusted)
        with self.guard.lease('prospective',recovery=True) as s:
            self.bind(s)
            s.data.setdefault('v5_recovery',[]).append({'at':stamp(self.clock.now),'result':result})
            # Recuperación técnica no vuelve elegible la ventana ni reanuda el calendario.
            s.save('V5_RECOVERY_RESULT',s.data['v5_recovery'][-1])
        return result
    def classify_interval(self,start,end,*,qc_passed=False,observed_target=None):
        a,b=instant(start),instant(end)
        if b<=a:raise Blocked('Intervalo de medición inválido')
        with self.guard.lease('prospective',recovery=True) as s:
            self.bind(s)
            windows=list(s.data.get('v5_windows',{}).values())
            result={'temporal_eligible':False,'study_eligible':False,'mode':'LAB_ONLY'}
            for w in windows:
                lo=instant(datetime.fromisoformat(w['scheduled_start']));hi=instant(datetime.fromisoformat(w['scheduled_end']))
                if lo<=a<hi:
                    result['sequence']=w['sequence']
                    if w['phase']!='TREATMENT':return {**result,'reason':'RESERVE'}
                    if w['status'] not in ('LAB_COMMITTED','LAB_NO_CHANGE') or not w['analysis_start']:
                        return {**result,'reason':'UNVERIFIED_OR_INCIDENT'}
                    eligible=instant(datetime.fromisoformat(w['analysis_start']))
                    if a<eligible:return {**result,'reason':'TRANSITION_OR_SETTLING'}
                    if b>hi:return {**result,'reason':'CROSSES_WINDOW_END'}
                    if s.data.get('pending') or s.data.get('review_required') or s.data.get('schedule_halted'):
                        cutoff=s.data.get('v5_halt_at',(s.data.get('pending') or {}).get('started'))
                        if cutoff is None or b>cutoff:
                            return {**result,'reason':'CAMPAIGN_INCIDENT'}
                    if qc_passed is not True:return {**result,'reason':'QC_PENDING'}
                    if observed_target is None or list(observed_target)!=w['target']:
                        return {**result,'reason':'RF_NOT_CONFIRMED'}
                    return {**result,'temporal_eligible':True,'reason':'LAB_ONLY_PROTOCOL_PENDING',
                            'tcp_execution_enabled':False}
            return {**result,'reason':'NO_VERIFIED_WINDOW'}
    def request_tcp_measurement(self,*args,**kwargs):
        # Ni los flags de un JSON ni los ensayos aprueban el protocolo de campo.
        raise Blocked('TCP_DISABLED: protocolo pendiente; sin iperf ni subprocess')
