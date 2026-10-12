# -*- coding: utf-8 -*-
import sys
import subprocess
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "app.py",
        base_dir / "dashboard" / "app.py",
        base_dir.parent / "dashboard" / "app.py"
    ]
    target = None
    for cand in candidates:
        if cand.exists():
            target = cand
            break
    if not target:
        print("[ERROR] Streamlit 'app.py' not found.")
        sys.exit(1)

    print("=" * 68)
    print("  EGYPT REAL ESTATE FINANCING DECISION ENGINE")
    print("  Launching Streamlit Interactive Application...")
    print("=" * 68)
    print(f"  App Path : {target}")
    print("-" * 68)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(target),
        "--server.headless=false",
        "--theme.primaryColor=#2A9D8F",
        "--theme.backgroundColor=#F8F9FA",
        "--theme.secondaryBackgroundColor=#FFFFFF",
        "--theme.textColor=#1B2A4A"
    ]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nSession closed.")

if __name__ == "__main__":
    main()
