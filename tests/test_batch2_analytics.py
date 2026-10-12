# -*- coding: utf-8 -*-
"""
Test Suite for Batch 2: Analytics, Charts & Map Engine Fixes (Bugs 6 to 10)
"""
import os
import re
import sys
from pathlib import Path
import pytest
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

def test_bug6_ghost_canvas_and_collinearity_modal():
    """Bug 6: Verify elimination of ghost chartTemporal canvas and presence of active correlation modal."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    assert html_file.exists(), "index.html must exist"
    content = html_file.read_text(encoding="utf-8")

    # Confirm ghost canvas and its context reference are completely removed
    assert "chartTemporal" not in content, "chartTemporal canvas and references must be removed"
    assert "chartInstances.temp" not in content, "chartInstances.temp must be removed"

    # Confirm correlation modal and handlers exist
    assert 'id="correlationModal"' in content, "correlationModal overlay must exist in DOM"
    assert "openCorrelationModal" in content, "openCorrelationModal JS function must be defined"
    assert "closeCorrelationModal" in content, "closeCorrelationModal JS function must be defined"
    assert "renderCorrelationHeatmap" in content, "renderCorrelationHeatmap JS function must be defined"


def test_bug7_sort_preservation_in_apply_filters():
    """Bug 7: Verify that applySortToFilteredRecords preserves active column sort order inside applyFilters."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    assert "function applySortToFilteredRecords" in content, "applySortToFilteredRecords helper must be defined"
    assert "applySortToFilteredRecords()" in content, "applySortToFilteredRecords() must be called"

    # Verify applyFilters invokes applySortToFilteredRecords before rendering
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    assert apply_filters_match, "applyFilters function must exist"
    body = apply_filters_match.group(1)
    assert "applySortToFilteredRecords()" in body, "applySortToFilteredRecords() must be called inside applyFilters()"


def test_bug8_dynamic_map_marker_aggregation():
    """Bug 8: Verify updateMapMarkers computes dynamic locStats from filteredRecords and is triggered by applyFilters."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    # Verify dynamic aggregation in updateMapMarkers
    map_func_match = re.search(r"function updateMapMarkers\(\)\s*\{([\s\S]*?)\n\}", content)
    assert map_func_match, "updateMapMarkers function must exist"
    map_body = map_func_match.group(1)
    assert "locStats" in map_body, "updateMapMarkers must aggregate into locStats"
    assert "filteredRecords.forEach" in map_body, "updateMapMarkers must iterate over filteredRecords"

    # Verify applyFilters invokes updateMapMarkers
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    body = apply_filters_match.group(1)
    assert "updateMapMarkers()" in body, "updateMapMarkers() must be called inside applyFilters()"


def test_bug9_empirical_waterfall_decomposition():
    """Bug 9: Verify empirical median differences in initWaterfallChart and real-time trigger in applyFilters."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    waterfall_match = re.search(r"function initWaterfallChart\(\)\s*\{([\s\S]*?)\n\}", content)
    assert waterfall_match, "initWaterfallChart function must exist"
    wf_body = waterfall_match.group(1)

    # Check for empirical calculation logic
    assert "getMedianVal" in content, "getMedianVal helper function must exist"
    assert "areaDelta" in wf_body, "Must compute areaDelta"
    assert "compDelta" in wf_body, "Must compute compDelta"
    assert "finishDelta" in wf_body, "Must compute finishDelta"
    assert "locationDelta" in wf_body, "Must compute locationDelta"

    # Verify applyFilters invokes initWaterfallChart
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    body = apply_filters_match.group(1)
    assert "initWaterfallChart()" in body, "initWaterfallChart() must be called inside applyFilters()"


def test_bug10_data_loader_clean_paths():
    """Bug 10: Verify data_loader candidate paths and fallback coordinates without bogus or dead paths."""
    src_dir = BASE_DIR / "dashboard" / "src"
    sys.path.insert(0, str(src_dir))
    
    loader_path = src_dir / "data_loader.py"
    assert loader_path.exists(), "data_loader.py must exist"
    loader_content = loader_path.read_text(encoding="utf-8")

    assert "airquality" not in loader_content, "Must not contain dead airquality paths"
    assert "load_raw_dataset" in loader_content, "Must define load_raw_dataset"
    assert "load_neighborhood_coordinates" in loader_content, "Must define load_neighborhood_coordinates"

    # Import and test functions
    import data_loader
    df_raw = data_loader.load_raw_dataset()
    assert isinstance(df_raw, pd.DataFrame), "load_raw_dataset must return pandas DataFrame"
    assert len(df_raw) > 10000, f"Expected >10,000 records, got {len(df_raw)}"

    df_coords = data_loader.load_neighborhood_coordinates()
    assert isinstance(df_coords, pd.DataFrame), "load_neighborhood_coordinates must return DataFrame"
    assert "latitude" in df_coords.columns, "Must have latitude column"
    assert "longitude" in df_coords.columns, "Must have longitude column"
    assert len(df_coords) >= 10, f"Expected >=10 coordinate entries, got {len(df_coords)}"
