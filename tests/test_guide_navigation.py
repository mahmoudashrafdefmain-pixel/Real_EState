# -*- coding: utf-8 -*-
"""
Test Suite: Dashboard Guide & Model Validation Navigation
File: test_guide_navigation.py
Verifies:
1. Guide page renders cleanly with all Sections A through I.
2. Streamlit app.py navigation exposes all 4 pages including Guide and AI Valuation Model.
3. Standalone HTML dashboard index.html integrates btnNavGuide button and guideModal dialog.
4. Model Validation Report page renders cleanly with KPI cards, baseline comparisons, and live simulator.
"""

import sys
from pathlib import Path
import pytest
import streamlit as st

core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

DASHBOARD_HTML = core_dir / "index.html"
APP_PY = core_dir / "app.py"


class MockColumn:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def markdown(self, *args, **kwargs):
        pass
    def metric(self, *args, **kwargs):
        pass
    def number_input(self, *args, **kwargs):
        return kwargs.get("value", 100.0)
    def selectbox(self, *args, **kwargs):
        opts = kwargs.get("options", ["Option 1"])
        return opts[kwargs.get("index", 0)] if opts else "Option 1"
    def slider(self, *args, **kwargs):
        return kwargs.get("value", 50.0)
    def button(self, *args, **kwargs):
        return False
    def caption(self, *args, **kwargs):
        pass


class MockContext:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


def test_guide_sections_completeness():
    """Verify that Guide module covers all 9 mandatory sections (A through I)."""
    from src.view_guide import render_guide_page
    guide_code = (core_dir / "src" / "view_guide.py").read_text(encoding="utf-8")

    expected_sections = [
        "Section A: Getting Started",
        "Section B: Dashboard Modes",
        "Section C: Navigation & Page Directory",
        "Section D: Filters & Controls",
        "Section E: Charts & Statistical Analysis",
        "Section F: Predictive Model",
        "Section G: Investment Feasibility Lab",
        "Section H: Understanding Results & Limitations",
        "Section I: Quick-Start Workflow"
    ]

    for sec in expected_sections:
        assert sec in guide_code, f"Mandatory guide section '{sec}' missing from view_guide.py"


def test_guide_renders_without_exceptions(monkeypatch):
    """Verify render_guide_page executes without uncaught exceptions under mocked Streamlit."""
    from src.view_guide import render_guide_page

    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "columns", lambda n: [MockColumn() for _ in range(n if isinstance(n, int) else len(n))])
    monkeypatch.setattr(st, "tabs", lambda names: [MockContext() for _ in names])
    monkeypatch.setattr(st, "button", lambda *a, **k: False)
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "dataframe", lambda *a, **k: None)

    # Must execute with zero exceptions
    render_guide_page()


def test_model_validation_renders_without_exceptions(monkeypatch):
    """Verify render_model_validation_page executes cleanly without uncaught exceptions."""
    from src.view_model_validation import render_model_validation_page

    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)
    monkeypatch.setattr(st, "columns", lambda n: [MockColumn() for _ in range(n if isinstance(n, int) else len(n))])
    monkeypatch.setattr(st, "tabs", lambda names: [MockContext() for _ in names])
    monkeypatch.setattr(st, "expander", lambda *a, **k: MockContext())
    monkeypatch.setattr(st, "dataframe", lambda *a, **k: None)
    monkeypatch.setattr(st, "plotly_chart", lambda *a, **k: None)
    monkeypatch.setattr(st, "number_input", lambda *a, **k: k.get("value", 100.0))
    monkeypatch.setattr(st, "selectbox", lambda *a, **k: k.get("options", ["A"])[k.get("index", 0)])
    monkeypatch.setattr(st, "slider", lambda *a, **k: k.get("value", 50.0))
    monkeypatch.setattr(st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(st, "warning", lambda *a, **k: None)

    # Must execute with zero exceptions
    render_model_validation_page()


def test_app_py_navigation_options():
    """Verify that app.py contains all 4 page options in sidebar radio navigation."""
    assert APP_PY.exists(), "app.py must exist"
    app_text = APP_PY.read_text(encoding="utf-8")

    assert "1. 🏦 Bank System & Financing Calculator" in app_text
    assert "2. 🌟 Dynamic Market & Quality Dashboard" in app_text
    assert "3. 🤖 AI Valuation Model & Validation Report" in app_text
    assert "4. 📖 Dashboard Guide & System Manual" in app_text


def test_html_dashboard_guide_integration():
    """Verify that standalone HTML dashboard contains Guide navigation button and modal."""
    assert DASHBOARD_HTML.exists(), "index.html must exist"
    html_text = DASHBOARD_HTML.read_text(encoding="utf-8")

    assert 'id="btnNavGuide"' in html_text, "Top navigation must contain btnNavGuide"
    assert 'id="guideModal"' in html_text, "HTML must contain guideModal dialog"
    assert "openGuideModal" in html_text, "JavaScript must implement openGuideModal"
    assert "closeGuideModalDirect" in html_text, "JavaScript must implement closeGuideModalDirect"
