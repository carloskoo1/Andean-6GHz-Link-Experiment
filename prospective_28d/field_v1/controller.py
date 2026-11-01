#!/usr/bin/env python3
"""Versioned entrypoint of the installed unit; authorized commissioning is isolated."""
import sys,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2]
release=root/'prospective_28d/field_v3'
sys.path.insert(0,str(release))
program='commissioning.py' if (root/'prospective_runtime/COMMISSIONING_AUTH.json').exists() else 'controller.py'
runpy.run_path(str(release/program),run_name='__main__')
