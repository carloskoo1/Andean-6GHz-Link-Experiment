"""Read-only acquisition audit. No radio access, iperf, service or DB writes."""
import argparse
import collections
import datetime as dt
import json
import math
from pathlib import Path
import sqlite3

UTC = dt.timezone.utc

def instant(value):
    try:
        result = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return result.astimezone(UTC) if result.tzinfo else None
    except (ValueError, TypeError):
        return None

def radio_clock(raw, collected):
    """Do not treat a radio's naive wall clock as a trusted timestamp."""
    try:
        value = dt.datetime.strptime(raw, '%m/%d/%Y:%H:%M:%S')
    except (ValueError, TypeError):
        return {'present': False, 'timezone_verified': False}
    return {'present': True, 'timezone_verified': False,
            'raw_value': raw,
            'offset_seconds_if_raw_is_utc': (value.replace(tzinfo=UTC)-collected).total_seconds(),
            'use_as_analysis_time': False}

def audit(database, as_of=None, hours=24):
    if not math.isfinite(hours) or hours <= 0:
        raise ValueError('hours must be finite and positive')
    now = instant(as_of) if as_of is not None else dt.datetime.now(UTC)
    if now is None:
        raise ValueError('as_of must include a timezone')
    cutoff = now-dt.timedelta(hours=hours)
    con = sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    report = {'as_of_utc': now.isoformat(), 'cutoff_utc': cutoff.isoformat(),
              'window_hours': hours, 'read_only': True, 'campaign_authorized': False,
              'notes': ['Presence and quality audit; does not prove measurement accuracy or field readiness.',
                        'Missing observations are not imputed as zeros.'], 'tables': {}}
    specs = [('radio_link_config_telemetry','timestamp_utc'),
             ('active_throughput_6g','timestamp_start_utc'),
             ('station_observations','timestamp_utc'),('radio_link_local','timestamp_utc')]
    try:
        for table, timecol in specs:
            exists = con.execute('select 1 from sqlite_master where name=? and type in (?,?)',
                                 (table,'table','view')).fetchone()
            if not exists:
                report['tables'][table] = {'available': False}
                continue
            columns = {r[1] for r in con.execute('pragma table_info('+table+')')}
            if timecol not in columns:
                report['tables'][table] = {'available': True,'error':'missing timestamp column'}
                continue
            rows = [dict(r) for r in con.execute('select * from '+table+' where julianday('+timecol+')>=julianday(?) and julianday('+timecol+')<=julianday(?) order by julianday('+timecol+')', (cutoff.isoformat(),now.isoformat()))]
            latest = con.execute('select '+timecol+' from '+table+' order by julianday('+timecol+') desc limit 1').fetchone()
            last = instant(latest[0]) if latest else None
            item = {'available':True,'rows_in_window':len(rows),
                    'latest_utc':last.isoformat() if last else None,
                    'latest_age_seconds':(now-last).total_seconds() if last else None}
            report['tables'][table] = item
            if table == 'station_observations':
                groups = collections.defaultdict(list)
                for r in rows:groups[r.get('station_id')].append(r)
                item['stations'] = {}
                for site, rr in groups.items():
                    fields = ['temp_avg_C','hum_avg_pct','pres_avg_hPa','wind_speed_ms','wind_direction_deg','wind_gust_ms','rain_1min_mm','rain_1h_mm','rain_total_mm','pulses_total']
                    item['stations'][site] = {'rows':len(rr),
                        'nonnull':{k:sum(r.get(k) is not None for r in rr) for k in fields},
                        'quality_flags':{k:dict(collections.Counter(str(r.get(k)) for r in rr)) for k in ['bme_ok','wind_ok','rain_ok']}}
            elif table == 'radio_link_config_telemetry':
                item['statuses'] = dict(collections.Counter(r.get('collection_status') for r in rows))
                def strict(r):
                    return (r.get('collection_status')=='LINK_OPERATIONAL_DUAL'
                        and r.get('operating_frequency_mhz') is not None
                        and r.get('channel_bandwidth_mhz') is not None
                        and r.get('operating_frequency_mhz')==r.get('sm_operating_frequency_mhz')
                        and r.get('channel_bandwidth_mhz')==r.get('sm_channel_bandwidth_mhz'))
                item['dual_config_match_rows']=sum(strict(r) for r in rows)
                item['invalid_rssi_rows']={k:sum(not isinstance(r.get(k),(int,float)) or not -120<r[k]<-10 for r in rows) for k in ['dl_rssi_dbm','ul_rssi_dbm']}
                item['nonnull']={k:sum(r.get(k) is not None for r in rows) for k in ['dl_rssi_dbm','ul_rssi_dbm','dl_snr_db','ul_snr_db','ap_tx_power_dbm','sm_tx_power_dbm','dashboard_raw_json','sm_dashboard_raw_json']}
                item['radio_clocks']={}
                if rows:
                    latestrow=rows[-1];collected=instant(latestrow[timecol])
                    for side,key in [('AP','dashboard_raw_json'),('SM','sm_dashboard_raw_json')]:
                        try:raw=json.loads(latestrow.get(key) or '{}')
                        except (ValueError,TypeError):raw={}
                        item['radio_clocks'][side]=radio_clock(raw.get('cambiumDateTime') if isinstance(raw,dict) else None,collected)
            elif table == 'active_throughput_6g':
                item['statuses']=dict(collections.Counter(r.get('status') for r in rows))
                item['profiles']=[{'protocol':p[0],'duration':p[1],'omit':p[2],'streams':p[3],'direction':p[4],'count':n} for p,n in collections.Counter((r.get('protocol'),r.get('duration_seconds'),r.get('omit_seconds'),r.get('parallel_streams'),r.get('direction')) for r in rows).items()]
                item['rf_pair_within_300s_rows']=sum(isinstance(r.get('rf_time_delta_seconds'),(int,float)) and abs(r['rf_time_delta_seconds'])<=300 and r.get('rf_telemetry_id') is not None for r in rows)
                item['route_verified_rows']=sum(r.get('route_verified')==1 for r in rows)
            else:
                item['chains_nonnull']={k:sum(r.get(k) is not None for r in rows) for k in ['rssi_c0p','rssi_c0e','rssi_c1p','rssi_c1e']}
                item['chain_measurements_available']=any(item['chains_nonnull'].values())
    finally:
        con.close()
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',required=True)
    parser.add_argument('--as-of')
    parser.add_argument('--hours',type=float,default=24)
    args=parser.parse_args()
    print(json.dumps(audit(args.database,args.as_of,args.hours),ensure_ascii=False,indent=2))
