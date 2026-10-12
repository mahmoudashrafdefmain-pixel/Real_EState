# -*- coding: utf-8 -*-
"""
Test Suite for Batch 4: Advanced Features & Zero-Scroll Layout Overhaul (Additions 1 to 5 + 5 UX Rules)
"""
import re
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent

def test_addition1_mortgage_rate_and_down_payment_sliders():
    """Addition 1: Verify interactive mortgage interest rate (3-25%) and down payment ratio sliders and presets."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    assert 'id="slAffordInterest"' in content, "slAffordInterest slider must exist"
    assert 'id="slAffordDownPct"' in content, "slAffordDownPct slider must exist"
    assert "setMortgageRatePreset" in content, "setMortgageRatePreset function must exist"

    # Verify preset buttons for Subsidized 3%, Middle 8%, Commercial 17.5%
    assert "Subsidized 3%" in content, "Subsidized 3% preset button must exist"
    assert "Middle Tier 8%" in content, "Middle Tier 8% preset button must exist"
    assert "Commercial 17.5%" in content, "Commercial 17.5% preset button must exist"

    # Verify calculateAffordabilityScore uses dynamic rate and down payment
    afford_match = re.search(r"function calculateAffordabilityScore\([\s\S]*?\{([\s\S]*?)\n\}", content)
    assert afford_match, "calculateAffordabilityScore function must exist"
    afford_body = afford_match.group(1)
    assert "slAffordInterest" in afford_body, "calculateAffordabilityScore must read slAffordInterest"
    assert "slAffordDownPct" in afford_body, "calculateAffordabilityScore must read slAffordDownPct"


def test_addition2_directional_sort_glyphs_and_studios():
    """Addition 2: Verify directional sort glyphs (▲/▼/⬍), studios, 5+ beds, and sortable Opportunity/DTI & Baths."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    # Table headers with sort glyph IDs
    assert 'id="th_col_9"' in content, "Normalized location header must exist"
    assert 'id="th_col_23"' in content, "Opportunity/DTI sortable header must exist"
    assert 'id="th_col_4"' in content, "Bathrooms sortable header must exist"
    assert 'id="glyph_9"' in content, "Glyph span 9 must exist"
    assert 'id="glyph_23"' in content, "Glyph span 23 must exist"

    # Directional glyphs in applySortToFilteredRecords
    assert "'▲' : '▼'" in content or '"▲" : "▼"' in content or "currentSortAsc ? '▲' : '▼'" in content, "applySortToFilteredRecords must update ▲ / ▼ glyphs"

    # filterRooms options
    assert 'value="0"' in content, "Studio (0-Bed) option must exist"
    assert 'value="5+"' in content, "5+ Bedrooms option must exist"

    # Rooms filter logic in applyFilters
    apply_filters_match = re.search(r"function applyFilters\(\)\s*\{([\s\S]*?)\n\}", content)
    body = apply_filters_match.group(1)
    assert "rooms === '0'" in body, "applyFilters must handle Studio (0) rooms"
    assert "rooms === '5+'" in body, "applyFilters must handle 5+ rooms"


def test_addition3_active_filter_ribbon():
    """Addition 3: Verify active filter tag ribbon container and dynamic chip rendering with removal callbacks."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    assert 'id="activeFilterRibbon"' in content, "activeFilterRibbon container must exist in DOM"
    assert "function renderActiveFilterRibbon" in content, "renderActiveFilterRibbon function must be defined"
    assert "renderActiveFilterRibbon()" in content, "renderActiveFilterRibbon() must be called in applyFilters"
    assert "filter-chip" in content, "filter-chip class must be used for active chips"
    assert "filter-chip-remove" in content, "filter-chip-remove must provide individual [✕] remove buttons"


def test_addition4_comparison_matrix_print_report():
    """Addition 4: Verify Export Comparison PDF / Print Report button and @media print CSS."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    assert "Export Comparison PDF / Print Report" in content, "Print dossier button must exist in compare modal"
    assert "function printCompareDossier" in content, "printCompareDossier JS function must be defined"
    assert "@media print" in content, "@media print CSS block must exist"
    assert "#compareModal" in content, "compareModal print styles must be declared"


def test_addition5_map_flyto_and_pulse_ring():
    """Addition 5: Verify map flyTo and luminous pulse ring animation on hub selection."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    map_filter_match = re.search(r"function filterByMapLocation\([\s\S]*?\{([\s\S]*?)\n\}", content)
    assert map_filter_match, "filterByMapLocation function must exist"
    body = map_filter_match.group(1)

    assert "mapInstance.flyTo" in body, "filterByMapLocation must invoke mapInstance.flyTo"
    assert "pulseRing" in body, "filterByMapLocation must create a pulse ring marker"
    assert "setTimeout" in body, "pulseRing must be removed after animation"


def test_ux_rules_zero_scroll_and_chart_explanations():
    """UX Rules: Verify strict zero outer scrolling (100vh), 5 unique slides with 4 cards, and chart commentaries & toggles."""
    html_file = BASE_DIR / "dashboard" / "index.html"
    content = html_file.read_text(encoding="utf-8")

    # Rule 1: Zero outer window scrolling
    assert "overflow: hidden" in content, "Must declare overflow: hidden on html/body"
    assert "height: 100vh" in content, "Must lock height to 100vh"

    # Rule 2: 5 unique slides
    for i in range(1, 6):
        assert f'id="slide{i}"' in content, f"slide{i} must exist"

    # Rule 5: Explanatory commentaries ("What does this chart mean?") and dynamic toggles
    assert content.count("What does this chart mean?") >= 7, "Must have 'What does this chart mean?' on all 7 charts"
    assert "function toggleChartType" in content, "toggleChartType function must be defined"
    assert content.count("toggleChartType(") >= 7, "Must have toggleChartType button on all 7 charts"
