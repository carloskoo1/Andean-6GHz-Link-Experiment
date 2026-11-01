"""One-time handover after real systemd pilot and complete zero-data reconciliation."""
import pathlib,sys,json,datetime,fcntl,hashlib,shutil,sqlite3,os
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from controller import load_plan,parse,atomic,event,matches,verify_manifest
from backend import Backend

def main():
 rec=ROOT/'prospective_28d/recovery_20261101';pilot=rec/'service_pilot'
 if not (pilot/'PASSED.json').exists():raise RuntimeError('Real systemd commissioning not complete')
 passed=json.loads((pilot/'PASSED.json').read_text())
 if not passed['systemd_context'] or not passed['returned_reference'] or passed['tcp_pairs']!=2:raise RuntimeError('Commissioning proof incomplete')
 if len(passed['results'])!=6:raise RuntimeError('Six configurations not verified')
 backup=json.loads((rec/'BACKUP.json').read_text())
 if backup['quick_check']!='ok':raise RuntimeError('Backup not verified')
 plan=load_plan(HERE/'plan.json');now=datetime.datetime.now(datetime.timezone.utc)
 if now>=parse(plan['windows'][0]['start_local'])-datetime.timedelta(minutes=15):raise RuntimeError('Calendar requires a future D0')
 db=sqlite3.connect('file:/home/carlos/Proyectos/EstacionMeteorologica/SQLite/CU01/weather_local.db?mode=ro',uri=True,timeout=10)
 old=db.execute("select count(*) from active_throughput_6g where campaign_id in ('LUISITA_PROSPECTIVE_28D_20261030','LUISITA_PROSPECTIVE_28D_20261031')").fetchone()[0]
 tests=db.execute("select direction,status,count(*) from active_throughput_6g where campaign_id='LUISITA_SERVICE_PILOT_20261101_LIVE' group by direction,status").fetchall()
 provenance=db.execute("select count(*) from prospective_rf_verification where campaign_id='LUISITA_SERVICE_PILOT_20261101_LIVE'").fetchone()[0]
 good=db.execute("select count(*) from active_throughput_6g where campaign_id='LUISITA_SERVICE_PILOT_20261101_LIVE' and status='OK' and route_verified=1 and duration_seconds=8 and omit_seconds=1 and parallel_streams=1").fetchone()[0];db.close()
 if provenance!=4 or old!=0 or sorted(tests)!=[('DL','OK',2),('UL','OK',2)] or good!=4:raise RuntimeError('Real TCP evidence does not satisfy commissioning criteria')
 runtime=ROOT/'prospective_runtime';b=Backend(plan)
 with (runtime/'link.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   manifest=json.loads((HERE/'freeze.json').read_text());verify_manifest(manifest)
   if not (runtime/'HALT.json').exists() or (runtime/'PENDING.json').exists():raise RuntimeError('Prior attempt state differs from audit')
   if (HERE/'DEPLOYMENT.json').exists():raise RuntimeError('Already handed over; do not replay')
   b.precheck();reference=b.readback()
   if not matches(reference,dict(frequency_mhz=7000,bandwidth_mhz=20)):raise RuntimeError('Reference not restored')
   if int(b.api.read().get('cambiumCfgTrialTimer',-1))!=0:raise RuntimeError('Active trial still present')
   b.close();b.api=None
   archive=rec/'reconciled_runtime';archive.mkdir()
   for name in ['ENABLED.json','HALT.json','PENDING.json','state.json','STATUS.json','events.jsonl','COMMISSIONING_AUTH.json']:
    p=runtime/name
    if p.exists():shutil.copy2(p,archive/name)
   manifest[str(HERE/'handover.py')]=hashlib.sha256((HERE/'handover.py').read_bytes()).hexdigest()
   atomic(HERE/'freeze.json',manifest)
   atomic(runtime/'ENABLED.json',{'enabled_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':plan['authorization'],'campaign_id':plan['campaign_id'],'active_release':'field_v3','automatic_RF_before_D0':False,'supersedes':['LUISITA_PROSPECTIVE_28D_20261030','LUISITA_PROSPECTIVE_28D_20261031'],'previous_attempts_archived':str(rec)})
   for name in ['HALT.json','PENDING.json','state.json','STATUS.json']:
    p=runtime/name
    if p.exists():p.unlink()
   (runtime/'events.jsonl').write_text('')
   event(runtime,'SESSION_RECOVERY_HANDOVER',campaign_id=plan['campaign_id'],previous_attempts_tests=old,systemd_pilot_tests=good,reference=reference,start_local=plan['windows'][0]['start_local'],end_local=plan['windows'][-1]['end_local'])
   (runtime/'COMMISSIONING_AUTH.json').unlink()
   atomic(HERE/'DEPLOYMENT.json',{'activated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaign_id':plan['campaign_id'],'start_local':plan['windows'][0]['start_local'],'end_local':plan['windows'][-1]['end_local'],'reference':reference,'old_attempts_tests':old,'systemd_pilot_TCP_OK':good,'normal_tests':32,'optimized_tests':32,'real_session_cycles':12,'backup':backup,'previous_runtime_archive':str(archive)})
  except Exception as e:
   if not (runtime/'HALT.json').exists():atomic(runtime/'HALT.json',{'reason':'Handover failed: '+str(e)})
   raise
  finally:b.close()
 print('HANDOVER_COMPLETE',plan['windows'][0]['start_local'],plan['windows'][-1]['end_local'])
if __name__=='__main__':main()
