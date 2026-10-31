"""One explicit SM scan-list repair under durable audit and the campaign lock."""
import sys,json,pathlib,copy,time,fcntl,hashlib,os
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'prospective_28d/field_v1'))
from backend import Backend,rf
from controller import matches,event,atomic,verify_manifest
HERE=pathlib.Path(__file__).resolve().parent

def main():
 plan=json.loads((ROOT/'prospective_28d/field_v1/plan.json').read_text())
 verify_manifest(json.loads((ROOT/'prospective_28d/field_v1/freeze.json').read_text()))
 folder=ROOT/'prospective_runtime'
 if not (folder/'HALT.json').exists():raise RuntimeError('Requires halted campaign')
 if (HERE/'SM_SCAN_INTENT.json').exists():raise RuntimeError('Existing repair intent: reconcile, do not replay')
 b=Backend(plan);sm=None
 with (folder/'link.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   b.precheck()
   before=b.readback()
   if not matches(before,{'frequency_mhz':7000,'bandwidth_mhz':20}):raise RuntimeError('Reference mismatch')
   from campaign_orchestrator import CambiumAPI
   cfg=copy.deepcopy(b.config);cfg['network']['ap_ip']=rf.SM_IP;cfg['api']['scheme']='http'
   sm=CambiumAPI(cfg)
   auth=sm.request(f"{cfg['api'].get('scheme','http')}://{rf.SM_IP}/cgi-bin/luci",{'username':'admin','password':pathlib.Path(rf.SM_PASSFILE).read_text().strip()})
   sm.stok=str(auth.get('stok',''))
   if len(sm.stok)!=32:raise RuntimeError('SM authentication failed')
   if str(sm.post('test_connect',{}).get('test'))!='1':raise RuntimeError('SM session check failed')
   props=sm.read()
   keys=['wirelessInterfaceScanFrequencyBandwidth','wirelessInterfaceScanFrequencyListTwenty','wirelessInterfaceScanFrequencyListForty','wirelessInterfaceHTMode','wirelessDeviceCountryCode']
   old={k:props.get(k) for k in keys}
   atomic(HERE/'SM_SCAN_BEFORE.json',old)
   desired={'wirelessInterfaceScanFrequencyBandwidth':'3','wirelessInterfaceScanFrequencyListTwenty':'6475 6655 7000','wirelessInterfaceScanFrequencyListForty':'6475 6655 7000'}
   atomic(HERE/'SM_SCAN_INTENT.json',{'before':old,'desired':desired,'reference':before,'authorization':'Carlos: resolvamos, 31/10/2026'})
   event(HERE,'SM_SCAN_REPAIR_INTENT',desired=desired)
   sm.post('set_param',{'changed_elements':json.dumps({'device_props':desired,'template_props':{'config_id':sm.config_id}},separators=(',',':')),'trial':'1','debug':'true'})
   started=time.monotonic();event(HERE,'SM_SCAN_TRIAL_ACK')
   b.wait_target({'frequency_mhz':7000,'bandwidth_mhz':20},120)
   current=sm.read()
   if any(str(current.get(k))!=v for k,v in desired.items()):raise RuntimeError('SM scan lists do not match')
   if time.monotonic()-started>210:raise RuntimeError('SM confirmation margin exhausted')
   sm.finish(True);event(HERE,'SM_SCAN_CONFIRM_ACK')
   b.wait_target({'frequency_mhz':7000,'bandwidth_mhz':20},90)
   current=sm.read()
   if any(str(current.get(k))!=v for k,v in desired.items()):raise RuntimeError('SM scan configuration not retained')
   if any(str(current.get(k))!=str(old[k]) for k in ['wirelessInterfaceHTMode','wirelessDeviceCountryCode']):raise RuntimeError('Unrelated SM controls changed')
   atomic(HERE/'SM_SCAN_VERIFIED.json',{'desired':desired,'readback':b.readback()})
   event(HERE,'SM_SCAN_REPAIR_VERIFIED')
  finally:
   if sm:sm.logout()
   b.close()
if __name__=='__main__':main()
