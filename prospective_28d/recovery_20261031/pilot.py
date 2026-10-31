"""Explicit pre-campaign six-configuration pilot, never counted as exposure data."""
import pathlib,sys,json,time,fcntl,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'prospective_28d/field_v1'))
from backend import Backend
from controller import atomic,event,matches,verify_manifest
class DiagnosticBackend(Backend):
 def wait_target(self,row,deadline_seconds):
  deadline=time.monotonic()+deadline_seconds;good=0;attempt=0
  while time.monotonic()<deadline:
   attempt+=1;seen=None;err=None
   try:
    seen=self.readback();ok=matches(seen,row)
    if ok:self.route()
   except Exception as e:ok=False;err=str(e)
   good=good+1 if ok else 0
   event(HERE,'PILOT_PROBE',segment=row['segment_id'],attempt=attempt,consecutive=good,readback=seen,error=err)
   if good>=10:return
   time.sleep(2)
  raise RuntimeError('Dual verification timeout; see PILOT_PROBE diagnostic events')
def main():
 if not (HERE/'SM_SCAN_VERIFIED.json').exists():raise RuntimeError('SM scan repair not verified')
 if (HERE/'PILOT_STARTED.json').exists():raise RuntimeError('Existing pilot: no replay')
 if not (ROOT/'prospective_runtime/HALT.json').exists():raise RuntimeError('Requires campaign HALT')
 verify_manifest(json.loads((ROOT/'prospective_28d/field_v1/freeze.json').read_text()))
 plan=json.loads((ROOT/'prospective_28d/field_v1/plan.json').read_text());plan['campaign_id']='LUISITA_RECOVERY_PILOT_20261031'
 b=DiagnosticBackend(plan)
 with (ROOT/'prospective_runtime/link.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   b.precheck()
   if not matches(b.readback(),{'frequency_mhz':7000,'bandwidth_mhz':20}):raise RuntimeError('Initial reference mismatch')
   atomic(HERE/'PILOT_STARTED.json',{'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaign_id':plan['campaign_id'],'not_factorial_data':True})
   targets=[(6655,40),(7000,40),(6655,20),(6475,40),(6475,20),(7000,20)]
   results=[]
   for i,(freq,bw) in enumerate(targets):
    row={'segment_id':'RECOVERY_PILOT_'+str(i+1),'frequency_mhz':freq,'bandwidth_mhz':bw}
    atomic(HERE/'PILOT_PENDING.json',row);event(HERE,'PILOT_TRIAL_INTENT',row=row)
    b.precheck();b.trial(row);event(HERE,'PILOT_TRIAL_ACK',row=row)
    b.wait_target(row,150);b.confirm();event(HERE,'PILOT_CONFIRM_ACK',row=row)
    b.wait_target(row,120)
    seen=b.readback()
    if not matches(seen,row):raise RuntimeError('Final pilot mismatch')
    results.append({'target':row,'readback':seen,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    atomic(HERE/'PILOT_PROGRESS.json',results);event(HERE,'PILOT_TARGET_VERIFIED',row=row)
    (HERE/'PILOT_PENDING.json').unlink()
    if i==0:
     b.measure(row);event(HERE,'PILOT_TCP_PAIR_COMPLETED',campaign_id=plan['campaign_id'])
   atomic(HERE/'PILOT_PASSED.json',{'results':results,'not_factorial_data':True,'returned_reference':True})
   event(HERE,'PILOT_PASSED')
  except Exception as e:
   atomic(HERE/'PILOT_HALT.json',{'error':str(e),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});event(HERE,'PILOT_ERROR',error=str(e));raise
  finally:b.close()
if __name__=='__main__':main()
