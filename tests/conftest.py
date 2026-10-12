# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Central test configuration: Ensure project folders are on sys.path
root_dir = Path(__file__).resolve().parent.parent
dashboard_dir = root_dir / "dashboard"
model_dir = root_dir / "model"
data_scripts_dir = root_dir / "data_analysis" / "scripts"

for p in [dashboard_dir, model_dir, data_scripts_dir, root_dir]:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))
