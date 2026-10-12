# -*- coding: utf-8 -*-
"""
Test Suite for Batch 1: Core System and Data Integrity Fixes (Bugs 1 to 5)
"""
import os
import json
import re
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

def test_bug1_purpose_filtering_non_zero():
    """Bug 1: Verify that both 'Residential Own' and 'Investment' classifications have valid non-zero counts."""
    data_json = BASE_DIR / "dashboard" / "data.json"
    assert data_json.exists(), "data.json must exist"
    with open(data_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    types = data.get("categoricals", {}).get("type", {})
    assert "Residential Own" in types, "Residential Own must be present in categoricals"
    assert "Investment / Capital Growth" in types, "Investment must be present in categoricals"
    assert types["Residential Own"] > 10000, f"Residential count should be substantial, got {types['Residential Own']}"
    assert types["Investment / Capital Growth"] > 3000, f"Investment count should be substantial, got {types['Investment / Capital Growth']}"

def test_bug2_secondary_launcher_chrome_support():
    """Bug 2: Verify dashboard/run_dashboard.py includes Google Chrome auto-detection logic."""
    launcher = BASE_DIR / "dashboard" / "run_dashboard.py"
    assert launcher.exists(), "dashboard/run_dashboard.py must exist"
    content = launcher.read_text(encoding="utf-8")
    assert "chrome_candidates" in content, "Must include chrome_candidates scanning"
    assert "subprocess.Popen" in content, "Must include subprocess Chrome launch"
    assert "chrome.exe" in content, "Must search for chrome.exe"

def test_bug3_launch_streamlit_portable_path():
    r"""Bug 3: Verify launch_streamlit.bat uses portable %~dp0 instead of hardcoded D:\RealEstateDashBoard."""
    batch_file = BASE_DIR / "launch_streamlit.bat"
    assert batch_file.exists(), "launch_streamlit.bat must exist"
    content = batch_file.read_text(encoding="utf-8")
    assert "%~dp0" in content, "launch_streamlit.bat must use %~dp0 for portability"
    assert "cd /d \"D:\\RealEstateDashBoard\"" not in content, r"Must not contain hardcoded D:\RealEstateDashBoard"

def test_bug4_dataset_count_harmonization():
    """Bug 4: Verify that dataset rows count, records count, and metadata are 100% harmonized at 33,401."""
    data_json = BASE_DIR / "dashboard" / "data.json"
    with open(data_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total = data["meta"]["dataset_rows"]
    assert total == 33401, f"Expected 33,401 rows in meta, got {total}"
    assert len(data["records"]) == 33401, f"Expected 33,401 records, got {len(data['records'])}"
    assert data["data_quality"]["total_records"] == 33401, f"Expected 33,401 in data_quality, got {data['data_quality']['total_records']}"

def test_bug5_readiness_and_purpose_record_slots():
    """Bug 5: Verify record index 6 contains genuine readiness tier and index 22 contains purpose."""
    data_json = BASE_DIR / "dashboard" / "data.json"
    with open(data_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    first_record = data["records"][0]
    assert len(first_record) == 23, f"Expected 23 items per record tuple, got {len(first_record)}"
    
    readiness = first_record[6]
    assert isinstance(readiness, str), "Record slot 6 must be string readiness tier"
    assert readiness != 2025.0 and readiness != "2025.0", "Record slot 6 must not be hardcoded 2025.0"
    assert any(tier in readiness for tier in ["Ready to Move", "Immediate Delivery", "Off-Plan"]), f"Unexpected readiness: {readiness}"
    
    purpose = first_record[22]
    assert purpose in ["Residential Own", "Investment"], f"Record slot 22 must be valid purpose, got {purpose}"
