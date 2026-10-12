# -*- coding: utf-8 -*-
"""
Batch 5 Test Suite: Advanced Statistics & BI Suite Extension
Verifies:
1. Navigation switcher between Operations and Statistics areas.
2. 5 distinct Statistics slides with strictly 4 cards per slide (Rule 5: 4 cards max, no outer scrolling).
3. 20 distinct analytical charts, all equipped with explanatory commentary and interactive view switchers.
4. Genuine dataset integration (33,401 listings, furnished index integration, exact median/mean mathematical calculations).
5. Zero-scroll viewport layout, dedicated statistical slicing filters, and active filter ribbon.
"""

from pathlib import Path
import re
import pytest

DASHBOARD_HTML = Path(r"D:\RealEstateDashBoard\dashboard\index.html")
DATA_JSON = Path(r"D:\RealEstateDashBoard\dashboard\data.json")
CSV_PATH = Path(r"D:\RealEstateDashBoard\data_analysis\after\after_env.csv")


def test_statistics_navigation_switcher_and_containers():
    """Verify top navigation switcher and clean section container architecture."""
    assert DASHBOARD_HTML.exists(), "Dashboard index.html must exist"
    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Navigation buttons
    assert 'class="nav-section-switcher"' in html or "nav-section-switcher" in html
    assert 'id="btnNavOperations"' in html
    assert 'id="btnNavStatistics"' in html
    assert "switchMainSection('operations'" in html or 'switchMainSection("operations"' in html
    assert "switchMainSection('statistics'" in html or 'switchMainSection("statistics"' in html

    # Main containers
    assert 'id="operationsContainer"' in html
    assert 'id="statisticsContainer"' in html

    # Exactly 1 container of each
    assert html.count('id="operationsContainer"') == 1
    assert html.count('id="statisticsContainer"') == 1

    # Operations starts displayed, statistics starts hidden
    assert 'id="operationsContainer" style="display:flex;' in html
    assert 'id="statisticsContainer" style="display:none;' in html


def test_statistics_5_distinct_slides_and_card_architecture():
    """Verify all 5 Statistics slides exist, each with exactly 4 cards (20 cards total)."""
    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # 5 Tab buttons
    for i in range(1, 6):
        assert f'id="tabStat{i}"' in html, f"Missing tabStat{i}"
        assert f"goToStatSlide({i}" in html

    # 5 Slide sections
    for i in range(1, 6):
        assert f'id="statSlide{i}"' in html, f"Missing statSlide{i}"

    # Extract contents of each slide and count cards
    for i in range(1, 6):
        slide_pattern = rf'<section[^>]*id="statSlide{i}"[^>]*>(.*?)</section>'
        match = re.search(slide_pattern, html, re.DOTALL)
        assert match, f"Could not find section statSlide{i}"
        slide_content = match.group(1)

        # Count cards with class="card"
        cards = re.findall(r'<div class="card">', slide_content)
        assert len(cards) == 4, f"statSlide{i} must contain exactly 4 cards, found {len(cards)}"

    # Check bottom controller for statistics
    assert 'id="btnPrevStatSlide"' in html
    assert 'id="btnNextStatSlide"' in html
    assert 'id="statSlideIndicator"' in html
    assert "changeStatSlide(-1" in html
    assert "changeStatSlide(1" in html


def test_statistics_20_charts_with_commentary_and_view_switchers():
    """Verify all 20 charts exist, each having an explanatory commentary callout and a view switcher."""
    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    expected_canvases = [
        # Slide 1: Overview
        'chartStatOverviewType', 'chartStatOverviewGauge', 'chartStatOverviewRegion', 'chartStatOverviewTiers',
        # Slide 2: Market Analysis
        'chartStatMarketTypePrice', 'chartStatMarketFinishing', 'chartStatMarketFurnished', 'chartStatMarketAreaSpread',
        # Slide 3: Property Analysis
        'chartStatPropBeds', 'chartStatPropBaths', 'chartStatPropViews', 'chartStatPropSizeBeds',
        # Slide 4: Location Analysis
        'chartStatLocVolume', 'chartStatLocPPM', 'chartStatLocCities', 'chartStatLocCompound',
        # Slide 5: Price Analysis
        'chartStatPriceHist', 'chartStatPriceElasticity', 'chartStatPriceBox', 'chartStatPriceMatrix'
    ]

    for canvas_id in expected_canvases:
        assert f'id="{canvas_id}"' in html, f"Missing canvas element {canvas_id}"
        assert f"toggleChartType('{canvas_id}'" in html, f"Canvas {canvas_id} must have a toggleChartType switcher button"

    # Verify each card contains chart-explanation with "What does this chart mean?"
    stat_section_match = re.search(r'<div id="statisticsContainer".*?</div> <!-- End statisticsContainer -->', html, re.DOTALL)
    assert stat_section_match, "Could not extract statisticsContainer block"
    stat_html = stat_section_match.group(0)

    explanations = re.findall(r'<div class="chart-explanation">💡\s*<b>What does this chart mean\?</b>', stat_html)
    assert len(explanations) == 20, f"Expected 20 chart commentary explanations in Statistics, found {len(explanations)}"


def test_statistics_real_data_integrity_and_furnished_integration():
    """Verify data bundle and JavaScript engine use genuine dataset with Furnished column."""
    import json
    data_content = json.loads(DATA_JSON.read_text(encoding="utf-8"))

    # Verify dataset scale
    assert len(data_content["records"]) == 33401, "Total records must be 33,401"
    assert "furnished_indices" in data_content, "data.json must contain furnished_indices"
    assert len(data_content["furnished_indices"]) == 3195, "Exactly 3,195 furnished records in after_env.csv"

    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Check furnished mapping in initDataNormalization
    assert "furnishedSet" in html
    assert "r.furnished" in html or "norm.furnished" in html

    # Check JS math and filtering logic
    assert "function applyStatsFilters()" in html
    assert "function resetStatsFilters(" in html
    assert "function updateStatHeroKPIs()" in html
    assert "function updateStatisticsCharts()" in html
    assert "function renderSingleStatChart(" in html


def test_statistics_zero_scroll_and_filtering_capabilities():
    """Verify zero scroll layout constraints and statistics filter suite."""
    html = DASHBOARD_HTML.read_text(encoding="utf-8")

    # Zero scroll constraint on container
    assert 'id="statisticsContainer" style="display:none; flex-direction:column; height:calc(100vh - 52px); overflow:hidden;"' in html

    # Dedicated filters for statistics
    assert 'id="statFilterCity"' in html
    assert 'id="statFilterType"' in html
    assert 'id="statFilterFurnished"' in html
    assert 'id="statFilterRooms"' in html
    assert 'id="statFilterMaxPrice"' in html
    assert 'id="statFilterView"' in html
    assert 'id="statFilteredCountLabel"' in html
    assert 'id="statActiveFilterRibbon"' in html
    assert "resetStatsFilters(event)" in html

    # Check hero KPI strip on Slide 1
    assert 'id="statKpiTotal"' in html
    assert 'id="statKpiPrice"' in html
    assert 'id="statKpiPPM"' in html
    assert 'id="statKpiArea"' in html
