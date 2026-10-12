# -*- coding: utf-8 -*-
import math
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import streamlit as st

from .config import (
    FACTOR_EDUCATIONAL_EXPLANATIONS,
    SCORE_DISCLAIMER,
    USER_FRIENDLY_FACTOR_NAMES
)
from .formatting import format_currency, format_area

# helper kept for backwards compatibility
def create_property_score_chart(prop: pd.Series):
    return None

# render complete score breakdown inline without charts
def render_property_score_inline(prop: pd.Series):
    loc_str = str(prop.get("Location", prop.get("region", "Unknown Location")))
    price_val = float(prop.get("Price_Numeric", 0.0))
    area_val = float(prop.get("Area", prop.get("size_sqm", 0.0)))
    tot_score = float(prop.get("property_quality_value_score", 0.0))
    tier_label = str(prop.get("score_tier_label", "Moderate"))
    tier_color = str(prop.get("score_tier_color", "#1B2A4A"))
    data_quality = str(prop.get("score_data_quality", "Complete"))
    prop_type = str(prop.get("property_type", prop.get("type", "Unit")))

    air_s = float(prop.get("air_quality_score", 0.0))
    green_s = float(prop.get("green_coverage_score", 0.0))
    price_s = float(prop.get("price_value_score", 0.0))
    finish_s = float(prop.get("class_view_score", prop.get("finishing_score", 0.0)))
    floor_s = prop.get("floor_score", np.nan)
    floor_avail = bool(prop.get("floor_available", False)) and not (isinstance(floor_s, float) and math.isnan(floor_s))

    deserves_price = bool(tot_score >= 65.0)

    with st.container(border=True):
        head_c1, head_c2, head_c3 = st.columns([1.5, 1.2, 1.3])
        with head_c1:
            st.markdown(f"### {loc_str}")
            st.caption(f"Type: **{prop_type}** | Price: **{format_currency(price_val)}** | Area: **{format_area(area_val)}**")
        with head_c2:
            st.metric(
                label="Property Quality & Value Score",
                value=f"{tot_score:.0f} / 100",
                delta=f"{tot_score:.0f}% ({tier_label})",
                delta_color="normal"
            )
        with head_c3:
            floor_status_badge = "Floor: Included (5 Factors)" if floor_avail else "Floor: Excluded (4 Factors)"
            st.markdown(
                f"<div style='background:#F8FAFC; border:1px solid #E2E8F0; padding:8px 12px; border-radius:6px; font-size:0.80rem;'>"
                f"Data Confidence: <strong>{data_quality}</strong><br>"
                f"Project Tier: <strong style='color:{tier_color};'>{tier_label}</strong><br>"
                f"<span style='color:#64748B;'>Standard: {floor_status_badge}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

        # 65-Point Price Justification Verdict Banner
        if deserves_price:
            st.markdown(
                f"""<div style="background:#E6F4EA; border:2px solid #34A853; border-radius:8px; padding:10px 14px; margin:8px 0 12px 0;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:1.02rem; font-weight:800; color:#137333;">✅ PRICE JUSTIFICATION: DESERVES ASKING PRICE</span>
<span style="background:#34A853; color:#FFFFFF; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px;">SCORE ≥ 65 BENCHMARK PASSED</span>
</div>
<div style="font-size:0.80rem; color:#1E4620; margin-top:4px;">
This {prop_type} achieved <strong>{tot_score:.0f}/100 points</strong> (≥ 65 benchmark). Its environmental quality, green surroundings, community classification, and location pricing fully justify its valuation of <strong>{format_currency(price_val)}</strong>.
</div>
</div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""<div style="background:#FCE8E6; border:2px solid #EA4335; border-radius:8px; padding:10px 14px; margin:8px 0 12px 0;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:1.02rem; font-weight:800; color:#C5221F;">❌ PRICE JUSTIFICATION: DOES NOT DESERVE ASKING PRICE</span>
<span style="background:#EA4335; color:#FFFFFF; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:12px;">SCORE &lt; 65 (OVERPRICED)</span>
</div>
<div style="font-size:0.80rem; color:#5C1D18; margin-top:4px;">
This {prop_type} achieved only <strong>{tot_score:.0f}/100 points</strong> (&lt; 65 benchmark). The asking price of <strong>{format_currency(price_val)}</strong> is considered overpriced for the delivered environmental and community quality standard.
</div>
</div>""",
                unsafe_allow_html=True
            )

        # Multi-factor distributed proportions strip
        grid_cols = 5 if floor_avail else 4
        floor_box = ""
        if floor_avail:
            fl_val = float(floor_s)
            floor_box = f"""<div style='background:rgba(255,255,255,0.08); padding:8px 6px; border-radius:5px; border:1px solid rgba(255,255,255,0.12);'>
<div style='font-size:0.72rem; color:#CBD5E1;'>Floor Level (25)</div>
<div style='font-size:1.15rem; font-weight:800; color:#A78BFA; margin:2px 0;'>{fl_val:.0f} / 25</div>
<div style='font-size:0.68rem; color:#94A3B8;'>{ (fl_val/25.0)*100.0:.0f}% Factor</div>
</div>"""

        st.markdown(
            f"""<div style='background:#1B2A4A; padding:10px 14px; border-radius:6px; margin:8px 0; color:#FFFFFF;'>
<div style='font-size:0.78rem; font-weight:700; color:#E9B44C; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.5px;'>
Adaptive Factor Score Distribution ({grid_cols} Factors = 100 Total)</div>
<div style='display:grid; grid-template-columns:repeat({grid_cols}, 1fr); gap:8px; text-align:center;'>
<div style='background:rgba(255,255,255,0.08); padding:8px 6px; border-radius:5px; border:1px solid rgba(255,255,255,0.12);'>
<div style='font-size:0.72rem; color:#CBD5E1;'>Air Quality (25)</div>
<div style='font-size:1.15rem; font-weight:800; color:#2A9D8F; margin:2px 0;'>{air_s:.0f} / 25</div>
<div style='font-size:0.68rem; color:#94A3B8;'>{ (air_s/25.0)*100.0:.0f}% Factor</div>
</div>
<div style='background:rgba(255,255,255,0.08); padding:8px 6px; border-radius:5px; border:1px solid rgba(255,255,255,0.12);'>
<div style='font-size:0.72rem; color:#CBD5E1;'>Green Living (25)</div>
<div style='font-size:1.15rem; font-weight:800; color:#10B981; margin:2px 0;'>{green_s:.0f} / 25</div>
<div style='font-size:0.68rem; color:#94A3B8;'>{ (green_s/25.0)*100.0:.0f}% Factor</div>
</div>
<div style='background:rgba(255,255,255,0.08); padding:8px 6px; border-radius:5px; border:1px solid rgba(255,255,255,0.12);'>
<div style='font-size:0.72rem; color:#CBD5E1;'>Price Value (25)</div>
<div style='font-size:1.15rem; font-weight:800; color:#3B82F6; margin:2px 0;'>{price_s:.0f} / 25</div>
<div style='font-size:0.68rem; color:#94A3B8;'>{ (price_s/25.0)*100.0:.0f}% Factor</div>
</div>
<div style='background:rgba(255,255,255,0.08); padding:8px 6px; border-radius:5px; border:1px solid rgba(255,255,255,0.12);'>
<div style='font-size:0.72rem; color:#CBD5E1;'>Class & View (25)</div>
<div style='font-size:1.15rem; font-weight:800; color:#F59E0B; margin:2px 0;'>{finish_s:.0f} / 25</div>
<div style='font-size:0.68rem; color:#94A3B8;'>{ (finish_s/25.0)*100.0:.0f}% Factor</div>
</div>
{floor_box}
</div>
</div>""",
            unsafe_allow_html=True
        )

        # Strongest and weakest factor insight badges
        ins_c1, ins_c2 = st.columns(2)
        with ins_c1:
            st.success(f"**Strongest Factor:** {prop.get('strongest_factor', 'N/A')}")
        with ins_c2:
            st.warning(f"**Weakest Factor:** {prop.get('weakest_factor', 'N/A')}")

        # Detailed factor cards with explanations
        if floor_avail:
            d_c1, d_c2, d_c3, d_c4, d_c5 = st.columns(5)
            with d_c1:
                with st.container(border=True):
                    st.markdown(f"**AIR QUALITY**\n### {air_s:.0f} / 25")
                    st.caption(f"AQI: **{prop.get('air_quality_value', 'N/A')}**")
                    st.info(prop.get("air_quality_reason", ""))
            with d_c2:
                with st.container(border=True):
                    st.markdown(f"**GREEN LIVING**\n### {green_s:.0f} / 25")
                    st.caption(f"Coverage: **{prop.get('green_coverage_value', 'N/A')}%**")
                    st.info(prop.get("green_coverage_reason", ""))
            with d_c3:
                with st.container(border=True):
                    st.markdown(f"**PRICE VALUE**\n### {price_s:.0f} / 25")
                    st.caption(f"Price/m²: **{format_currency(prop.get('price_per_m2', np.nan))}**")
                    st.info(prop.get("price_value_reason", ""))
            with d_c4:
                with st.container(border=True):
                    st.markdown(f"**CLASS & VIEW**\n### {finish_s:.0f} / 25")
                    st.caption(f"Community: **{prop.get('class_view_display', 'Standard')}**")
                    st.info(prop.get("class_view_reason", ""))
            with d_c5:
                with st.container(border=True):
                    st.markdown(f"**FLOOR LEVEL**\n### {float(floor_s):.0f} / 25")
                    st.caption(f"Level: **Floor {prop.get('floor_level', 'N/A')}**")
                    st.info(prop.get("floor_score_reason", ""))
        else:
            d_c1, d_c2, d_c3, d_c4 = st.columns(4)
            with d_c1:
                with st.container(border=True):
                    st.markdown(f"**AIR QUALITY**\n### {air_s:.0f} / 25")
                    st.caption(f"AQI: **{prop.get('air_quality_value', 'N/A')}**")
                    st.info(prop.get("air_quality_reason", ""))
            with d_c2:
                with st.container(border=True):
                    st.markdown(f"**GREEN LIVING**\n### {green_s:.0f} / 25")
                    st.caption(f"Coverage: **{prop.get('green_coverage_value', 'N/A')}%**")
                    st.info(prop.get("green_coverage_reason", ""))
            with d_c3:
                with st.container(border=True):
                    st.markdown(f"**PRICE VALUE**\n### {price_s:.0f} / 25")
                    st.caption(f"Price/m²: **{format_currency(prop.get('price_per_m2', np.nan))}**")
                    st.info(prop.get("price_value_reason", ""))
            with d_c4:
                with st.container(border=True):
                    st.markdown(f"**CLASS & VIEW**\n### {finish_s:.0f} / 25")
                    st.caption(f"Community: **{prop.get('class_view_display', 'Standard')}**")
                    st.info(prop.get("class_view_reason", ""))

        with st.expander("Why Each Factor Matters (Methodology Guide)", expanded=False):
            for factor_name, rationale in FACTOR_EDUCATIONAL_EXPLANATIONS.items():
                st.markdown(f"- **{factor_name}:** {rationale}")

        st.caption(SCORE_DISCLAIMER)

# render modal dialog with complete score breakdown without charts
@st.dialog("Property Quality & Value Score Breakdown", width="large")
def render_property_score_dialog(prop: pd.Series):
    render_property_score_inline(prop)
    if st.button("Close Score Window", use_container_width=True):
        st.rerun()
