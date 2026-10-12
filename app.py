# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Add dashboard folder and root to sys.path
root_dir = Path(__file__).resolve().parent
dash_dir = root_dir / "dashboard"
model_dir = root_dir / "model"

for p in [dash_dir, root_dir, model_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Forward execution to dashboard/app.py
target_app = dash_dir / "app.py"
with open(target_app, encoding="utf-8") as f:
    code = compile(f.read(), str(target_app), "exec")
    exec(code)
