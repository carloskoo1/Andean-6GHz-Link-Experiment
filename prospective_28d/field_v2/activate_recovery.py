"""Reconcile the failed zero-data attempt and activate a verified future calendar."""
import pathlib,sys,json,hashlib,shutil,fcntl,datetime,subprocess,os
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from controller import atomic,event,load_plan,parse,verify_manifest,matches
from backend import Backend
PYTHON='/home/carlos/Proyectos/EstacionMeteorologica/venv/bin/python'

def main():
 recovery=ROOT/'prospective_28d/recovery_20261031'
 if not (recovery/'PILOT_PASSED.json').exists():raise RuntimeError('Six-configuration field pilot is not complete')
 pilot=json.loads((recovery/'PILOT_PASSED.json').read_text())
 if len(pilot['results'])!=6 or not pilot['returned_reference']:raise RuntimeError('Pilot evidence incomplete')
 plan=load_plan(HERE/'plan.json')
 now=datetime.datetime.now(datetime.timezone.utc)
 if now>=parse(plan['windows'][0]['start_local'])-datetime.timedelta(minutes=15):raise RuntimeError('D0 too close or expired; do not retrodate')
 runtime=ROOT/'prospective_runtime';archive=recovery/'failed_runtime_20261030'
 if archive.exists():raise RuntimeError('Recovery already attempted; reconcile manually')
 oldmanifest=json.loads((ROOT/'prospective_28d/field_v1/freeze.json').read_text())
 verify_manifest(oldmanifest)
 import sqlite3
 db=sqlite3.connect('file:/home/carlos/Proyectos/EstacionMeteorologica/SQLite/CU01/weather_local.db?mode=ro',uri=True,timeout=10)
 oldcount=db.execute("select count(*) from active_throughput_6g where campaign_id='LUISITA_PROSPECTIVE_28D_20261030'").fetchone()[0]
 pairs=db.execute("select direction,status,count(*) from active_throughput_6g where campaign_id='LUISITA_RECOVERY_PILOT_20261031' group by direction,status").fetchall();db.close()
 if oldcount!=0 or sorted(pairs)!=[('DL','OK',1),('UL','OK',1)]:raise RuntimeError('Unexpected old or pilot TCP records')
 backup=pathlib.Path('/home/carlos/Backups/Luisita_prospective_recovery/20261031_111743/SHA256.json')
 if not backup.exists():raise RuntimeError('Consistent recovery backup missing')
 b=Backend(plan)
 with (runtime/'link.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   if not (runtime/'HALT.json').exists() or not (runtime/'PENDING.json').exists():raise RuntimeError('Failed attempt is not in expected state')
   b.precheck();before=b.readback()
   if not matches(before,{'frequency_mhz':7000,'bandwidth_mhz':20}):raise RuntimeError('Reference not restored')
   if int(b.api.read().get('cambiumCfgTrialTimer',-1))!=0:raise RuntimeError('AP trial still pending')
   archive.mkdir()
   for name in ['ENABLED.json','HALT.json','PENDING.json','events.jsonl','state.json','STATUS.json']:
    f=runtime/name
    if f.exists():shutil.copy2(f,archive/name)
   oldrelease=recovery/'original_field_v1'
   shutil.copytree(ROOT/'prospective_28d/field_v1',oldrelease,ignore=shutil.ignore_patterns('__pycache__'))
   shim='''#!/usr/bin/env python3\n"""Compatibility entry point for the existing systemd unit; active release field_v2."""\nimport sys,runpy\nfrom pathlib import Path\nrelease=Path(__file__).resolve().parent.parent/'field_v2'\nsys.path.insert(0,str(release))\nrunpy.run_path(str(release/'controller.py'),run_name='__main__')\n'''
   manifest=dict(oldmanifest)
   manifest[str(ROOT/'prospective_28d/field_v1/controller.py')]=hashlib.sha256(shim.encode()).hexdigest()
   for name in ['controller.py','backend.py','plan.json','calendar.csv','test_controller.py','test_backend.py','activate_recovery.py']:
    f=HERE/name;manifest[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
   atomic(HERE/'freeze.json',manifest)
   f=ROOT/'prospective_28d/field_v1/controller.py';temp=f.with_suffix('.recovery_tmp');temp.write_text(shim);os.replace(temp,f)
   verify_manifest(manifest)
   # Preserve the previous enable marker continuously, so old RF/TCP drivers stay blocked.
   atomic(runtime/'ENABLED.json',{'enabled_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':'Carlos: resolvamos, 31/10/2026','campaign_id':plan['campaign_id'],'active_release':'field_v2','automatic_RF_before_D0':False,'supersedes':'LUISITA_PROSPECTIVE_28D_20261030','failed_attempt_archived':str(archive)})
   for name in ['HALT.json','PENDING.json','state.json','STATUS.json']:
    f=runtime/name
    if f.exists():f.unlink()
   (runtime/'events.jsonl').write_text('')
   event(runtime,'RECOVERY_HANDOVER',campaign_id=plan['campaign_id'],failed_attempt_archived=str(archive),old_prospective_tests=oldcount,reference=before,start_local=plan['windows'][0]['start_local'],end_local=plan['windows'][-1]['end_local'])
   atomic(HERE/'DEPLOYMENT.json',{'activated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaign_id':plan['campaign_id'],'start_local':plan['windows'][0]['start_local'],'end_local':plan['windows'][-1]['end_local'],'reference_readback':before,'previous_attempt_tests':oldcount,'pilot_tcp':pairs,'backup_manifest':str(backup),'existing_systemd_entry_point':str(ROOT/'prospective_28d/field_v1/controller.py'),'new_release':str(HERE),'halt_reconciled_only_after_evidence':True})
  except Exception as e:
   if not (runtime/'HALT.json').exists():
    atomic(runtime/'HALT.json',{'reason':'Recovery activation failed: '+str(e),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
   raise
  finally:b.close()
 done=subprocess.run([PYTHON,str(ROOT/'prospective_28d/field_v1/controller.py'),'tick'],capture_output=True,text=True,check=True)
 print('FIRST_TICK',done.stdout)
 if 'WAITING_START' not in done.stdout:raise RuntimeError('Post-activation status not waiting for D0')
 print('ACTIVATED',plan['windows'][0]['start_local'],plan['windows'][-1]['end_local'])
if __name__=='__main__':main()
