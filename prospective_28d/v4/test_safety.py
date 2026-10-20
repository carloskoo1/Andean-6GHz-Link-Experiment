import contextlib
import copy
import io
import json
import multiprocessing as mp
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
from campaign_orchestrator import load_config
from prospective_28d.v2 import prospective_plan as plan
from prospective_28d.v4.safety import (Guard,Blocked,Busy,Uncertain,Clock,Radio,Candidate,
                                      ScheduledProspective,OriginalRunner,run_original_lab)
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE={'mode':'LAB_ONLY','original_closed':True,'original_timer_disabled':True,'stability_48h':True,'expert_conditions':True}

def hold(directory,role,connection,release):
    try:
        with Guard(directory).lease(role):
            connection.send('locked')
            if not release.wait(5):raise RuntimeError('timeout laboratorio')
    finally:connection.close()

def crash(directory):
    with Guard(directory).lease('prospective') as s:
        s.data['pending']={'id':'crash','before':[7000,20],'target':[6475,40],
                           'stage':'TRIAL_INTENT','started':0,'not_before':360}
        s.save('CRASH_INTENT',{'lab':True})
        os._exit(17)

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.g=Guard(self.base/'guard')
        self.g.handover_lab(EVIDENCE)
        self.clock=Clock();self.radio=Radio(self.clock);self.c=Candidate(self.g,self.radio,self.clock)
    def state(self):
        with self.g.lease('prospective',recovery=True) as s:return copy.deepcopy(s.data)
    def failed(self,fault):
        self.radio.fault=fault
        with self.assertRaises(Uncertain):self.c.switch((6475,40),'incident')
    def writes(self):return [v for v in self.radio.calls if isinstance(v,tuple)]
    def test_normal_commit(self):
        self.assertEqual(self.c.switch((6475,40),'a'),'LAB_COMMITTED')
        self.assertIsNone(self.state()['pending']);self.assertEqual(self.radio.current,(6475,40))
    def test_no_change(self):
        self.assertEqual(self.c.switch((7000,20),'a'),'LAB_NO_CHANGE');self.assertEqual(self.writes(),[])
    def test_duplicate(self):
        self.c.switch((6475,40),'a');before=self.writes()
        self.assertEqual(self.c.switch((6475,40),'a'),'ALREADY_RECORDED');self.assertEqual(before,self.writes())
    def test_id_reuse_rejected(self):
        self.c.switch((6475,40),'a')
        with self.assertRaises(Blocked):self.c.switch((6655,20),'a')
    def test_trial_ack_loss_waits_without_cancel(self):
        self.failed('trial_after');before=self.writes()
        self.assertEqual(self.c.recover(clock_trusted=True),'WAIT_NO_WRITES');self.assertEqual(before,self.writes())
        self.assertNotIn(('finish',False),before)
    def test_trial_not_accepted_recovers_previous(self):
        self.failed('trial_before');self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED');self.assertEqual(len(self.writes()),1)
    def test_trial_accepted_autoexpires_simulated(self):
        self.failed('trial_after');self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED');self.assertEqual(self.radio.current,(7000,20))
    def test_confirm_not_accepted_autoexpires(self):
        self.failed('confirm_before');self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_confirm_accepted_ack_lost_restores_once(self):
        self.failed('confirm_after');self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RESTORE_PENDING_RECHECK')
        self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
        self.assertEqual(self.radio.current,(7000,20));self.assertEqual(self.writes().count(('trial',(7000,20))),1)
    def test_restore_ack_lost_is_reconciled(self):
        self.failed('confirm_after');self.clock.advance(360);self.radio.fault='confirm_after'
        self.assertEqual(self.c.recover(clock_trusted=True),'RESTORE_PENDING_RECHECK');self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_restore_trial_ack_lost_does_not_loop(self):
        self.failed('confirm_after');self.clock.advance(360);self.radio.fault='trial_after'
        self.c.recover(clock_trusted=True);self.clock.advance(360);before=self.writes()
        self.assertEqual(self.c.recover(clock_trusted=True),'MANUAL_REQUIRED');self.assertEqual(before,self.writes())
    def test_unknown_rf_requires_manual_without_write(self):
        self.failed('confirm_after');self.clock.advance(360);self.radio.current=(6655,40);before=self.writes()
        self.assertEqual(self.c.recover(clock_trusted=True),'MANUAL_REQUIRED');self.assertEqual(before,self.writes())
    def test_unreachable_recovery(self):
        self.failed('trial_after');self.clock.advance(360);self.radio.reachable=False;before=self.writes()
        self.assertEqual(self.c.recover(clock_trusted=True),'MANUAL_REQUIRED');self.assertEqual(before,self.writes())
    def test_untrusted_clock(self):
        self.failed('trial_after')
        with self.assertRaises(Blocked):self.c.recover(clock_trusted=False)
    def test_clock_rollback(self):
        self.failed('trial_after');self.clock.now=-1
        with self.assertRaises(Blocked):self.c.recover(clock_trusted=True)
    def test_review_required_after_recovery(self):
        self.failed('trial_after');self.clock.advance(360);self.c.recover(clock_trusted=True)
        with self.assertRaises(Blocked):self.c.switch((6475,40),'b')
        self.g.acknowledge_lab('prospective','incident')
        self.assertFalse(self.state()['review_required'])
    def test_cannot_ack_pending(self):
        self.failed('trial_after')
        with self.assertRaises(Blocked):self.g.acknowledge_lab('prospective','incident')
    def test_wrong_incident_ack(self):
        self.failed('trial_after');self.clock.advance(360);self.c.recover(clock_trusted=True)
        with self.assertRaises(Blocked):self.g.acknowledge_lab('prospective','other')
    def test_owner_persists_new_guard(self):
        with self.assertRaises(Blocked):
            with Guard(self.base/'guard').lease('original'):pass
    def test_original_owns_initially(self):
        other=Guard(self.base/'other')
        with self.assertRaises(Blocked):
            with other.lease('prospective'):pass
    def test_handover_requires_all_evidence(self):
        other=Guard(self.base/'other')
        for key in ('original_closed','original_timer_disabled','stability_48h','expert_conditions'):
            with self.subTest(key=key),self.assertRaises(Blocked):other.handover_lab({**EVIDENCE,key:False})
    def test_handover_pending_rejected(self):
        other=Guard(self.base/'other')
        with other.lease('original') as s:s.data['pending']={'id':'x'};s.save('LAB_INTENT',{})
        with self.assertRaises(Blocked):other.handover_lab(EVIDENCE)
    def test_original_wrapper_uses_existing_executor_fake_runner(self):
        guard=Guard(self.base/'original_guard');runner=OriginalRunner()
        cfg=load_config(ROOT/'campaign_plan.template.json');cfg['outputs']['directory']=str(self.base/'original_runtime')
        path=self.base/'config.json';path.write_text(json.dumps(cfg))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_original_lab(path,datetime.fromisoformat('2026-09-16T00:01:00-05:00'),guard,runner),0)
        self.assertEqual(len(runner.calls),1)
        guard.handover_lab(EVIDENCE)
        with self.assertRaises(Blocked):run_original_lab(path,datetime.fromisoformat('2026-09-16T00:01:00-05:00'),guard,runner)
        self.assertEqual(len(runner.calls),1)
    def contend(self,role,directory,attempt):
        ctx=mp.get_context('spawn');recv,send=ctx.Pipe(duplex=False);release=ctx.Event()
        p=ctx.Process(target=hold,args=(str(directory),role,send,release));p.start();send.close()
        try:
            self.assertTrue(recv.poll(5));self.assertEqual(recv.recv(),'locked')
            with self.assertRaises(Busy):attempt()
        finally:
            release.set();p.join(5)
            if p.is_alive():p.terminate();p.join()
            recv.close()
        self.assertEqual(p.exitcode,0)
    def test_two_processes_original_blocks_prospective(self):
        g=Guard(self.base/'first');c=Candidate(g,self.radio,self.clock)
        self.contend('original',g.directory,lambda:c.switch((6475,40),'x'))
        self.assertEqual(self.writes(),[])
    def test_two_processes_prospective_blocks_original(self):
        self.contend('prospective',self.g.directory,lambda:run_original_lab(self.base/'absent.json',datetime.now().astimezone(),self.g,OriginalRunner()))
    def test_killed_process_releases_lock_but_keeps_intent(self):
        ctx=mp.get_context('spawn');p=ctx.Process(target=crash,args=(str(self.g.directory),));p.start();p.join(5)
        if p.is_alive():p.terminate();p.join();self.fail('Proceso de ensayo no terminó')
        self.assertEqual(p.exitcode,17)
        with self.assertRaises(Blocked):self.c.switch((6475,40),'next')
        self.clock.advance(360);self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_live_rejected(self):
        with self.assertRaises(Blocked):Guard(self.base/'live',live=True)
        with self.assertRaises(Blocked):Candidate(self.g,self.radio,self.clock,live=True)
    def test_full_calendar_shared_guard(self):
        scheduled=ScheduledProspective(plan.read_plan(),self.c)
        with patch('socket.socket',side_effect=AssertionError('NO NETWORK')):
            for row in scheduled.rows:
                at=datetime.fromisoformat(row['start_local']);self.clock.now=at.timestamp()
                self.assertIn(scheduled.tick(at),('LAB_COMMITTED','LAB_NO_CHANGE'))
        self.assertEqual(self.state()['last_sequence'],49);self.assertEqual(self.radio.current,(7000,20))
    def test_failed_schedule_stays_halted_after_recovery_ack(self):
        scheduled=ScheduledProspective(plan.read_plan(),self.c);at=datetime.fromisoformat(scheduled.rows[0]['start_local'])
        self.clock.now=at.timestamp();self.radio.fault='trial_after'
        with self.assertRaises(Uncertain):scheduled.tick(at)
        self.clock.advance(360);self.c.recover(clock_trusted=True);self.g.acknowledge_lab('prospective','prospective-1')
        self.clock.now=at.timestamp()
        with self.assertRaises(Blocked):scheduled.tick(at)
    def test_schedule_missed_blocks(self):
        scheduled=ScheduledProspective(plan.read_plan(),self.c);at=datetime.fromisoformat(scheduled.rows[1]['start_local']);self.clock.now=at.timestamp()
        with self.assertRaises(Blocked):scheduled.tick(at)
        self.assertTrue(self.state()['schedule_halted']);self.assertEqual(self.writes(),[])
    def test_delayed_trial_does_not_confirm_without_margin(self):
        self.radio.trial_delay_seconds=250
        with self.assertRaises(Uncertain):self.c.switch((6475,40),'slow')
        self.assertNotIn(('finish',True),self.writes())
        self.assertEqual(self.state()['pending']['not_before'],610)
        self.assertEqual(self.c.recover(clock_trusted=True),'WAIT_NO_WRITES')
        self.clock.advance(360)
        self.assertEqual(self.c.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_readback_disagreement_no_initial_write(self):
        with patch.object(self.radio,'read',side_effect=[(7000,20),(6475,40),(7000,20)]):
            with self.assertRaises(Uncertain):self.c.switch((6475,40),'unstable')
        self.assertEqual(self.writes(),[])
    def test_invalid_initial_rf_no_write(self):
        self.radio.current=(1234,20)
        with self.assertRaises(Blocked):self.c.switch((6475,40),'bad')
        self.assertEqual(self.writes(),[])
    def test_recovery_requires_explicit_trusted_clock(self):
        self.failed('trial_after');self.clock.advance(360)
        with self.assertRaises(Blocked):self.c.recover()
    def test_restart_recovery_uses_durable_snapshot(self):
        self.failed('confirm_after');self.clock.advance(360)
        restarted=Candidate(Guard(self.g.directory),self.radio,self.clock)
        self.assertEqual(restarted.recover(clock_trusted=True),'RESTORE_PENDING_RECHECK')
        self.clock.advance(360)
        self.assertEqual(restarted.recover(clock_trusted=True),'RECOVERED_PREVIOUS_REVIEW_REQUIRED')
    def test_corrupt_journal_fails_closed(self):
        with sqlite3.connect(self.g.directory/'guard.sqlite') as db:db.execute("UPDATE state SET data='bad json'")
        with self.assertRaises(Exception):self.c.switch((6475,40),'corrupt')
        self.assertEqual(self.writes(),[])
    def test_schedule_clock_mismatch(self):
        scheduled=ScheduledProspective(plan.read_plan(),self.c)
        with self.assertRaises(Blocked):scheduled.tick(datetime.fromisoformat(scheduled.rows[0]['start_local']))

if __name__=='__main__':unittest.main()
