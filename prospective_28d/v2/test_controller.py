import copy
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
import prospective_plan as p
from controller_sim import Halt, SimulatedPair, tick, lock

class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name); self.p=p.read_plan(); self.rows=p.generate(self.p)
        self.now=datetime.fromisoformat(self.rows[0]['start_local']); self.r=SimulatedPair()
    def run_tick(self, **kw):
        return tick(self.p,self.rows,kw.pop('now',self.now),self.d,kw.pop('radio',self.r),**kw)
    def test_full_campaign(self):
        for row in self.rows:
            result=self.run_tick(now=datetime.fromisoformat(row['start_local']))
            self.assertEqual(result['status'],'SIMULATED_VERIFIED')
            self.assertFalse(result['study_eligible'])
        self.assertEqual(self.r.calls,49)
    def test_duplicate_restart(self):
        self.run_tick(); r=SimulatedPair(); self.run_tick(radio=r); self.assertEqual(r.calls,0)
    def test_partial_failure_blocks_retry(self):
        r=SimulatedPair('partial')
        with self.assertRaises(Halt): self.run_tick(radio=r)
        with self.assertRaises(Halt): self.run_tick()
        self.assertEqual(self.r.calls,0)
    def test_unreachable(self):
        r=SimulatedPair('unreachable')
        with self.assertRaises(Halt): self.run_tick(radio=r)
        self.assertEqual(r.calls,0)
    def test_unlinked(self):
        with self.assertRaises(Halt): self.run_tick(radio=SimulatedPair('unlinked'))
        self.assertEqual(self.r.calls,0)
    def test_late(self):
        with self.assertRaises(Halt): self.run_tick(now=self.now+timedelta(seconds=61))
        self.assertEqual(self.r.calls,0)
    def test_missed_slot(self):
        with self.assertRaises(Halt): self.run_tick(now=self.now+timedelta(hours=12))
    def test_crash_intent(self):
        self.run_tick()
        with sqlite3.connect(self.d/'events.sqlite') as db: db.execute("UPDATE events SET status='INTENT'")
        with self.assertRaises(Halt): self.run_tick()
        self.assertEqual(self.r.calls,1)
    def test_lock(self):
        with lock(self.d/'controller.lock'):
            with self.assertRaises(Halt): self.run_tick()
    def test_naive_clock(self):
        with self.assertRaises(Halt): self.run_tick(now=self.now.replace(tzinfo=None))
    def test_before_start(self):
        self.assertEqual(self.run_tick(now=self.now-timedelta(seconds=1))['status'],'WAITING')
    def test_end_exclusive(self):
        self.assertEqual(self.run_tick(now=datetime.fromisoformat(self.rows[-1]['end_local']))['status'],'FINISHED_NO_RF')
        self.assertEqual(self.r.calls,0)
    def test_tampered_frequency(self):
        self.rows[0]['frequency_mhz']=1234
        with self.assertRaises(Halt): self.run_tick()
    def test_changed_plan(self):
        self.run_tick(); self.p['permutation_seed']+=1; self.rows=p.generate(self.p)
        with self.assertRaises(Halt): self.run_tick()
    def test_not_real_adapter(self):
        with self.assertRaises(Halt): self.run_tick(radio=object())
    def test_settle_overrun(self):
        with self.assertRaises(Halt): self.run_tick(settle_seconds=43200)
    def test_invalid_midday_start(self):
        self.p['proposed_start_local']='2026-11-01T12:00:00-05:00'
        with self.assertRaises(ValueError): p.generate(self.p)
    def test_duplicate_levels(self):
        self.p['frequency_levels_mhz'].append(7000)
        with self.assertRaises(ValueError): p.generate(self.p)
    def test_reference_changed(self):
        self.p['reference_configuration']['bandwidth_mhz']=40
        with self.assertRaises(ValueError): p.generate(self.p)
    def test_empty_preconditions(self):
        self.p['preconditions']={}
        with self.assertRaises(ValueError): p.generate(self.p)

if __name__=='__main__': unittest.main()
