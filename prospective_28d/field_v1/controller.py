#!/usr/bin/env python3
"""Compatibility entry point for the existing systemd unit; active release field_v2."""
import sys,runpy
from pathlib import Path
release=Path(__file__).resolve().parent.parent/'field_v2'
sys.path.insert(0,str(release))
runpy.run_path(str(release/'controller.py'),run_name='__main__')
