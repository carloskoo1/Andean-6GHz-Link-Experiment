import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from audit_acquisition import audit, radio_clock

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'fixture.db'
        c=sqlite3.connect(self.path)
        c.execute('create table radio_link_config_telemetry(timestamp_utc text, collection_status text, operating_frequency_mhz real, sm_operating_frequency_mhz real, channel_bandwidth_mhz real, sm_channel_bandwidth_mhz real, dl_rssi_dbm real, ul_rssi_dbm real, dashboard_raw_json text, sm_dashboard_raw_json text)')
        rows=[('2026-10-26T11:59:59Z','LINK_OPERATIONAL_DUAL',7000,7000,20,20,-75,-80,'{}','{}'),
              ('2026-10-26T12:00:00Z','LINK_OPERATIONAL_DUAL',7000,7000,20,20,-75,-80,'{}','{}'),
              ('2026-10-27T06:59:00-05:00','LINK_OPERATIONAL_DUAL',7000,0,20,None,0,None,'{}','{}'),
              ('2026-10-27T13:00:00Z','LINK_OPERATIONAL_DUAL',7000,7000,20,20,-75,-80,'{}','{}')]
        c.executemany('insert into radio_link_config_telemetry values(?,?,?,?,?,?,?,?,?,?)',rows)
        c.execute('create table radio_link_local(timestamp_utc text,rssi_c0p real,rssi_c0e real,rssi_c1p real,rssi_c1e real)')
        c.execute("insert into radio_link_local values('2026-10-27T11:59:00Z',NULL,NULL,NULL,NULL)")
        c.commit();c.close()
    def tearDown(self):self.tmp.cleanup()
    def run_audit(self):return audit(self.path,'2026-10-27T12:00:00Z')
    def test_window_handles_timezone_and_excludes_future(self):
        self.assertEqual(self.run_audit()['tables']['radio_link_config_telemetry']['rows_in_window'],2)
    def test_aggregate_status_does_not_override_bad_endpoint(self):
        r=self.run_audit()['tables']['radio_link_config_telemetry'];self.assertEqual(r['dual_config_match_rows'],1)
    def test_zero_and_missing_rssi_are_invalid(self):
        self.assertEqual(self.run_audit()['tables']['radio_link_config_telemetry']['invalid_rssi_rows'],{'dl_rssi_dbm':1,'ul_rssi_dbm':1})
    def test_null_chains_not_reported_as_measurements(self):
        self.assertFalse(self.run_audit()['tables']['radio_link_local']['chain_measurements_available'])
    def test_missing_tables_reported(self):
        self.assertFalse(self.run_audit()['tables']['station_observations']['available'])
    def test_audit_does_not_change_source_bytes_or_authorize_campaign(self):
        before=hashlib.sha256(self.path.read_bytes()).digest();r=self.run_audit()
        self.assertEqual(before,hashlib.sha256(self.path.read_bytes()).digest());self.assertFalse(r['campaign_authorized'])
    def test_naive_reference_time_rejected(self):
        with self.assertRaises(ValueError):audit(self.path,'2026-10-27T12:00:00')
    def test_radio_clock_is_untrusted_and_offset_explicit(self):
        r=radio_clock('10/28/2026:06:22:56',dt.datetime(2026,10,27,19,22,57,tzinfo=dt.timezone.utc))
        self.assertEqual(r['offset_seconds_if_raw_is_utc'],39599);self.assertFalse(r['use_as_analysis_time'])
    def test_malformed_radio_clock_is_missing(self):
        self.assertFalse(radio_clock('invalid',dt.datetime.now(dt.timezone.utc))['present'])
    def test_nonpositive_window_rejected(self):
        with self.assertRaises(ValueError):audit(self.path,hours=0)

if __name__=='__main__':unittest.main()
