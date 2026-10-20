import contextlib
import copy
import io
import sqlite3
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
from campaign_orchestrator import load_config
from prospective_28d.v2 import prospective_plan as plan
from prospective_28d.v3.adapter import AdapterError,LabAPI,LabOrchestrator,ProspectiveAdapter,lock
from prospective_28d.v3.rehearse import rehearse
ROOT=Path(__file__).resolve().parents[2]

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)
        self.c=copy.deepcopy(load_config(ROOT/'campaign_plan.template.json'))
        self.c['outputs']['directory']=str(self.out)
        self.p=plan.read_plan(); self.api=LabAPI()
        self.orch=LabOrchestrator(self.c,ROOT/'campaign_plan.template.json',self.api)
        self.adapter=ProspectiveAdapter(self.p,self.orch)
        self.row=self.adapter.rows[0]; self.at=datetime.fromisoformat(self.row['start_local'])
        redirect=contextlib.redirect_stdout(io.StringIO()); redirect.__enter__()
        self.addCleanup(redirect.__exit__,None,None,None)
    def go(self,row=None,at=None):return self.adapter.transition(row or self.row,at or self.at)
    def status(self):
        with sqlite3.connect(self.out/'prospective.sqlite') as db:
            return db.execute('SELECT status FROM transitions ORDER BY seq').fetchall()
    def test_full49_no_network(self):
        with patch('campaign_orchestrator.ping',side_effect=AssertionError('No network')), patch('urllib.request.OpenerDirector.open',side_effect=AssertionError('No HTTP')):
            r=rehearse()
        self.assertEqual((r['transitions'],r['treatments'],r['reserves'],r['confirmed_trials']),(49,42,7,49))
        self.assertFalse(r['sm_rf_verified']);self.assertEqual(r['real_rf_changes'],0)
        self.assertEqual(r['final_ap_simulated']['wirelessInterfaceHTMode'],'1')
    def test_commit_readback(self):
        r=self.go();self.assertEqual(r['status'],'LAB_VERIFIED')
        self.assertIn(('finish',True),self.api.calls);self.assertEqual(self.status(),[('VERIFIED',)])
        self.assertFalse(r['study_eligible']);self.assertFalse(r['sm_rf_readback'])
    def test_secondary_frequency_preserved(self):
        self.go();self.assertEqual(self.api.props['centerFrequency2'],'0')
    def test_duplicate(self):
        self.go();calls=list(self.api.calls)
        self.assertEqual(self.go()['status'],'ALREADY_RECORDED');self.assertEqual(self.api.calls,calls)
    def test_restart(self):
        self.go();self.adapter=ProspectiveAdapter(self.p,self.orch)
        calls=list(self.api.calls);self.go();self.assertEqual(self.api.calls,calls)
    def test_preflight_failure(self):
        self.orch.reachable=False
        with self.assertRaises(AdapterError):self.go()
        self.assertFalse(any(isinstance(c,tuple) and c[0]=='trial' for c in self.api.calls))
        self.assertEqual(self.status(),[('HALTED',)])
    def test_reassociation_failure_cancels(self):
        self.orch.fail_stable_call=1
        with self.assertRaises(AdapterError):self.go()
        self.assertIn(('finish',False),self.api.calls);self.assertEqual(self.api.props['centerFrequency'],'7000')
    def test_post_commit_failure_rolls_back(self):
        self.orch.fail_stable_call=2
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls.count(('finish',True)),2)
        self.assertEqual(self.api.props['wirelessInterfaceHTMode'],'1');self.assertEqual(self.status(),[('HALTED',)])
    def test_cancel_failure_safe_abort(self):
        self.api.fault='cancel';self.orch.fail_stable_call=1
        with self.assertRaises(AdapterError):self.go()
        self.assertTrue((self.out/'SAFE_ABORT.json').exists());calls=list(self.api.calls)
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls,calls)
    def test_wrong_readback(self):
        self.api.fault='wrong_readback'
        with self.assertRaises(AdapterError):self.go()
        self.assertNotIn(('finish',True),self.api.calls);self.assertEqual(self.status(),[('HALTED',)])
    def test_read_failure(self):
        self.api.fault='read'
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.status(),[('HALTED',)])
    def test_crash_intent(self):
        self.go()
        with sqlite3.connect(self.out/'prospective.sqlite') as db:db.execute("UPDATE transitions SET status='INTENT'")
        calls=list(self.api.calls)
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls,calls)
    def test_safe_abort(self):
        (self.out/'SAFE_ABORT.json').write_text('{}')
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls,[])
    def test_lock(self):
        with lock(self.out/'prospective.lock'):
            with self.assertRaises(RuntimeError):self.go()
        self.assertEqual(self.api.calls,[])
    def test_late(self):
        with self.assertRaises(AdapterError):self.go(at=self.at+timedelta(seconds=61))
        self.assertEqual(self.api.calls,[])
        with self.assertRaises(AdapterError):self.go()
    def test_skip(self):
        row=self.adapter.rows[1]
        with self.assertRaises(AdapterError):self.go(row,datetime.fromisoformat(row['start_local']))
        self.assertEqual(self.api.calls,[])
    def test_end_exclusive(self):
        with self.assertRaises(AdapterError):self.go(at=datetime.fromisoformat(self.row['end_local']))
        self.assertEqual(self.api.calls,[])
    def test_naive_clock(self):
        with self.assertRaises(AdapterError):self.go(at=self.at.replace(tzinfo=None))
    def test_tampered_row(self):
        with self.assertRaises(AdapterError):self.go({**self.row,'frequency_mhz':9999})
    def test_live_disabled(self):
        with self.assertRaises(AdapterError):ProspectiveAdapter(self.p,self.orch,live=True)
        self.assertEqual(self.api.calls,[])
    def test_arbitrary_backend_rejected(self):
        with self.assertRaises(AdapterError):ProspectiveAdapter(self.p,object())
    def test_config_changed_restart(self):
        self.go();self.adapter=ProspectiveAdapter(self.p,self.orch,settle_seconds=301)
        with self.assertRaises(AdapterError):self.go()
    def test_settle_overrun(self):
        with self.assertRaises(AdapterError):ProspectiveAdapter(self.p,self.orch,settle_seconds=43200)
    def test_mutation_after_construction(self):
        self.c['safety']['minimum_successful_probes']=99
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls,[])
    def test_trial_ack_lost_is_uncertain_and_blocked(self):
        self.api.fault='trial_ack_lost'
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.status(),[('HALTED',)])
        self.assertNotIn(('finish',True),self.api.calls)
        calls=list(self.api.calls)
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.api.calls,calls)
    def test_confirm_ack_lost_is_not_success(self):
        self.api.fault='confirm_ack_lost'
        with self.assertRaises(AdapterError):self.go()
        self.assertEqual(self.status(),[('HALTED',)])
        with self.assertRaises(AdapterError):self.go()
    def test_invalid_original_config(self):
        self.c['safety']['trial_timeout_seconds']=1
        with self.assertRaises(AdapterError):ProspectiveAdapter(self.p,self.orch)

if __name__=='__main__':unittest.main()
