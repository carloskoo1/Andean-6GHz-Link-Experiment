import copy
from datetime import datetime,timedelta
import json
from pathlib import Path
import tempfile
import unittest
import controller as m


class Backend:
    def __init__(self):
        self.rf=dict(ap_f=7000,ap_b=20,sm_f=7000,sm_b=20)
        self.writes=[];self.measurements=[];self.fail=None
    def precheck(self):
        if self.fail=='precheck':raise RuntimeError('precheck failed')
    def readback(self):return self.rf.copy()
    def trial(self,row):
        self.writes.append(('trial',row['segment_id']))
        self.rf=dict(ap_f=row['frequency_mhz'],ap_b=row['bandwidth_mhz'],sm_f=row['frequency_mhz'],sm_b=row['bandwidth_mhz'])
        if self.fail=='trial':raise RuntimeError('lost trial ACK')
    def confirm(self):
        self.writes.append(('confirm',))
        if self.fail=='confirm':raise RuntimeError('lost confirm ACK')
    def wait_target(self,row,deadline_seconds):
        if self.fail=='wait':raise RuntimeError('readback failed')
    def measure(self,row):self.measurements.append(row['segment_id'])


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)
        self.plan=m.load_plan(Path(__file__).with_name('plan.json'))
        self.now=m.parse(self.plan['windows'][0]['start_local'])+timedelta(seconds=1)
        self.io=Backend();self.c=m.Controller(self.plan,self.io,self.folder,clock=lambda:self.now)
    def tearDown(self):self.tmp.cleanup()
    def test_waits_without_RF(self):
        self.now-=timedelta(hours=1);self.assertEqual(self.c.step(),'WAITING_START');self.assertEqual(self.io.writes,[])
    def test_committed_once(self):
        self.assertEqual(self.c.step(),'WINDOW_VERIFIED');self.assertEqual(self.c.step(),'SETTLING');self.assertEqual(len(self.io.writes),2)
    def test_lost_trial_blocks_after_restart(self):
        self.io.fail='trial'
        with self.assertRaises(RuntimeError):self.c.step()
        self.io.fail=None;self.assertEqual(self.c.step(),'HALTED');self.assertEqual(len(self.io.writes),1)
    def test_lost_confirm_blocks_after_restart(self):
        self.io.fail='confirm'
        with self.assertRaises(RuntimeError):self.c.step()
        self.io.fail=None;self.assertEqual(self.c.step(),'HALTED');self.assertEqual(len(self.io.writes),2)
    def test_readback_failure_does_not_confirm(self):
        self.io.fail='wait'
        with self.assertRaises(RuntimeError):self.c.step()
        self.assertEqual(len(self.io.writes),1);self.assertEqual(self.c.step(),'HALTED')
    def test_missed_window_halts_without_RF(self):
        self.now+=timedelta(minutes=11);self.assertEqual(self.c.step(),'HALTED');self.assertEqual(self.io.writes,[])
    def test_pending_journal_blocks_without_RF(self):
        m.atomic(self.folder/'PENDING.json',{'incomplete':True});self.assertEqual(self.c.step(),'HALTED');self.assertEqual(self.io.writes,[])
    def test_no_measure_during_settling(self):
        self.c.step();self.now+=timedelta(minutes=14);self.assertEqual(self.c.step(),'SETTLING');self.assertEqual(self.io.measurements,[])
    def test_measure_once_per_slot(self):
        self.c.step();self.now=self.now.replace(minute=45,second=1)
        self.assertEqual(self.c.step(),'MEASURED');self.assertEqual(self.c.step(),'ALREADY_MEASURED');self.assertEqual(len(self.io.measurements),1)
    def test_missing_RF_is_not_fabricated(self):
        self.c.step();self.now=self.now.replace(minute=45,second=1);self.io.rf['sm_b']=None
        self.assertEqual(self.c.step(),'RF_UNVERIFIED');self.assertEqual(self.io.measurements,[])
    def test_reserve_is_separate_reference(self):
        reserve=self.plan['windows'][6];self.assertEqual(reserve['phase'],'RESERVE');self.assertEqual((reserve['frequency_mhz'],reserve['bandwidth_mhz']),(7000,20))
    def test_final_target_reference(self):
        t=m.target(self.plan,m.parse(self.plan['windows'][-1]['end_local']));self.assertEqual(t['phase'],'FINAL_REFERENCE');self.assertEqual(t['frequency_mhz'],7000)
    def test_frozen_hash_rejects_changes(self):
        f=self.folder/'source.py';f.write_text('changed')
        with self.assertRaises(RuntimeError):m.verify_manifest({str(f):'wrong'})
    def test_invalid_calendar_rejected(self):
        plan=copy.deepcopy(self.plan);plan['windows'][1]['start_local']=plan['windows'][0]['start_local']
        f=self.folder/'bad.json';f.write_text(json.dumps(plan))
        with self.assertRaises(ValueError):m.load_plan(f)
    def test_all_49_windows_and_final_reference(self):
        for row in self.plan['windows']:
            self.now=m.parse(row['start_local'])+timedelta(seconds=1)
            self.assertEqual(self.c.step(),'WINDOW_VERIFIED')
            self.assertTrue(m.matches(self.io.rf,row))
            self.now=self.now+timedelta(minutes=45)
            self.assertEqual(self.c.step(),'MEASURED')
        self.assertEqual(len(self.io.measurements),49)
        self.now=m.parse(self.plan['windows'][-1]['end_local'])+timedelta(seconds=1)
        self.assertEqual(self.c.step(),'WINDOW_VERIFIED')
        self.assertEqual(self.c.step(),'FINISHED')
        self.assertEqual((self.io.rf['ap_f'],self.io.rf['sm_b']),(7000,20))
    def test_no_change_does_not_send_trial(self):
        previous=self.plan['windows'][-2]
        self.assertEqual((previous['frequency_mhz'],previous['bandwidth_mhz']),(7000,20))
        m.atomic(self.folder/'state.json',previous)
        self.now=m.parse(self.plan['windows'][-1]['start_local'])+timedelta(seconds=1)
        self.assertEqual(self.c.step(),'WINDOW_VERIFIED');self.assertEqual(self.io.writes,[])


if __name__=='__main__':unittest.main()
