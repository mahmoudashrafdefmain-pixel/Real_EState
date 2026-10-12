# -*- coding: utf-8 -*-
r"""
Egypt Real Estate Intelligence Platform
Streamlit Decision Engine
"""
import sys
import subprocess
from pathlib import Path

try:
    import streamlit as st
except ImportError:
    print("=" * 68)
    print("  [ERROR] Streamlit is not installed in this Python environment:")
    print(f"  {sys.executable}")
    print("=" * 68)
    print("  To run this application, use Python 3.12 where Streamlit is installed:")
    print(r"    cd D:\RealEstateDashBoard")
    print("    py -3.12 run_streamlit.py")
    print("=" * 68)
    sys.exit(1)

# Auto-bootstrap Streamlit runner if invoked directly via bare python
if not st.runtime.exists():
    app_path = Path(__file__).resolve()
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=false",
        "--theme.primaryColor=#2A9D8F",
        "--theme.backgroundColor=#F8F9FA",
        "--theme.secondaryBackgroundColor=#FFFFFF",
        "--theme.textColor=#1B2A4A"
    ]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
    sys.exit(0)

core_dir = Path(__file__).resolve().parent
root_dir = core_dir.parent
model_dir = root_dir / "model"
for p in [core_dir, root_dir, model_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# configure global application layout and title
st.set_page_config(
    page_title="Egypt Real-Estate Financing Decision Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# inject strict zero outer page scroll executive styling
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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    [data-testid="stAppViewContainer"], .main {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        background-color: #F8F9FA !important;
    }

    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
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

    header[data-testid="stHeader"] {
        height: 1.5rem !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        overflow-y: auto !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: #1B2A4A !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        opacity: 1 !important;
        cursor: pointer !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        margin-bottom: 4px !important;
        background: #F1F5F9 !important;
        display: flex !important;
        transition: all 0.15s ease-in-out !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #E2E8F0 !important;
        color: #2A9D8F !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

from src.view_dynamic_dashboard import render_dynamic_dashboard_page
from src.view_mortgage import render_mortgage_financing_page
from src.view_model_validation import render_model_validation_page
from src.view_guide import render_guide_page

# Available application pages
page_options = [
    "1. 🏦 Bank System & Financing Calculator",
    "2. 🌟 Dynamic Market & Quality Dashboard",
    "3. 🤖 AI Valuation Model & Validation Report",
    "4. 📖 Dashboard Guide & System Manual"
]

# Track previous page to allow smooth return from Guide
current_index = 0
if "nav_page_selection" in st.session_state and st.session_state["nav_page_selection"] in page_options:
    current_index = page_options.index(st.session_state["nav_page_selection"])

# render prominent executive sidebar with 4 integrated pages
with st.sidebar:
    st.markdown(
        """
        <div style="background-color:#1B2A4A; padding:14px; border-radius:8px; margin-bottom:14px; color:#FFFFFF; text-align:center;">
            <div style="font-size:0.75rem; font-weight:800; color:#E9B44C; text-transform:uppercase; letter-spacing:1px;">EGYPT REAL ESTATE</div>
            <h3 style="margin:4px 0 0 0; color:#FFFFFF; font-size:1.15rem; font-weight:800;">Decision Engine</h3>
            <div style="font-size:0.75rem; color:#CBD5E1; margin-top:3px;">Dynamic Multi-Factor Platform</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    page_choice = st.radio(
        "Navigation",
        options=page_options,
        index=current_index,
        label_visibility="collapsed"
    )

    # Save last analytical workspace if not currently browsing Guide
    if "Guide" not in page_choice:
        st.session_state["previous_active_page"] = page_choice
    st.session_state["nav_page_selection"] = page_choice

    st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:10px 12px; border-radius:6px; font-size:0.75rem; color:#64748B; line-height:1.4;">
            <strong>Platform Standards:</strong><br>
            - Active Market: 33,401 Listings<br>
            - 4-5 Factor Adaptive Quality Score<br>
            - Standalone: Floor Excluded<br>
            - Price Worthiness: Score ≥ 65 Gate<br>
            - Model R²: 63.9% (Held-Out Test)<br>
            - Bank Income Min: EGP 20,000/mo<br>
            - Max Installment: 30% DTI Cap
        </div>
        """,
        unsafe_allow_html=True
    )

# dispatch to selected page renderer
if "Bank" in page_choice or "Financing" in page_choice:
    render_mortgage_financing_page()
elif "Dynamic Market" in page_choice:
    render_dynamic_dashboard_page()
elif "AI Valuation" in page_choice:
    render_model_validation_page()
elif "Guide" in page_choice:
    render_guide_page()
else:
    render_mortgage_financing_page()


