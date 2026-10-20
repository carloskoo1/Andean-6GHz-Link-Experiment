"""Ensayo reproducible V4 sin radios: python3 -m prospective_28d.v4.rehearse."""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from prospective_28d.v2 import prospective_plan as plan
from .safety import Guard,Clock,Radio,Candidate,ScheduledProspective,Uncertain

EVIDENCE={'mode':'LAB_ONLY','original_closed':True,'original_timer_disabled':True,
          'stability_48h':True,'expert_conditions':True}

def recovery_case(root,fault):
    guard=Guard(root);guard.handover_lab(EVIDENCE)
    clock=Clock();radio=Radio(clock);candidate=Candidate(guard,radio,clock)
    radio.fault=fault
    try:candidate.switch((6475,40),'lab-incident')
    except Uncertain:pass
    outcomes=[candidate.recover(clock_trusted=True)]
    clock.advance(360);outcomes.append(candidate.recover(clock_trusted=True))
    if outcomes[-1]=='RESTORE_PENDING_RECHECK':
        clock.advance(360);outcomes.append(candidate.recover(clock_trusted=True))
    with guard.lease('prospective',recovery=True) as s:
        halted=s.data['review_required'];pending=s.data['pending'] is not None
    return {'fault':fault,'outcomes':outcomes,'final_simulated_rf':radio.current,
            'review_required':halted,'pending':pending,
            'write_operations':[c for c in radio.calls if isinstance(c,tuple)]}

def rehearse():
    with tempfile.TemporaryDirectory(prefix='luisita_v4_') as d:
        root=Path(d);guard=Guard(root/'calendar');guard.handover_lab(EVIDENCE)
        clock=Clock();radio=Radio(clock);candidate=Candidate(guard,radio,clock)
        scheduled=ScheduledProspective(plan.read_plan(),candidate)
        outcomes=[]
        for row in scheduled.rows:
            at=datetime.fromisoformat(row['start_local']);clock.now=at.timestamp()
            outcomes.append(scheduled.tick(at))
        return {'mode':'LAB_ONLY','live_enabled':False,'real_rf_changes':0,
                'calendar':{'slots':len(outcomes),'treatments':42,'reserves':7,
                            'committed':outcomes.count('LAB_COMMITTED'),'no_change':outcomes.count('LAB_NO_CHANGE'),
                            'final_simulated_rf':radio.current,'study_eligible':False},
                'recovery_cases':[recovery_case(root/f,f) for f in ('trial_before','trial_after','confirm_before','confirm_after')],
                'handover_evidence':'FICTITIOUS_FOR_TESTING_NOT_EXPERT_APPROVAL'}

if __name__=='__main__':print(json.dumps(rehearse(),indent=2))
