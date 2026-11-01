"""One authorized pilot executed by the actual installed systemd unit."""
import pathlib,sys,json,fcntl,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=ROOT/'prospective_28d/recovery_20261101/service_pilot'
from controller import atomic,event,matches,verify_manifest
import controller
from backend import Backend

def main():
 release=pathlib.Path(__file__).resolve().parent
 verify_manifest(json.loads((release/'freeze.json').read_text()))
 runtime=ROOT/'prospective_runtime'
 with (runtime/'link.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  if (HERE/'PASSED.json').exists():print('COMMISSIONED_WAITING_HANDOVER');return
  if (HERE/'FAILED.json').exists() or (HERE/'PENDING.json').exists():raise RuntimeError('Commissioning interrupted or failed; no automatic replay')
  if not (runtime/'HALT.json').exists():raise RuntimeError('Requires reconciled halted experimental driver')
  auth=json.loads((runtime/'COMMISSIONING_AUTH.json').read_text())
  if auth.get('authorization')!='Carlos: resolvamos ya mediante DC, 01/11/2026':raise RuntimeError('Commissioning authorization missing')
  plan=json.loads((release/'plan.json').read_text());plan['campaign_id']='LUISITA_SERVICE_PILOT_20261101_LIVE'
  b=Backend(plan);controller.RUNTIME=HERE
  try:
   b.precheck();before=b.readback()
   if not (HERE/'STARTED.json').exists() and not matches(before,{'frequency_mhz':7000,'bandwidth_mhz':20}):raise RuntimeError('Initial reference mismatch')
   if not (HERE/'STARTED.json').exists():atomic(HERE/'STARTED.json',{'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'campaign_id':plan['campaign_id'],'context':'actual installed systemd unit; excluded from experiment'})
   result=json.loads((HERE/'PROGRESS.json').read_text()) if (HERE/'PROGRESS.json').exists() else []
   targets=[(6655,40),(7000,40),(6655,20),(6475,40),(6475,20),(7000,20)]
   for i in range(len(result),min(len(result)+1,len(targets))):
    f,bw=targets[i]
    row={'segment_id':'SERVICE_PILOT_'+str(i+1),'frequency_mhz':f,'bandwidth_mhz':bw}
    b.precheck();atomic(HERE/'PENDING.json',row);event(HERE,'TRIAL_INTENT',row=row)
    b.trial(row);event(HERE,'TRIAL_ACK',row=row)
    b.wait_target(row,180);b.confirm();event(HERE,'CONFIRM_ACK',row=row);b.wait_target(row,120)
    if not matches(b.readback(),row):raise RuntimeError('Pilot RF verification mismatch')
    if i in (0,5):b.measure(row)
    result.append({'target':row,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'readback':b.readback()})
    b.close();b.api=None
    atomic(HERE/'PROGRESS.json',result);(HERE/'PENDING.json').unlink()
   if len(result)<6:print('PILOT_STEP_COMPLETE',len(result));return
   atomic(HERE/'PASSED.json',{'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':result,'returned_reference':True,'systemd_context':True,'tcp_pairs':2,'excluded_from_factorial':True})
   event(HERE,'SERVICE_PILOT_PASSED')
  except Exception as e:
   atomic(HERE/'FAILED.json',{'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':str(e)})
   event(HERE,'SERVICE_PILOT_FAILED',error=str(e));raise
  finally:b.close()
if __name__=='__main__':main()
