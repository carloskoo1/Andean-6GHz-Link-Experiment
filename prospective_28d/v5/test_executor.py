import copy
import json
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
from campaign_orchestrator import CampaignError
from prospective_28d.v2 import prospective_plan as plan
from prospective_28d.v4.safety import Guard,Clock,Blocked,Uncertain,Busy
from prospective_28d.v5.executor import UnifiedExecutor,SimulatedLuci,APIBridge,TCP,validate_tcp
EVIDENCE={'mode':'LAB_ONLY','original_closed':True,'original_timer_disabled':True,'stability_48h':True,'expert_conditions':True}

class UnifiedTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.g=Guard(Path(self.tmp.name)/'guard');self.g.handover_lab(EVIDENCE)
        self.p=plan.read_plan();self.at=datetime.fromisoformat(plan.generate(self.p)[0]['start_local'])
        self.clock=Clock(self.at.timestamp());self.server=SimulatedLuci(self.clock)
        self.e=UnifiedExecutor(self.p,self.g,self.server,self.clock)
        for name in ('socket.socket','subprocess.run'):
            p=patch(name,side_effect=AssertionError('REAL_IO_FORBIDDEN'));p.start();self.addCleanup(p.stop)
    def state(self):
        with self.g.lease('prospective',recovery=True) as s:return copy.deepcopy(s.data)
    def target(self,row=0):
        r=self.e.rows[row];return (r['frequency_mhz'],r['bandwidth_mhz'])
    def tick(self):return self.e.tick(self.at)
    def parse(self,stamp):return datetime.fromisoformat(stamp)
    def fail(self,fault):
        self.server.radio.fault=fault
        with self.assertRaises(Uncertain):self.tick()
    def recover(self):return self.e.recover(clock_trusted=True)
    def good_interval(self,w=None):
        w=w or self.tick();a=self.parse(w['analysis_start']);return a,a+timedelta(seconds=20)
    def test_real_api_contract_and_effective_times(self):
        w=self.tick();self.assertEqual(w['status'],'LAB_COMMITTED')
        self.assertGreater(self.parse(w['verified_at']),self.parse(w['confirm_ack_at']))
        self.assertEqual(self.parse(w['analysis_start'])-self.parse(w['verified_at']),timedelta(seconds=300))
        self.assertGreater(self.parse(w['trial_requested_at']),self.parse(w['requested_at']))
        self.assertFalse(w['study_eligible']);self.assertEqual(self.server.secondary_frequency,'0')
    def test_configuration_id_read_and_updated(self):
        self.tick();self.assertGreater(self.server.config_id,1)
        self.assertEqual(self.e.candidate.radio.api.config_id,str(self.server.config_id))
    def test_trial_lost_before_acceptance(self):
        self.fail('trial_before');self.clock.advance(360)
        self.assertEqual(self.recover(),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
        self.assertEqual(self.server.radio.current,(7000,20))
    def test_trial_lost_after_acceptance(self):
        self.fail('trial_after');events=len(self.server.events)
        self.assertEqual(self.recover(),'WAIT_NO_WRITES');self.assertEqual(len(self.server.events),events)
        self.clock.advance(360);self.assertEqual(self.recover(),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_confirm_lost_before_acceptance(self):
        self.fail('confirm_before');self.clock.advance(360)
        self.assertEqual(self.recover(),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_confirm_lost_after_acceptance_restores(self):
        self.fail('confirm_after');self.clock.advance(360)
        self.assertEqual(self.recover(),'RESTORE_PENDING_RECHECK');self.clock.advance(360)
        self.assertEqual(self.recover(),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
        self.assertEqual(self.server.radio.current,(7000,20))
    def test_restore_ack_loss_reconciled(self):
        self.fail('confirm_after');self.clock.advance(360);self.server.radio.fault='confirm_after'
        self.assertEqual(self.recover(),'RESTORE_PENDING_RECHECK');self.clock.advance(360)
        self.assertEqual(self.recover(),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_unknown_rf_no_recovery_write(self):
        self.fail('confirm_after');self.clock.advance(360);self.server.radio.current=(6655,40)
        writes=[v for v in self.server.radio.calls if isinstance(v,tuple)]
        self.assertEqual(self.recover(),'MANUAL_REQUIRED')
        self.assertEqual(writes,[v for v in self.server.radio.calls if isinstance(v,tuple)])
    def test_incident_window_excluded_after_recovery(self):
        self.fail('trial_after');self.clock.advance(360);self.recover()
        a=self.at+timedelta(minutes=20)
        result=self.e.classify_interval(a,a+timedelta(seconds=20),qc_passed=True,observed_target=self.target())
        self.assertEqual(result['reason'],'UNVERIFIED_OR_INCIDENT');self.assertFalse(result['temporal_eligible'])
    def test_ack_does_not_resume_schedule(self):
        self.fail('trial_after');self.clock.advance(360);self.recover()
        self.g.acknowledge_lab('prospective','v5-1');self.clock.now=self.at.timestamp()
        with self.assertRaises(Blocked):self.tick()
    def test_duplicate_no_api_calls(self):
        self.tick();count=len(self.server.events)
        # A timer tick may be repeated with clock matched to its instant.
        at=datetime.fromtimestamp(self.clock.now,self.at.tzinfo)
        self.assertEqual(self.e.tick(at)['status'],'ALREADY_RECORDED');self.assertEqual(len(self.server.events),count)
    def test_restart_preserves_window(self):
        w=self.tick();self.e=UnifiedExecutor(self.p,Guard(self.g.directory),self.server,self.clock)
        self.assertEqual(self.state()['v5_windows']['1']['analysis_start'],w['analysis_start'])
    def test_restart_pending_recovers(self):
        self.fail('confirm_after');self.e=UnifiedExecutor(self.p,Guard(self.g.directory),self.server,self.clock)
        self.clock.advance(360);self.assertEqual(self.recover(),'RESTORE_PENDING_RECHECK')
    def test_changed_contract_blocks_before_recovery(self):
        self.fail('confirm_after');self.clock.advance(360);self.e.settle=301;n=len(self.server.events)
        with self.assertRaises(Blocked):self.recover()
        self.assertEqual(len(self.server.events),n)
    def test_transition_exclusion(self):
        w=self.tick();a=self.parse(w['verified_at'])
        r=self.e.classify_interval(a,a+timedelta(seconds=2),qc_passed=True,observed_target=self.target())
        self.assertEqual(r['reason'],'TRANSITION_OR_SETTLING')
    def test_analysis_start_inclusive(self):
        a,b=self.good_interval();r=self.e.classify_interval(a,b,qc_passed=True,observed_target=self.target())
        self.assertTrue(r['temporal_eligible']);self.assertFalse(r['study_eligible'])
    def test_measurement_crosses_end_excluded(self):
        w=self.tick();end=self.parse(w['scheduled_end'])
        r=self.e.classify_interval(end-timedelta(seconds=5),end+timedelta(seconds=1),qc_passed=True,observed_target=self.target())
        self.assertEqual(r['reason'],'CROSSES_WINDOW_END')
    def test_measurement_end_exact_boundary(self):
        w=self.tick();end=self.parse(w['scheduled_end'])
        r=self.e.classify_interval(end-timedelta(seconds=20),end,qc_passed=True,observed_target=self.target())
        self.assertTrue(r['temporal_eligible'])
    def test_qc_not_presumed(self):
        a,b=self.good_interval();self.assertEqual(self.e.classify_interval(a,b,observed_target=self.target())['reason'],'QC_PENDING')
    def test_rf_not_presumed(self):
        a,b=self.good_interval();self.assertEqual(self.e.classify_interval(a,b,qc_passed=True)['reason'],'RF_NOT_CONFIRMED')
    def test_wrong_rf_excluded(self):
        a,b=self.good_interval();self.assertEqual(self.e.classify_interval(a,b,qc_passed=True,observed_target=(1234,20))['reason'],'RF_NOT_CONFIRMED')
    def test_no_window(self):
        self.assertEqual(self.e.classify_interval(self.at-timedelta(seconds=20),self.at)['reason'],'NO_VERIFIED_WINDOW')
    def test_invalid_interval(self):
        with self.assertRaises(Blocked):self.e.classify_interval(self.at,self.at)
    def test_naive_time(self):
        with self.assertRaises(Blocked):self.e.tick(self.at.replace(tzinfo=None))
    def test_late_slot(self):
        self.clock.advance(61)
        with self.assertRaises(Blocked):self.e.tick(self.at+timedelta(seconds=61))
        self.assertEqual(self.server.events,[])
    def test_skipped_slot(self):
        at=self.parse(self.e.rows[1]['start_local']);self.clock.now=at.timestamp()
        with self.assertRaises(Blocked):self.e.tick(at)
    def test_clock_mismatch(self):
        self.clock.advance(5)
        with self.assertRaises(Blocked):self.tick()
    def test_tcp_stays_disabled(self):
        with self.assertRaises(Blocked):self.e.request_tcp_measurement('tcp_8s_omit1')
        self.assertIsNone(self.e.tcp['active_profile_id'])
    def test_cannot_self_approve_tcp(self):
        tcp=json.loads(TCP.read_text());tcp['status']='APPROVED'
        with self.assertRaises(Blocked):UnifiedExecutor(self.p,self.g,self.server,self.clock,tcp=tcp)
    def test_tcp_invalid_omit(self):
        tcp=json.loads(TCP.read_text());tcp['profiles_for_comparison']['tcp_8s_omit1']['omit_seconds']=9
        with self.assertRaises(Blocked):validate_tcp(tcp)
    def test_original_role_excludes_prospective(self):
        with self.assertRaises(Blocked):
            with self.g.lease('original'):pass
    def test_shared_lock_used_by_tick(self):
        with self.g.lease('prospective'):
            with self.assertRaises(Busy):self.tick()
        self.assertEqual(self.server.events,[])
    def test_live_disabled(self):
        with self.assertRaises(Blocked):UnifiedExecutor(self.p,self.g,self.server,self.clock,live=True)
    def test_arbitrary_opener_disabled(self):
        with self.assertRaises(Blocked):APIBridge(object())
    def test_malformed_getparam_blocks_without_write(self):
        self.server.unexpected_payload=True
        with self.assertRaises(CampaignError):self.tick()
        self.assertFalse(any(e['endpoint']=='set_param' for e in self.server.events))
        self.assertEqual(self.state()['v5_windows']['1']['status'],'INCIDENT')
    def test_calendar49_including_reserve_and_noop(self):
        noop=0
        for row in self.e.rows:
            at=self.parse(row['start_local']);self.clock.now=at.timestamp();w=self.e.tick(at)
            noop+=w['status']=='LAB_NO_CHANGE'
            if w['phase']=='RESERVE':
                a=self.parse(w['analysis_start']);r=self.e.classify_interval(a,a+timedelta(seconds=20),qc_passed=True,observed_target=w['target'])
                self.assertEqual(r['reason'],'RESERVE')
            if w['status']=='LAB_NO_CHANGE':self.assertIsNone(w['confirm_ack_at'])
        self.assertEqual(self.state()['last_sequence'],49);self.assertEqual(noop,3)
        self.assertEqual(self.server.radio.current,(7000,20))
    def test_history_not_discarded_by_later_failure(self):
        w=self.tick();a,b=self.good_interval(w);next_at=self.parse(self.e.rows[1]['start_local'])
        self.clock.now=next_at.timestamp();self.server.radio.fault='trial_after'
        with self.assertRaises(Uncertain):self.e.tick(next_at)
        r=self.e.classify_interval(a,b,qc_passed=True,observed_target=w['target'])
        self.assertTrue(r['temporal_eligible'])
    def test_tcp_change_after_construction(self):
        self.e.tcp['profiles_for_comparison']['tcp_8s_omit1']['duration_seconds']=9
        with self.assertRaises(Blocked):self.tick()
        self.assertEqual(self.server.events,[])
    def test_failure_after_confirmation_never_marks_eligible(self):
        from prospective_28d.v4.safety import Session
        original=Session.save
        def save(session,event,detail):
            if event=='V5_WINDOW_VERIFIED':raise OSError('LAB_DISK_ERROR')
            return original(session,event,detail)
        with patch.object(Session,'save',save):
            with self.assertRaises(OSError):self.tick()
        window=self.state()['v5_windows']['1']
        self.assertEqual(window['status'],'INCIDENT');self.assertIsNone(window['analysis_start'])
        self.assertTrue(self.state()['schedule_halted'])
    def test_tcp_profile_label_must_match(self):
        tcp=json.loads(TCP.read_text());tcp['profiles_for_comparison']['tcp_8s_omit1']['duration_seconds']=9
        with self.assertRaises(Blocked):validate_tcp(tcp)
    def test_tcp_cadence_not_self_frozen(self):
        tcp=json.loads(TCP.read_text());tcp['interval_minutes']=60
        with self.assertRaises(Blocked):validate_tcp(tcp)
    def test_rehearsal_full_flow(self):
        from prospective_28d.v5.rehearse import rehearse
        r=rehearse()
        self.assertEqual(len(r['timeline']),49);self.assertEqual(r['tcp_executions'],0)
        self.assertTrue(all(x['calendar_halted'] for x in r['incident_recovery_examples']))
        self.assertTrue(all(x['window']['analysis_start'] is None for x in r['incident_recovery_examples']))
    def test_untrusted_recovery_time(self):
        self.fail('trial_after')
        with self.assertRaises(Blocked):self.e.recover()
    def test_settle_does_not_fit_window(self):
        self.e=UnifiedExecutor(self.p,self.g,self.server,self.clock,settle_seconds=43199)
        with self.assertRaises(Blocked):self.tick()
        self.assertIsNone(self.state()['v5_windows']['1']['analysis_start'])

if __name__=='__main__':unittest.main()
