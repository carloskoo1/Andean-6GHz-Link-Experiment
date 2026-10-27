#!/usr/bin/env python3
import datetime as dt
import unittest
from prospective_plan import make_schedule
from prospective_simulator import FakeRadio, Simulation

START=dt.datetime.fromisoformat("2026-11-01T00:00:00-05:00")
class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.radio=FakeRadio()
        self.sim=Simulation(make_schedule(START),self.radio)
    def test_idempotency(self):
        self.assertEqual(self.sim.step(START),"SIMULATED_COMMIT")
        self.assertEqual(self.sim.step(START),"NO_OP_ALREADY_APPLIED")
        self.assertEqual(len(self.radio.history),1)
    def test_failure_blocks_following_transitions(self):
        self.radio.fail_next=True
        self.assertEqual(self.sim.step(START),"SAFE_ABORT")
        self.assertEqual(self.radio.current,"BASE_7000_20")
        self.assertEqual(self.sim.step(START+dt.timedelta(hours=12)),"BLOCKED")
    def test_reserve_no_rf_change(self):
        at=START+dt.timedelta(hours=72)
        self.assertEqual(self.sim.step(at),"RESERVE_NO_RF_CHANGE")
        self.assertEqual(self.radio.history,[])
    def test_all_cycles(self):
        for r in self.sim.rows:
            instant=dt.datetime.fromisoformat(r["start_local"])
            self.sim.step(instant)
        self.assertEqual(len(self.sim.confirmed),49)
        self.assertEqual(len(self.radio.history),42)
        self.assertEqual(self.radio.current,self.sim.rows[-2]["scenario_id"])
    def test_no_window(self):
        self.assertEqual(self.sim.step(START-dt.timedelta(seconds=1)),"NO_WINDOW")
if __name__=="__main__":
    unittest.main()
