"""Ensayo completo sin red: python3 -m prospective_28d.v3.rehearse."""
import contextlib
import copy
import io
import json
import tempfile
from datetime import datetime
from pathlib import Path
from campaign_orchestrator import load_config
from prospective_28d.v2 import prospective_plan as plan
from .adapter import LabAPI, LabOrchestrator, ProspectiveAdapter

ROOT = Path(__file__).resolve().parents[2]

def rehearse():
    p = plan.read_plan()
    with tempfile.TemporaryDirectory(prefix='luisita_lab_') as temp:
        c = copy.deepcopy(load_config(ROOT/'campaign_plan.template.json'))
        c['outputs']['directory'] = temp
        api = LabAPI()
        orch = LabOrchestrator(c,ROOT/'campaign_plan.template.json',api)
        adapter = ProspectiveAdapter(p,orch)
        with contextlib.redirect_stdout(io.StringIO()):
            results = [adapter.transition(row,datetime.fromisoformat(row['start_local'])) for row in adapter.rows]
        return {'mode':'LAB_REAL_ORCHESTRATOR_FAKE_RADIOS','transitions':len(results),
                'treatments':sum(r['phase']=='TREATMENT' for r in results),
                'reserves':sum(r['phase']=='RESERVE' for r in results),
                'confirmed_trials':api.calls.count(('finish',True)),
                'final_ap_simulated':api.props,'real_rf_changes':0,'live_enabled':False,
                'sm_rf_verified':False,'study_eligible':False}

if __name__=='__main__':
    print(json.dumps(rehearse(),indent=2))
