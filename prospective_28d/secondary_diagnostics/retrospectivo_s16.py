"""Exploracion retrospectiva, solo lectura. No define elegibilidad confirmatoria."""
import sqlite3, csv, json, statistics as st, collections as co, math, datetime
DB='/home/carlos/Proyectos/EstacionMeteorologica/SQLite/CU01/weather_local.db'
SCHEDULE='/home/carlos/Proyectos/Andean-6GHz-Link-Experiment/campaign_runtime/campaign_schedule.csv'
c=sqlite3.connect('file:'+DB+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
schedule=[r for r in csv.DictReader(open(SCHEDULE)) if r['phase']=='EXPERIMENT']
def segment(t):
 for r in schedule:
  if r['start_local']<=t<r['end_local']:return r
def med(v):
 v=[x for x in v if isinstance(x,(int,float)) and math.isfinite(x)]
 return round(st.median(v),4) if v else None
def phase(t):return 'noche_18_06' if int(t[11:13])>=18 or int(t[11:13])<6 else 'dia_06_18'
rf={};rh=co.defaultdict(list);rt=co.defaultdict(list);tcp=co.defaultdict(list);weather=co.defaultdict(list)
counters=co.defaultdict(lambda:co.defaultdict(set));chain_keys=set();invalid=co.Counter()
for row in c.execute("select * from radio_link_config_telemetry where timestamp_local>='2026-09-15' and timestamp_local<'2026-10-27'"):
 r=dict(row);seg=segment(r['timestamp_local'])
 if not seg:continue
 n=int(seg['sequence']);f=float(seg['frequency_mhz']);b=float(seg['bandwidth_mhz'])
 valid=r['collection_status']=='LINK_OPERATIONAL_DUAL' and r['operating_frequency_mhz']==r['sm_operating_frequency_mhz']==f and r['channel_bandwidth_mhz']==r['sm_channel_bandwidth_mhz']==b
 rf[r['id']]=r
 if not valid:invalid[n]+=1;continue
 r['_seg']=n;rh[r['timestamp_local'][:13]].append(r);rt[n].append(r)
 for field in ['dashboard_raw_json','sm_dashboard_raw_json','station_raw_json']:
  try:raw=json.loads(r[field]) if r[field] else {}
  except (ValueError,TypeError):raw={}
  if isinstance(raw,dict):
   for k,v in raw.items():
    if any(z in k.lower() for z in ['chain','rssi0','rssi1','rssi_c','polar']):chain_keys.add(field+':'+k)
    if 'RebootCounter' in k or k=='cambiumLANSpeedStatus':counters[n][field+':'+k].add(str(v))
for row in c.execute("select * from active_throughput_6g where campaign_id='CAMPAIGN_6G_20260831' and timestamp_start_local>='2026-09-15' and timestamp_start_local<'2026-10-27' and status='OK' and protocol='TCP' and duration_seconds=8 and omit_seconds=1 and parallel_streams=1"):
 r=dict(row);seg=segment(r['timestamp_start_local']);a=rf.get(r['rf_telemetry_id'])
 if not seg or not a:continue
 f=float(seg['frequency_mhz']);b=float(seg['bandwidth_mhz'])
 if not (a['collection_status']=='LINK_OPERATIONAL_DUAL' and a['operating_frequency_mhz']==a['sm_operating_frequency_mhz']==f and a['channel_bandwidth_mhz']==a['sm_channel_bandwidth_mhz']==b and r['operating_frequency_mhz']==f and r['channel_bandwidth_mhz']==b):continue
 # Exigir cercania explicita; no convertir emparejamiento en simultaneidad.
 delta=r['rf_time_delta_seconds']
 if delta is None or abs(delta)>300:continue
 r['_seg']=int(seg['sequence']);tcp[r['timestamp_start_local'][:13]].append(r)
for row in c.execute("select station_id,timestamp_local,temp_avg_C,hum_avg_pct,wind_speed_ms,wind_gust_ms,wind_ok,rain_1h_mm,rain_ok,bme_ok from station_observations where timestamp_local>='2026-09-15' and timestamp_local<'2026-10-27'"):
 r=dict(row);weather[(r['station_id'],r['timestamp_local'][:13])].append(r)
hourly=[]
for h,rr in sorted(rh.items()):
 ids=set(r['_seg'] for r in rr)
 if len(ids)!=1:continue
 n=next(iter(ids));seg=schedule[n-1];tr=tcp.get(h,[])
 item={'h':h,'seg':n,'f':int(seg['frequency_mhz']),'b':int(seg['bandwidth_mhz']),'nr':len(rr),'nd':sum(r['direction']=='DL' for r in tr),'nu':sum(r['direction']=='UL' for r in tr)}
 for key,name in [('dl_rssi_dbm','rd'),('ul_rssi_dbm','ru'),('dl_snr_db','sd'),('ul_snr_db','su'),('ap_tx_power_dbm','pa'),('sm_tx_power_dbm','ps')]:
  item[name]=med([r[key] for r in rr if key not in ['dl_rssi_dbm','ul_rssi_dbm'] or (r[key] is not None and -120<r[key]<-10)])
 for direction,name in [('DL','td'),('UL','tu')]:item[name]=med([r['measured_throughput_mbps'] for r in tr if r['direction']==direction])
 for site,prefix in [('CU01','c'),('SJ01','s')]:
  ww=weather.get((site,h),[]);item[prefix+'n']=len(ww)
  for key,name,flag in [('temp_avg_C','t','bme_ok'),('hum_avg_pct','h','bme_ok'),('wind_speed_ms','w','wind_ok'),('wind_gust_ms','g','wind_ok'),('rain_1h_mm','p','rain_ok')]:
   vv=[r[key] for r in ww if r[flag]==1 and isinstance(r[key],(int,float))]
   item[prefix+name]=round(max(vv),4) if vv and name in ['g','p'] else med(vv)
 hourly.append(item)
out={'extracted_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'RF dual strict; TCP 8/1 one stream, paired RF <=300s; hourly summaries; descriptive only','profiles':[],'segment_summary':[],'counter16':{k:sorted(v) for k,v in counters[16].items()},'chain_keys':sorted(chain_keys)}
for n in [6,12,16]:
 for p in ['dia_06_18','noche_18_06']:
  hh=[r for r in hourly if r['seg']==n and phase(r['h'])==p]
  out['profiles'].append({'seg':n,'period':p,'hours':len(hh),**{k:med([r[k] for r in hh]) for k in ['td','tu','rd','ru','sd','su','ch','sh','cw','sw','cp','sp']}})
for seg in schedule:
 n=int(seg['sequence']);hh=[r for r in hourly if r['seg']==n]
 out['segment_summary'].append({'seg':n,'f':int(seg['frequency_mhz']),'b':int(seg['bandwidth_mhz']),'hours':len(hh),'invalid_rf':invalid[n],**{k:med([r[k] for r in hh]) for k in ['td','tu','rd','ru','sd','su','pa','ps','ch','sh']}})
# Analogos elegidos solo por clima, con escalas fijas explicitas; no se seleccionan por RF/TCP.
# T/3 C, RH/10 puntos, viento/2 m/s y lluvia movil/2 mm. Mismo horario +-1 h.
keys={'ct':3,'st':3,'ch':10,'sh':10,'cw':2,'sw':2,'cp':2,'sp':2}
targets=[r for r in hourly if r['seg']==16 and r['nr']>=6 and r['td'] is not None and r['nd']>=2 and r['cn']>=30 and r['sn']>=20 and all(r.get(k) is not None for k in keys)]
controls=[r for r in hourly if r['seg']!=16 and r['nr']>=6 and r['td'] is not None and r['nd']>=2 and r['cn']>=30 and r['sn']>=20 and all(r.get(k) is not None for k in keys)]
matches=[]
for target in targets:
 hr=int(target['h'][11:13]);cand=[]
 for r in controls:
  dh=abs(int(r['h'][11:13])-hr);dh=min(dh,24-dh)
  if dh>1:continue
  dist=math.sqrt(sum(((target[k]-r[k])/scale)**2 for k,scale in keys.items())/len(keys))
  cand.append((dist,r))
 for label,cc in [('same_config',[(d,r) for d,r in cand if r['f']==7000 and r['b']==20]),('other_config',[(d,r) for d,r in cand if (r['f'],r['b'])!=(7000,20)])]:
  if cc:
   d,r=min(cc,key=lambda x:(x[0],x[1]['h']))
   matches.append({'type':label,'target':target['h'],'control':r['h'],'control_seg':r['seg'],'f':r['f'],'b':r['b'],'distance':round(d,4),'target_td':target['td'],'control_td':r['td'],'delta_td':round(target['td']-r['td'],4),'target_rd':target['rd'],'control_rd':r['rd'],'delta_rd':round(target['rd']-r['rd'],4) if target['rd'] is not None and r['rd'] is not None else None})
out['analogues_summary']=[]
for label in ['same_config','other_config']:
 for cap in [None,0.5]:
  mm=[m for m in matches if m['type']==label and (cap is None or m['distance']<=cap)]
  out['analogues_summary'].append({'type':label,'max_distance':cap,'n_pairs':len(mm),'unique_controls':len(set(m['control'] for m in mm)),'median_distance':med([m['distance'] for m in mm]),'median_delta_rssi':med([m['delta_rd'] for m in mm]),'median_delta_tcp':med([m['delta_td'] for m in mm])})
out['analogues_examples']=sorted([m for m in matches if m['type']=='same_config'],key=lambda r:r['distance'])[:8]
out['hour_profiles_7000_20']=[]
for n in [6,12,16]:
 for hr in range(24):
  hh=[r for r in hourly if r['seg']==n and int(r['h'][11:13])==hr]
  out['hour_profiles_7000_20'].append([n,hr,len(hh),med([r['td'] for r in hh]),med([r['tu'] for r in hh]),med([r['rd'] for r in hh]),med([r['ru'] for r in hh])])
out['hourly_episode']=[r for r in hourly if '2026-10-19'<=r['h']<'2026-10-27']
out['hourly_comparators']=[r for r in hourly if r['seg'] in [6,12,16]]
out['matches']=matches
c.close()
print('RETROSPECTIVE_JSON='+json.dumps(out,separators=(',',':'),ensure_ascii=False))
