# -*- coding: utf-8 -*-
"""
Test Suite for Batch 3: Usability, Synchronizations & UI Refinements (Edits 1 to 5)
"""
import re
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

def test_edit1_scatter_plot_dynamic_scaling():
    """Edit 1: Verify dynamic auto-scaling on scatter plot axes instead of hardcoded 350m2 / 25M EGP."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    assert "dynamicMaxArea" in content, "Must compute dynamicMaxArea"
    assert "dynamicMaxPrice" in content, "Must compute dynamicMaxPrice"
    assert "suggestedMax: dynamicMaxArea" in content, "Must use suggestedMax for X axis"
    assert "suggestedMax: dynamicMaxPrice" in content, "Must use suggestedMax for Y axis"

    # Ensure hardcoded max: 350 and max: 25 are not present in scatter chart configuration
    scatter_block_match = re.search(r"chartInstances\.scatter\s*=\s*new Chart\(ctxSc,\s*\{([\s\S]*?)\}\);", content)
    assert scatter_block_match, "Scatter plot instantiation must exist"
    scatter_code = scatter_block_match.group(1)
    assert "max: 350" not in scatter_code, "Scatter plot must not hardcode max: 350"
    assert "max: 25" not in scatter_code, "Scatter plot must not hardcode max: 25"


def test_edit2_single_table_render_pipeline():
    """Edit 2: Verify affordability calculation is decoupled and table renders only once per filter pass."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    # Verify calculateAffordabilityScore accepts skipRender parameter
    assert "function calculateAffordabilityScore(skipRender" in content, "calculateAffordabilityScore must accept skipRender parameter"

    # Verify applyFilters rendering sequence
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    assert apply_filters_match, "applyFilters function must exist"
    body = apply_filters_match.group(1)

    # Check that calculateAffordabilityScore(true) occurs before renderTable()
    afford_idx = body.find("calculateAffordabilityScore(true)")
    render_idx = body.find("renderTable()")
    assert afford_idx != -1, "calculateAffordabilityScore(true) must be called in applyFilters"
    assert render_idx != -1, "renderTable() must be called in applyFilters"
    assert afford_idx < render_idx, "calculateAffordabilityScore(true) must run BEFORE renderTable()"

    # Verify renderTable() is only called once in applyFilters
    assert body.count("renderTable()") == 1, "renderTable() must be called exactly once inside applyFilters()"


def test_edit3_segment_duel_filtered_records():
    """Edit 3: Verify updateDuel benchmarks against filteredRecords and is triggered by applyFilters."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    duel_match = re.search(r"function updateDuel\(\)\s*\{([\s\S]*?)\n\}", content)
    assert duel_match, "updateDuel function must exist"
    duel_body = duel_match.group(1)

    assert "sourceRecords" in duel_body, "updateDuel must define sourceRecords"
    assert "filteredRecords" in duel_body, "updateDuel must reference filteredRecords"

    # Verify applyFilters triggers updateDuel
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    body = apply_filters_match.group(1)
    assert "updateDuel()" in body, "updateDuel() must be invoked inside applyFilters()"


def test_edit4_checkbox_synchronization_and_reset():
    """Edit 4: Verify selectAllCheckbox synchronization in renderTable and selection clearing in resetFilters."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    # Verify renderTable synchronizes selectAllCheckbox
    render_match = re.search(r"function renderTable\(\)\s*\{([\s\S]*?)\n\}", content)
    assert render_match, "renderTable function must exist"
    render_body = render_match.group(1)
    assert "selectAllCheckbox" in render_body, "renderTable must synchronize selectAllCheckbox"
    assert "selAll.checked" in render_body, "renderTable must set selAll.checked based on page items"

    # Verify resetFilters clears selections
    reset_match = re.search(r"function resetFilters\(.*?\)\s*\{([\s\S]*?)\n\}", content)
    assert reset_match, "resetFilters function must exist"
    reset_body = reset_match.group(1)
    assert "selectedPropertyIndices.clear()" in reset_body, "resetFilters must clear selectedPropertyIndices"
    assert "compareCount" in reset_body, "resetFilters must reset compareCount display"


def test_edit5_launcher_synchronization():
    """Edit 5: Verify dual launchers (root and dashboard) are synchronized with candidate paths and Chrome auto-detection."""
    root_dash = BASE_DIR / "run_dashboard.py"
    sub_dash = BASE_DIR / "dashboard" / "run_dashboard.py"
    root_stream = BASE_DIR / "run_streamlit.py"
    sub_stream = BASE_DIR / "dashboard" / "run_streamlit.py"

    assert root_dash.exists(), "root run_dashboard.py must exist"
    assert sub_dash.exists(), "dashboard/run_dashboard.py must exist"
    assert root_stream.exists(), "root run_streamlit.py must exist"
    assert sub_stream.exists(), "dashboard/run_streamlit.py must exist"

    # Both dashboard launchers must scan candidates and support Chrome
    for dash_file in [root_dash, sub_dash]:
        c = dash_file.read_text(encoding="utf-8")
        assert "chrome_candidates" in c, f"{dash_file.name} must scan chrome_candidates"
        assert "candidates" in c, f"{dash_file.name} must search candidates"
        assert "index.html" in c, f"{dash_file.name} must target index.html"

    # Both streamlit launchers must scan candidate app.py locations
    for stream_file in [root_stream, sub_stream]:
        c = stream_file.read_text(encoding="utf-8")
        assert "candidates" in c, f"{stream_file.name} must search candidate paths for app.py"
        assert "streamlit" in c, f"{stream_file.name} must invoke streamlit"
