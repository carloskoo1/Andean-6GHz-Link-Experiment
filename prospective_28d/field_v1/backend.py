"""Real AP-only trial transport and explicit single-attempt TCP acquisition."""
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[2]
ATMOS=Path('/home/carlos/Proyectos/EstacionMeteorologica')
DB=ATMOS/'SQLite/CU01/weather_local.db'
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ATMOS))
from campaign_orchestrator import CambiumAPI, load_config
from weather_station.telemetry import radio_config_6g_collector as rf
from weather_station.telemetry import active_throughput_6g as tcp


class Backend:
    def __init__(self,plan):
        self.plan=plan
        self.config=load_config(ROOT/'campaign_plan.template.json')
        self.api=None
        self.trial_at=None

    def precheck(self):
        ntp=subprocess.check_output(['timedatectl','show','-p','NTPSynchronized','--value'],text=True).strip()
        if ntp!='yes':raise RuntimeError('Controller NTP not synchronized')
        for unit in ['andean-campaign.timer','andean-throughput.timer','atmoslink-throughput-6g.timer',
                     'andean-campaign.service','andean-throughput.service','atmoslink-throughput-6g.service']:
            status=subprocess.run(['systemctl','is-active',unit],capture_output=True,text=True).stdout.strip()
            if status not in ('inactive','failed'):raise RuntimeError('Concurrent/unknown service: '+unit+' '+status)
        self.route()
        if self.api is None:
            self.api=CambiumAPI(self.config)
            self.api.authenticate(self.config['api']['credentials_file'])
        props=self.api.read()
        if str(props.get('wirelessInterfaceTDDRatio'))!='2' or str(props.get('wirelessInterfaceTDDFrameSize'))!='5000':
            raise RuntimeError('TDD changed; refusing prospective operation')

    def route(self):
        rows=json.loads(subprocess.check_output(['ip','-j','route','get','192.168.1.4','from','192.168.1.50'],text=True))
        if not rows or rows[0].get('dev')!='enp1s0' or rows[0].get('from')!='192.168.1.50':
            raise RuntimeError('TCP route mismatch')
        if subprocess.run(['ping','-I','enp1s0','-c','1','-W','2','192.168.1.4'],stdout=subprocess.DEVNULL).returncode:
            raise RuntimeError('Remote endpoint unreachable')

    def readback(self):
        user,pw,_=rf.load_runtime_config()
        result={}
        for role,host,login,secret,name,power in [
            ('ap',rf.AP_IP,user,pw,'Cunacales6',10),
            ('sm',rf.SM_IP,'admin',rf.SM_PASSFILE,'SanJose6',3)]:
            data=rf.parse_key_value(rf.run_ssh(login,secret,host,'show dashboard'))
            if data.get('cambiumEffectiveDeviceName')!=name or data.get('cambiumEffectiveDeviceIPAddress')!=host:
                raise RuntimeError('Radio identity mismatch: '+role)
            if data.get('cambiumCurrentSWInfo')!='5.4':raise RuntimeError('Firmware changed: '+role)
            if rf.numeric(data.get('cambiumSTAConductedTXPower'))!=power or rf.numeric(data.get('cambiumEffectiveAntennaGain'))!=26:
                raise RuntimeError('Power/gain changed: '+role)
            result[role+'_f']=rf.numeric(data.get('cambiumSTAConnectedRFFrequency'))
            result[role+'_b']={1:20,2:40}.get(rf.integer(data.get('cambiumSTAConnectedRFBandwidth')))
            if result[role+'_f'] is None or result[role+'_b'] is None:raise RuntimeError('RF unavailable: '+role)
        return result

    def trial(self,row):
        if self.api is None:raise RuntimeError('Precheck session missing')
        props=self.api.read()
        if str(props.get('wirelessInterfaceTDDRatio'))!='2' or str(props.get('wirelessInterfaceTDDFrameSize'))!='5000':
            raise RuntimeError('TDD changed; refusing RF write')
        self.trial_at=time.monotonic()
        self.api.trial(row)

    def confirm(self):
        if self.trial_at is None or time.monotonic()-self.trial_at>210:
            raise RuntimeError('Insufficient trial confirmation margin; no confirm sent')
        self.api.finish(True)

    def wait_target(self,row,deadline_seconds):
        from controller import matches
        deadline=time.monotonic()+deadline_seconds
        good=0
        while time.monotonic()<deadline:
            try:
                ok=matches(self.readback(),row)
                if ok:self.route()
            except Exception:
                ok=False
            good=good+1 if ok else 0
            if good>=10:return
            time.sleep(2)
        raise RuntimeError('Dual target/connectivity not stable before deadline')

    def measure(self,row):
        self.precheck()
        os.chdir(ATMOS)
        user,pw,_=rf.load_runtime_config()
        # Collect a new RF record. No alteration of previous observations.
        rf.collect_once(user,pw,DB)
        lockfile=ATMOS/'runtime/active_throughput_6g.lock'
        with lockfile.open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            connection=sqlite3.connect(DB,timeout=60)
            try:
                tcp.init_database(connection)
                ping=tcp.ping_metrics()
                testid=str(uuid.uuid4())
                for idx,direction in enumerate(['DL','UL']):
                    if idx:time.sleep(5)
                    su,sl=tcp.now_pair();before=tcp.interface_counters(tcp.CLIENT_INTERFACE)
                    command=['iperf3','--client',tcp.SERVER_IP,'--bind',tcp.CLIENT_IP,'--port','5201',
                             '--time','8','--omit','1','--parallel','1','--json']
                    if direction=='UL':command.append('--reverse')
                    payload=None;error=''
                    try:
                        done=tcp.run(command,timeout=39)
                        payload=json.loads(done.stdout) if done.stdout.strip() else None
                        if done.returncode or not isinstance(payload,dict) or payload.get('error'):
                            error=str((payload or {}).get('error') or done.stderr or 'iperf did not return a valid result')[-4000:]
                    except Exception as exc:
                        error=str(exc)[-4000:]
                    after=tcp.interface_counters(tcp.CLIENT_INTERFACE);eu,el=tcp.now_pair()
                    if not isinstance(payload,dict):payload=None
                    record=tcp.build_record(testid,direction,su,sl,eu,el,payload,error,before,after,ping,
                        tcp.nearest_rf(connection,su),tcp.nearest_weather(connection,'CU01',su),tcp.nearest_weather(connection,'SJ01',su))
                    record['campaign_id']=self.plan['campaign_id']
                    tcp.insert_record(connection,record)
                    print(json.dumps({k:record.get(k) for k in ['test_id','campaign_id','direction','status','timestamp_start_local','measured_throughput_mbps','error']}),flush=True)
                tcp.export_csv(connection,ATMOS/'Data/exports/active_throughput_6g.csv')
            finally:
                connection.close()

    def close(self):
        if self.api:
            self.api.logout()
