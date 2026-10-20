"""Punto único de ensayo: python3 -m prospective_28d.v5.rehearse. Sin red."""
import copy
import json
import tempfile
from datetime import datetime,timedelta
from pathlib import Path
from prospective_28d.v2 import prospective_plan as planner
from prospective_28d.v4.safety import Guard,Clock,Uncertain
from .executor import UnifiedExecutor,SimulatedLuci

EVIDENCE={'mode':'LAB_ONLY','original_closed':True,'original_timer_disabled':True,
          'stability_48h':True,'expert_conditions':True}

def instance(root):
    p=planner.read_plan();clock=Clock(datetime.fromisoformat(p['proposed_start_local']).timestamp())
    guard=Guard(root);guard.handover_lab(EVIDENCE);server=SimulatedLuci(clock)
    return UnifiedExecutor(p,guard,server,clock)

def rehearse():
    with tempfile.TemporaryDirectory(prefix='luisita_v5_') as directory:
        root=Path(directory);e=instance(root/'calendar');timeline=[];examples=[]
        for row in e.rows:
            at=datetime.fromisoformat(row['start_local']);e.clock.now=at.timestamp()
            w=e.tick(at);timeline.append(w)
            if row['sequence']==1:
                verified=datetime.fromisoformat(w['verified_at']);eligible=datetime.fromisoformat(w['analysis_start'])
                end=datetime.fromisoformat(w['scheduled_end'])
                cases=[('during_transition',at,at+timedelta(seconds=1),True,w['target']),
                       ('settling',verified,verified+timedelta(seconds=1),True,w['target']),
                       ('qc_pending',eligible,eligible+timedelta(seconds=20),False,w['target']),
                       ('rf_unknown',eligible,eligible+timedelta(seconds=20),True,None),
                       ('valid_lab_only',eligible,eligible+timedelta(seconds=20),True,w['target']),
                       ('crosses_end',end-timedelta(seconds=5),end+timedelta(seconds=5),True,w['target'])]
                for name,a,b,qc,rf in cases:
                    examples.append({'case':name,'start':a.isoformat(),'end':b.isoformat(),
                                     **e.classify_interval(a,b,qc_passed=qc,observed_target=rf)})
            if row['phase']=='RESERVE' and not any(x['case']=='reserve' for x in examples):
                a=datetime.fromisoformat(w['analysis_start'])
                examples.append({'case':'reserve','start':a.isoformat(),'end':(a+timedelta(seconds=20)).isoformat(),
                                 **e.classify_interval(a,a+timedelta(seconds=20),qc_passed=True,observed_target=w['target'])})
        faults=[]
        for fault in ('trial_before','trial_after','confirm_before','confirm_after'):
            f=instance(root/fault);f.server.radio.fault=fault
            try:f.tick(datetime.fromtimestamp(f.clock.now,datetime.fromisoformat(f.plan['proposed_start_local']).tzinfo))
            except Uncertain:pass
            outcomes=[f.recover(clock_trusted=True)];f.clock.advance(360)
            outcomes.append(f.recover(clock_trusted=True))
            if outcomes[-1]=='RESTORE_PENDING_RECHECK':
                f.clock.advance(360);outcomes.append(f.recover(clock_trusted=True))
            with f.guard.lease('prospective',recovery=True) as s:
                window=copy.deepcopy(s.data['v5_windows']['1'])
                halted=s.data['schedule_halted'];review=s.data['review_required']
            faults.append({'fault':fault,'recovery':outcomes,'window':window,
                           'calendar_halted':halted,'review_required':review,
                           'final_simulated_rf':f.server.radio.current})
        return {'mode':'LAB_ONLY','live_enabled':False,'cu01_contacted':False,'real_rf_changes':0,
                'tcp_executions':0,'tcp_status':e.tcp['status'],'active_profile_id':e.tcp['active_profile_id'],
                'slots':49,'treatments':42,'reserves':7,'timeline':timeline,
                'classification_examples':examples,'incident_recovery_examples':faults,
                'handover_evidence':'FICTITIOUS_FOR_TESTS_ONLY_NOT_EXPERT_APPROVAL'}

if __name__=='__main__':print(json.dumps(rehearse(),indent=2))
