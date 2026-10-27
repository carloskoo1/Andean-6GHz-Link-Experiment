import sqlite3,csv,json,statistics as st,collections as co,datetime,hashlib
from pathlib import Path
DB='/home/carlos/Proyectos/EstacionMeteorologica/SQLite/CU01/weather_local.db'
ROOT=Path('/home/carlos/Proyectos/Andean-6GHz-Link-Experiment')
schedule=[r for r in csv.DictReader(open(ROOT/'campaign_runtime/campaign_schedule.csv')) if r['phase']=='EXPERIMENT']
events=[]
for line in open(ROOT/'campaign_runtime/campaign_events.jsonl'):
 try:events.append(json.loads(line))
 except ValueError:pass
c=sqlite3.connect('file:'+DB+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('BEGIN')
rf={r['id']:dict(r) for r in c.execute("select * from radio_link_config_telemetry where timestamp_local>='2026-09-15' and timestamp_local<'2026-10-27'")}
alltcp=[dict(r) for r in c.execute("select * from active_throughput_6g where timestamp_start_local>='2026-09-15' and timestamp_start_local<'2026-10-27'")]
out={'cutoff':'2026-10-27','rule_version':'retrospective_record_QC_v1','temporal_exposure':'first matching SWITCH_COMMITTED, dual RF required','segment_threshold':'none imposed post hoc; coverage reported; low-coverage sensitivity separate','segments':[],'source_projection':[]}
def median(rs,k):
 v=[r[k] for r in rs if isinstance(r.get(k),(int,float))];return st.median(v) if v else None
for seg in schedule:
 n=int(seg['sequence']);a,b=seg['start_local'],seg['end_local'];f=float(seg['frequency_mhz']);bw=float(seg['bandwidth_mhz'])
 ee=[]
 for e in events:
  t=e.get('timestamp_utc')
  if not t:continue
  local=datetime.datetime.fromisoformat(t).astimezone(datetime.timezone(datetime.timedelta(hours=-5))).isoformat()
  if a<=local<b and e.get('event')=='SWITCH_COMMITTED' and e.get('frequency_mhz')==f and e.get('bandwidth_mhz')==bw:ee.append(local)
 start=min(ee) if ee else None
 ar=[r for r in rf.values() if a<=r['timestamp_local']<b]
 strict=[r for r in ar if r['collection_status']=='LINK_OPERATIONAL_DUAL' and r['operating_frequency_mhz']==r['sm_operating_frequency_mhz']==f and r['channel_bandwidth_mhz']==r['sm_channel_bandwidth_mhz']==bw]
 strict_ids={r['id'] for r in strict};selected=[];reason=co.Counter()
 attempts=[r for r in alltcp if a<=r['timestamp_start_local']<b and r['direction']=='DL']
 for r in attempts:
  why=None
  if r['campaign_id']!='CAMPAIGN_6G_20260831':why='other_campaign'
  elif r['status']!='OK':why='status_not_OK'
  elif r['protocol']!='TCP' or r['duration_seconds']!=8 or r['omit_seconds']!=1 or r['parallel_streams']!=1:why='other_protocol'
  elif r['route_verified']!=1:why='route_unverified'
  elif not start or r['timestamp_start_local']<start:why='before_confirmed_treatment'
  elif not r['timestamp_end_local'] or r['timestamp_end_local']>=b:why='outside_end_window'
  elif r['operating_frequency_mhz']!=f or r['channel_bandwidth_mhz']!=bw:why='tcp_configuration_mismatch'
  elif r['rf_telemetry_id'] not in strict_ids:why='rf_not_dual_matching'
  elif r['rf_time_delta_seconds'] is None or abs(r['rf_time_delta_seconds'])>300:why='rf_pair_exceeds_300s'
  elif not isinstance(r['measured_throughput_mbps'],(int,float)) or r['measured_throughput_mbps']<0:why='invalid_throughput'
  if why:reason[why]+=1
  else:selected.append(r)
 vals=sorted(r['measured_throughput_mbps'] for r in selected)
 item={'segment':n,'block':int(seg['block']),'f':int(f),'b':int(bw),'start':a,'end':b,'confirmed':start,'rf_total':len(ar),'rf_strict':len(strict),'dl_attempts_all_profiles':len(attempts),'dl_n':len(selected),'dl_median':median(selected,'measured_throughput_mbps'),'dl_mean':st.mean(vals) if vals else None,'hours_with_dl':len({r['timestamp_start_local'][:13] for r in selected}),'nominal_hours':int(seg['days'])*24,'exclusions':dict(reason)}
 for k in ['dl_rssi_dbm','ul_rssi_dbm','dl_snr_db','ul_snr_db','reported_dl_link_rate_mbps','reported_ul_link_rate_mbps','ap_tx_power_dbm','sm_tx_power_dbm']:
  item[k]=median([r for r in strict if 'rssi' not in k or (r[k] is not None and -120<r[k]<-10)],k)
 for direction in ['UL']:
  ul=[r for r in alltcp if a<=r['timestamp_start_local']<b and r['direction']==direction and r['campaign_id']=='CAMPAIGN_6G_20260831' and r['status']=='OK' and r['protocol']=='TCP' and r['duration_seconds']==8 and r['omit_seconds']==1 and r['parallel_streams']==1 and r['route_verified']==1 and start and r['timestamp_start_local']>=start and r['timestamp_end_local'] and r['timestamp_end_local']<b and r['rf_telemetry_id'] in strict_ids and r['rf_time_delta_seconds'] is not None and abs(r['rf_time_delta_seconds'])<=300]
  item['ul_n']=len(ul);item['ul_median']=median(ul,'measured_throughput_mbps')
 for k in ['reported_dl_link_rate_mbps','reported_ul_link_rate_mbps']:item[k]=median(selected,k)
 item['dl_mcs_counts']={str(k):v for k,v in co.Counter(r.get('dl_mcs') for r in strict).items()}
 item['ul_mcs_counts']={str(k):v for k,v in co.Counter(r.get('ul_mcs') for r in strict).items()}
 out['segments'].append(item)
 out['source_projection'].extend({'segment':n,**{k:r[k] for k in ['id','test_id','timestamp_start_utc','timestamp_start_local','timestamp_end_local','measured_throughput_mbps','rf_telemetry_id','rf_time_delta_seconds','duration_seconds','omit_seconds','parallel_streams','route_verified']}} for r in selected)
c.rollback();c.close()
projection=json.dumps(out.pop('source_projection'),sort_keys=True,separators=(',',':')).encode();out['selected_projection_sha256']=hashlib.sha256(projection).hexdigest();out['selected_projection_rows']=sum(r['dl_n'] for r in out['segments'])
print('CLOSURE_JSON='+json.dumps(out,separators=(',',':')))
