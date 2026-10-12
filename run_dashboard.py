# -*- coding: utf-8 -*-
import sys
import webbrowser
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "index.html",
        base_dir / "dashboard" / "index.html",
    ]
    target = None
    for cand in candidates:
        if cand.exists():
            target = cand
            break
    if not target:
        print("[ERROR] Dashboard file 'index.html' not found.")
        sys.exit(1)

    print("=" * 68)
    print("  EGYPT REAL ESTATE INTELLIGENCE PLATFORM (v1)")
    print("  Interactive Geospatial Heatmap & Executive Analytics")
    print("=" * 68)
    print(f"  Target File : {target.name}")
    print(f"  URI         : {target.as_uri()}")
    print("-" * 68)

    chrome_candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    for chrome_path in chrome_candidates:
        if chrome_path.is_file():
            print(f"  Auto-launching in Google Chrome: {chrome_path}")
            try:
                subprocess.Popen([str(chrome_path), target.as_uri()])
                return
            except Exception as err:
                print(f"  [WARN] Chrome launch error: {err}")

    webbrowser.open(target.as_uri())

if __name__ == '__main__':
    main()
