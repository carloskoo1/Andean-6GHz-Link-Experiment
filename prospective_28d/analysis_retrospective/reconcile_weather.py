"""Offline audit only: original SQLite and field controller are never modified."""
import argparse,bisect,datetime as dt,hashlib,json,sqlite3
from pathlib import Path

CAMPAIGN='LUISITA_PROSPECTIVE_28D_20261102'
DB='/home/carlos/Proyectos/EstacionMeteorologica/SQLite/CU01/weather_local.db'
def stamp(s):
    d=dt.datetime.fromisoformat(s)
    if d.tzinfo is None:raise ValueError('Naive timestamp')
    return d.timestamp()
def nearest(rows,t):
    # Earlier observation wins an exact-distance tie; ID breaks duplicate-time ties.
    return min(rows,key=lambda r:(abs(stamp(r['timestamp_utc'])-t),stamp(r['timestamp_utc']),r['source_id'])) if rows else None
def analyze(snapshot):
    result=[]
    for test in snapshot['tcp']:
        t=stamp(test['timestamp_start_utc'])
        row={'tcp_id':test['id'],'test_id':test['test_id'],'direction':test['direction'],'timestamp_start_utc':test['timestamp_start_utc']}
        for station in ['CU01','SJ01']:
            samples=snapshot['weather'][station]
            chosen=nearest(samples,t)
            gap=abs(stamp(chosen['timestamp_utc'])-t) if chosen else None
            old=test[station.lower()+'_weather_time_delta_seconds']
            mature=bool(samples and max(stamp(r['timestamp_utc']) for r in samples)>=t+120)
            row[station]={'original_delta_seconds':old,'original_timestamp_local':test[station.lower()+'_weather_timestamp_local'],
                'source_id':chosen['source_id'] if chosen else None,
                'timestamp_utc':chosen['timestamp_utc'] if chosen else None,
                'signed_delta_seconds':stamp(chosen['timestamp_utc'])-t if chosen else None,
                'delta_seconds':gap,'within_120s':gap is not None and gap<=120,
                'mature':mature,'original_within_120s':old is not None and old<=120,
                'bme_ok':chosen.get('bme_ok') if chosen else None,
                'rain_ok':chosen.get('rain_ok') if chosen else None,
                'wind_ok':chosen.get('wind_ok') if chosen else None}
        result.append(row)
    stats={}
    for st in ['CU01','SJ01']:
        data=[r[st] for r in result]
        stats[st]={'n':len(data),'original_within_120s':sum(x['original_within_120s'] for x in data),
          'retrospective_within_120s':sum(x['within_120s'] for x in data),
          'recovered':sum(x['within_120s'] and not x['original_within_120s'] for x in data),
          'unmatched':sum(not x['within_120s'] for x in data),
          'immature':sum(not x['mature'] for x in data),
          'max_delta_seconds':max((x['delta_seconds'] for x in data if x['delta_seconds'] is not None),default=None),
          'bme_rain_wind_all_ok':sum(x['within_120s'] and all(x[k]==1 for k in ['bme_ok','rain_ok','wind_ok']) for x in data)}
    return {'summary':stats,'rows':result}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--snapshot',type=Path)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    if args.snapshot:snapshot=json.loads(args.snapshot.read_text())
    else:
        c=sqlite3.connect('file:'+DB+'?mode=ro',uri=True,timeout=15);c.row_factory=sqlite3.Row;c.execute('BEGIN')
        fields=['id','test_id','campaign_id','direction','timestamp_start_utc','timestamp_start_local','status']
        for st in ['cu01','sj01']:fields += [st+'_weather_timestamp_local',st+'_weather_time_delta_seconds']
        tcp=[dict(r) for r in c.execute('SELECT '+','.join(fields)+' FROM active_throughput_6g WHERE campaign_id=? ORDER BY timestamp_start_utc,id',(CAMPAIGN,))]
        if not tcp:raise RuntimeError('No prospective tests')
        low=dt.datetime.fromtimestamp(min(stamp(x['timestamp_start_utc']) for x in tcp)-600,dt.timezone.utc).isoformat()
        high=dt.datetime.fromtimestamp(max(stamp(x['timestamp_start_utc']) for x in tcp)+600,dt.timezone.utc).isoformat()
        common='timestamp_utc,timestamp_local,station_id,temp_avg_C,hum_avg_pct,pres_avg_hPa,rain_1min_mm,rain_1h_mm,rain_total_mm,wind_speed_ms,wind_gust_ms,wind_direction_deg,bme_ok,rain_ok,wind_ok'
        weather={}
        for st,table,key in [('CU01','weather_local','id'),('SJ01','station_observations','central_id')]:
            where="(station_id='CU01' OR station_id IS NULL)" if st=='CU01' else "(source_station_id='SJ01' OR station_id='SJ01')"
            weather[st]=[dict(r) for r in c.execute('SELECT '+key+' AS source_id,'+common+' FROM '+table+' WHERE '+where+' AND timestamp_utc>=? AND timestamp_utc<=? ORDER BY timestamp_utc,'+key,(low,high))]
        c.close()
        snapshot={'observed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'campaign_id':CAMPAIGN,'range_utc':[low,high],'tcp':tcp,'weather':weather}
    raw=(json.dumps(snapshot,indent=2)+'\n').encode()
    (args.output/'snapshot.json').write_bytes(raw)
    audit=analyze(snapshot);audit['snapshot_sha256']=hashlib.sha256(raw).hexdigest()
    (args.output/'pairing.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'observed_at_utc':snapshot['observed_at_utc'],'summary':audit['summary'],'snapshot_sha256':audit['snapshot_sha256']},indent=2))
if __name__=='__main__':main()
