# -*- coding: utf-8 -*-
from typing import Union, Any
import math

# format numerical amounts to professional egp currency strings
def format_currency(val: Any) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "EGP —"
    try:
        num = float(val)
        return f"EGP {num:,.0f}"
    except Exception:
        return "EGP —"

# format decimal ratios to readable percentages
def format_percentage(val: Any) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "— %"
    try:
        num = float(val)
        return f"{num * 100.0:.1f}%" if num <= 1.0 else f"{num:.1f}%"
    except Exception:
        return "— %"

# format distance in kilometers
def format_distance(val: Any) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "Distance unavailable"
    try:
        num = float(val)
        return f"{num:.1f} km"
    except Exception:
        return "Distance unavailable"

# format apartment surface area in square meters
def format_area(val: Any) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "— m²"
    try:
        num = float(val)
        return f"{num:.0f} m²"
    except Exception:
        return "— m²"

# generate html status badge for matching results
def format_status_badge(status: str) -> str:
    if status == "MATCH":
        return "<span style='background-color:#E6F4EA; color:#137333; font-weight:700; padding:3px 8px; border-radius:4px; font-size:0.80rem;'>✓ MATCH</span>"
    elif status == "CLOSE MATCH":
        return "<span style='background-color:#FEF7E0; color:#B06000; font-weight:700; padding:3px 8px; border-radius:4px; font-size:0.80rem;'>⚠ CLOSE MATCH</span>"
    else:
        return "<span style='background-color:#FCE8E6; color:#C5221F; font-weight:700; padding:3px 8px; border-radius:4px; font-size:0.80rem;'>✕ NOT MATCHED</span>"

# inject strict zero outer page scroll styling
def inject_zero_scroll_css():
    import streamlit as st
    st.markdown(
        """
        <style>
        html, body {
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #F8F9FA !important;
        }
        [data-testid="stAppViewContainer"], .main {
            height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
            background-color: #F8F9FA !important;
        }
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
            max-width: 100% !important;
            height: calc(100vh - 1rem) !important;
            max-height: calc(100vh - 1rem) !important;
            overflow-y: auto !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        .block-container::-webkit-scrollbar {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
