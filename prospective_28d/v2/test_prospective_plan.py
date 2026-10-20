import json
import tempfile
import unittest
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
import prospective_plan as plan

class TestProspectivePlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = plan.read_plan()
        cls.rows = plan.generate(cls.p)

    def test_plan_is_locked_draft(self):
        self.assertEqual(self.p['status'], 'DRAFT_NOT_AUTHORIZED')
        self.assertTrue(all(v is False for v in self.p['preconditions'].values()))

    def test_49_rows(self):
        self.assertEqual(len(self.rows), 49)

    def test_42_exposures_and_seven_reserves(self):
        self.assertEqual(Counter(r['phase'] for r in self.rows),{'TREATMENT':42,'RESERVE':7})

    def test_each_condition_seven_times(self):
        cnt=Counter(r['scenario_id'] for r in self.rows if r['phase']=='TREATMENT')
        self.assertEqual(set(cnt.values()), {7})
        self.assertEqual(len(cnt),6)

    def test_no_gaps_or_overlaps(self):
        self.assertTrue(plan.validate_schedule(self.p,self.rows))

    def test_exact_28_days(self):
        self.assertEqual(datetime.fromisoformat(self.rows[-1]['end_local'])-datetime.fromisoformat(self.rows[0]['start_local']),timedelta(days=28))

    def test_date_start_end(self):
        self.assertEqual(self.rows[0]['start_local'],'2026-11-01T00:00:00-05:00')
        self.assertEqual(self.rows[-1]['end_local'],'2026-11-29T00:00:00-05:00')

    def test_each_scenario_each_slot_in_first_six_cycles(self):
        for sid in set(r['scenario_id'] for r in self.rows if r['phase']=='TREATMENT'):
            slots={r['slot'] for r in self.rows if r['phase']=='TREATMENT' and r['cycle'] <= 6 and r['scenario_id']==sid}
            self.assertEqual(slots,{1,2,3,4,5,6})

    def test_day_night_balanced_first_six(self):
        for sid in set(r['scenario_id'] for r in self.rows if r['phase']=='TREATMENT'):
            v=Counter(r['daypart'] for r in self.rows if r['phase']=='TREATMENT' and r['cycle']<=6 and r['scenario_id']==sid)
            self.assertEqual(v,{'DAY':3,'NIGHT':3})

    def test_simulation_failures_do_not_actuate(self):
        state, counts=plan.simulate(self.rows, failure_sequence=9)
        self.assertIn((9,'SIMULATED_FAILURE_NEEDS_OPERATOR'),state)
        self.assertEqual(sum(counts.values()),41)

    def test_simulation_reserve_has_no_actuation(self):
        states,_=plan.simulate(self.rows)
        self.assertEqual(sum(v=='REFERENCE_REQUEST_PLANNED_NOT_EXECUTED' for _,v in states),7)

    def test_invalid_time_zone_is_rejected(self):
        p={**self.p, 'timezone':'UTC'}
        with self.assertRaises(ValueError):plan.validate_plan(p)

    def test_approval_not_falsified(self):
        p={**self.p, 'preconditions':{**self.p['preconditions'],'explicit_operator_authorization':True}}
        with self.assertRaises(ValueError):plan.validate_plan(p)

    def test_inconsistent_duration_rejected(self):
        p={**self.p, 'slot_hours':13}
        with self.assertRaises(ValueError):plan.validate_plan(p)

    def test_deterministic_repeatable(self):
        self.assertEqual(plan.generate(self.p),plan.generate(self.p))

if __name__=='__main__':unittest.main(verbosity=2)
