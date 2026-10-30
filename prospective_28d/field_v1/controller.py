#!/usr/bin/env python3
"""Serial, fail-closed field controller. No retries of ambiguous RF writes."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / 'prospective_runtime'


def instant():
    return datetime.now(timezone.utc)


def parse(s):
    return datetime.fromisoformat(s)


def atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    with temp.open('w') as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def event(folder, name, **detail):
    folder.mkdir(parents=True, exist_ok=True)
    row = dict(timestamp_utc=instant().isoformat(), event=name, **detail)
    with (folder / 'events.jsonl').open('a') as f:
        f.write(json.dumps(row) + '\n')
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps(row), flush=True)


def verify_manifest(manifest):
    for name, expected in manifest.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Frozen dependency changed: ' + name)


def load_plan(path):
    p = json.loads(path.read_text())
    rows = p['windows']
    if len(rows) != 49:
        raise ValueError('49 windows required')
    previous = None
    counts = {}
    for i, row in enumerate(rows):
        start, end = parse(row['start_local']), parse(row['end_local'])
        if start.utcoffset() != timedelta(hours=-5) or start.minute or start.second or start.hour not in (0, 12):
            raise ValueError('Civil half-day boundary required')
        if previous is not None and start != previous:
            raise ValueError('Non-contiguous calendar')
        previous = end
        reserve = i % 7 == 6
        if row['phase'] != ('RESERVE' if reserve else 'PROSPECTIVE'):
            raise ValueError('Wrong phase order')
        if end - start != timedelta(hours=24 if reserve else 12):
            raise ValueError('Wrong exposure length')
        pair = (row['frequency_mhz'], row['bandwidth_mhz'])
        if reserve:
            if pair != (7000, 20):
                raise ValueError('Reserve must use reference')
        elif pair not in {(6475,20),(6475,40),(6655,20),(6655,40),(7000,20),(7000,40)}:
            raise ValueError('Invalid RF target')
        else:
            counts[pair] = counts.get(pair, 0) + 1
    if set(counts.values()) != {7} or len(counts) != 6:
        raise ValueError('Unbalanced treatment counts')
    for c in range(7):
        if len({(r['frequency_mhz'],r['bandwidth_mhz']) for r in rows[c*7:c*7+6]}) != 6:
            raise ValueError('Cycle is not a complete factorial')
    if p['tcp'] != {'duration_seconds':8,'omit_seconds':1,'parallel_streams':1,'interval_minutes':15}:
        raise ValueError('Unapproved TCP profile')
    return p


def target(plan, now):
    for row in plan['windows']:
        if parse(row['start_local']) <= now < parse(row['end_local']):
            return row
    if now >= parse(plan['windows'][-1]['end_local']):
        return dict(segment_id='FINAL_REFERENCE',phase='FINAL_REFERENCE',frequency_mhz=7000,bandwidth_mhz=20,
                    start_local=plan['windows'][-1]['end_local'])
    return None


def matches(readback, row):
    return (readback['ap_f'],readback['ap_b'],readback['sm_f'],readback['sm_b']) == (
        row['frequency_mhz'],row['bandwidth_mhz'],row['frequency_mhz'],row['bandwidth_mhz'])


class Controller:
    def __init__(self, plan, backend, folder=RUNTIME, clock=instant):
        self.plan, self.io, self.folder, self.clock = plan, backend, Path(folder), clock

    def step(self):
        f = self.folder
        f.mkdir(parents=True,exist_ok=True)
        if (f/'HALT.json').exists():
            return 'HALTED'
        if (f/'PENDING.json').exists():
            atomic(f/'HALT.json',{'reason':'Interrupted durable intent; reconcile manually','at':self.clock().isoformat()})
            return 'HALTED'
        now = self.clock()
        row = target(self.plan, now)
        if row is None:
            return 'WAITING_START'
        state = json.loads((f/'state.json').read_text()) if (f/'state.json').exists() else {}
        if state.get('segment_id') != row['segment_id']:
            if (now-parse(row['start_local'])).total_seconds() > 600:
                atomic(f/'HALT.json',{'reason':'Missed window start by >600 seconds','segment':row['segment_id']})
                event(f,'MISSED_WINDOW_HALT',segment=row['segment_id'])
                return 'HALTED'
            self.io.precheck()
            before = self.io.readback()
            if state and not matches(before,state):
                raise RuntimeError('Unexpected current RF; no automatic overwrite')
            if not state and not matches(before,dict(frequency_mhz=7000,bandwidth_mhz=20)):
                raise RuntimeError('Initial reference is not 7000/20')
            # Any exception or crash after this point blocks all subsequent RF changes.
            atomic(f/'PENDING.json',{'row':row,'before':before,'created':self.clock().isoformat()})
            event(f,'WINDOW_INTENT',row=row,before=before)
            changed = not matches(before,row)
            if changed:
                self.io.trial(row)
                event(f,'TRIAL_ACK',segment=row['segment_id'])
                self.io.wait_target(row, deadline_seconds=150)
                self.io.confirm()
                event(f,'CONFIRM_ACK',segment=row['segment_id'])
                self.io.wait_target(row, deadline_seconds=120)
            if not matches(self.io.readback(),row):
                raise RuntimeError('Final dual readback mismatch')
            verified = self.clock()
            state = dict(row,verified_at=verified.isoformat(),analysis_start=(verified+timedelta(seconds=1800)).isoformat(),
                         changed=changed,last_measurement_slot=None)
            atomic(f/'state.json',state)
            event(f,'WINDOW_VERIFIED',state=state)
            (f/'PENDING.json').unlink()
            return 'WINDOW_VERIFIED'
        if row['phase'] == 'FINAL_REFERENCE':
            return 'FINISHED'
        if now < parse(state['analysis_start']):
            return 'SETTLING'
        # Fixed civil quarter-hour slots. Never replay missed opportunities.
        if now.minute % 15 != 0 or now.second > 90 or (parse(row['end_local'])-now).total_seconds() < 180:
            return 'MONITORING'
        slot=now.isoformat()[:16]
        if state.get('last_measurement_slot') == slot:
            return 'ALREADY_MEASURED'
        state['last_measurement_slot']=slot
        atomic(f/'state.json',state)  # Mark before launch: no duplicate load after restart.
        event(f,'MEASUREMENT_OPPORTUNITY',segment=row['segment_id'],phase=row['phase'],slot=slot)
        if not matches(self.io.readback(),row):
            event(f,'MEASUREMENT_SKIPPED_RF',segment=row['segment_id'])
            return 'RF_UNVERIFIED'
        self.io.measure(row)
        event(f,'MEASUREMENT_COMPLETE',segment=row['segment_id'],phase=row['phase'])
        return 'MEASURED'


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['validate','preflight','tick'])
    args=ap.parse_args()
    plan=load_plan(HERE/'plan.json')
    if args.action == 'validate':
        print('Calendar/profile validated; no RF access')
        return
    verify_manifest(json.loads((HERE/'freeze.json').read_text()))
    from backend import Backend
    io=Backend(plan)
    if args.action == 'preflight':
        try:
            io.precheck()
            readback=io.readback()
            if not matches(readback,dict(frequency_mhz=7000,bandwidth_mhz=20)):
                raise RuntimeError('Pre-install reference is not 7000/20 at both radios')
            print(json.dumps(readback));return
        finally:
            io.close()
    if not (RUNTIME/'ENABLED.json').exists():
        raise RuntimeError('Field deployment is not enabled')
    with (RUNTIME/'link.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return
        try:
            try:
                print(Controller(plan,io).step(),flush=True)
            except Exception as exc:
                event(RUNTIME,'CONTROLLER_ERROR',error=str(exc))
                if (RUNTIME/'PENDING.json').exists():
                    atomic(RUNTIME/'HALT.json',{'reason':str(exc),'at':instant().isoformat()})
                raise
        finally:
            io.close()


if __name__=='__main__':
    main()
