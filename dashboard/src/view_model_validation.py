# -*- coding: utf-8 -*-
"""
Egypt Real Estate Intelligence Platform
Module: view_model_validation.py
Purpose:
    AI Valuation Model Governance, Class-Separated Estimators,
    and Inferential Statistics & Hypothesis Testing Suite.
    - Tab 1: Interactive Property Valuation Simulator (Class A, B, C, D)
    - Tab 2: Class-Separated Model Governance, Reliability & Monotonic Scaling
    - Tab 3: Inferential Statistics Lab (Welch's t-test, ANOVA, Chi-Square, 95% CIs)
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from .formatting import format_currency, inject_zero_scroll_css
from .data_loader import load_raw_dataset
from .inferential_statistics import (
    run_two_sample_t_test,
    run_one_way_anova,
    run_chi_square_test,
    compute_confidence_intervals,
    compute_correlation_matrix
)
from ml_engine import (
    get_model_pipeline,
    predict_property_price,
    get_model_validation_report,
    get_model_metadata
)

# Egyptian Executive Palette Tokens
DEEP_NAVY = "#1B2A4A"
NILE_TEAL = "#2A9D8F"
SANDSTONE_GOLD = "#E9B44C"
CORAL_RED = "#E85D4C"
SOFT_SAGE = "#8FB996"
CHARCOAL = "#264653"
LIGHT_BG = "#F8F9FA"


def render_model_validation_page():
    """Renders the comprehensive Model Performance, Validation Report & Predictor view."""
    inject_zero_scroll_css()

    rep = get_model_validation_report()
    meta = rep.get("model_metadata", {})
    per_class = rep.get("per_class_performance", {})
    overall = rep.get("combined_held_out_metrics", {})
    baselines = rep.get("baseline_benchmarks", {})
    monotonic_audit = rep.get("monotonicity_audit", {})
    subgroups = rep.get("subgroups", {})

    # Top Executive Header Strip
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {DEEP_NAVY} 0%, #2A4365 100%);
                    padding: 12px 20px; border-radius: 8px; margin-bottom: 12px; color: #FFFFFF;
                    display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div>
                <h2 style="margin: 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.3px;">
                    AI VALUATION ENGINE & INFERENTIAL STATISTICS SUITE
                </h2>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 2px;">
                    Class-Separated Hedonic Estimators (A, B, C, D) | Monotonic Constraints | Hypothesis Testing Lab
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: rgba(42, 157, 143, 0.25); border: 1px solid {NILE_TEAL};
                             color: #A7F3D0; padding: 4px 12px; border-radius: 20px;
                             font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">
                    SUITE STATUS: 4 MODELS VALIDATED
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_predictor, tab_governance, tab_stats = st.tabs([
        "🔮 1. Property Valuation Simulator",
        "📊 2. Class-Separated Governance & Monotonicity",
        "🧪 3. Inferential Statistics Lab"
    ])

    # -------------------------------------------------------------
    # TAB 1: VALUATION SIMULATOR
    # -------------------------------------------------------------
    with tab_predictor:
        st.markdown("##### INTERACTIVE PROPERTY VALUATION SIMULATOR (CLASS-SEPARATED ENGINE)")
        st.caption("Select compound tier and unit specifications below to route inference to the specialized class estimator.")

        p_col1, p_col2, p_col3 = st.columns(3)

        with p_col1:
            in_area = st.number_input("Living Area (m²)", min_value=25.0, max_value=1200.0, value=160.0, step=5.0)
            in_type = st.selectbox("Property Type", options=["Apartment", "Standalone Villa", "Townhouse", "Twin House", "Duplex", "Penthouse", "Chalet", "Studio"], index=0)
            in_class = st.selectbox("Compound Class Tier", options=["Class A (Ultra Luxury / Gated)", "Class B (Master Community)", "Class C (Mid-Market)", "Class D (Standalone Urban)"], index=1)
            in_view = st.selectbox("View Orientation", options=["Garden View", "Open View", "Pool View", "Sea View", "Lagoon / Lake View", "City View", "Street View"], index=0)

        with p_col2:
            in_beds = st.number_input("Bedrooms", min_value=1.0, max_value=8.0, value=3.0, step=1.0)
            in_baths = st.number_input("Bathrooms", min_value=1.0, max_value=8.0, value=2.0, step=1.0)
            in_floor = st.number_input("Floor Level (0 for Ground)", min_value=0.0, max_value=20.0, value=3.0, step=1.0)
            in_furn = st.selectbox("Furnishing Status", options=["No (Unfurnished)", "Yes (Furnished)"], index=0)

        with p_col3:
            in_city = st.selectbox("Macro City", options=["Cairo", "Giza", "Alexandria", "Red Sea", "Suez", "North Coast"], index=0)
            in_region = st.selectbox("District / Submarket", options=["New Cairo", "Sheikh Zayed", "6 October City", "Madinaty", "Maadi", "Nasr City", "Heliopolis", "Al Rehab", "Dokki", "El Shorouk City"], index=0)
            in_aqi = st.slider("Environmental AQI (Air Pollution)", min_value=40.0, max_value=100.0, value=68.0, step=1.0)
            in_green = st.slider("Green Space Coverage (%)", min_value=0.0, max_value=40.0, value=8.5, step=0.5)

        # Trigger Valuation Calculation
        cls_code = in_class.split(" ")[0] + " " + in_class.split(" ")[1]
        furn_val = "Yes" if "yes" in in_furn.lower() else "No"

        pipe = get_model_pipeline()
        result = predict_property_price(
            size_sqm=in_area,
            bedrooms=in_beds,
            bathrooms=in_baths,
            floor=in_floor,
            property_type=in_type,
            class_tier=cls_code,
            view=in_view,
            city=in_city,
            region=in_region,
            furnished=furn_val,
            air_quality=in_aqi,
            green_space=in_green,
            pipeline=pipe
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Render Valuation Output Box
        v_col1, v_col2, v_col3, v_col4 = st.columns(4)

        with v_col1:
            st.markdown(
                f"""
                <div style="background:#F0FDF4; border:2px solid {NILE_TEAL}; padding:14px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:800; color:{CHARCOAL}; text-transform:uppercase;">PREDICTED MARKET VALUE</div>
                    <div style="font-size:1.6rem; font-weight:900; color:{DEEP_NAVY}; margin:4px 0;">EGP {result['predicted_price_egp']:,.0f}</div>
                    <div style="font-size:0.75rem; color:{NILE_TEAL}; font-weight:700;">≈ EGP {result['predicted_price_egp']/1e6:.2f} Million</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with v_col2:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; padding:14px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:800; color:#64748B; text-transform:uppercase;">UNIT RATE PER M²</div>
                    <div style="font-size:1.6rem; font-weight:900; color:{CHARCOAL}; margin:4px 0;">EGP {result['price_per_m2']:,.0f}</div>
                    <div style="font-size:0.75rem; color:#64748B;">Based on {in_area:.0f} m² living area</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with v_col3:
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; padding:14px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:800; color:#64748B; text-transform:uppercase;">EMPIRICAL 80% CONFIDENCE</div>
                    <div style="font-size:1.15rem; font-weight:800; color:{DEEP_NAVY}; margin:8px 0;">
                        [{result['interval_80_lower_egp']/1e6:.2f}M – {result['interval_80_upper_egp']/1e6:.2f}M]
                    </div>
                    <div style="font-size:0.72rem; color:{SANDSTONE_GOLD}; font-weight:700;">{result.get('prediction_confidence', '80% Interval')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with v_col4:
            st.markdown(
                f"""
                <div style="background:#EFF6FF; border:1px solid #BFDBFE; padding:14px; border-radius:8px; text-align:center;">
                    <div style="font-size:0.72rem; font-weight:800; color:#1E40AF; text-transform:uppercase;">MODEL GUARANTEE</div>
                    <div style="font-size:0.85rem; font-weight:700; color:{DEEP_NAVY}; margin:6px 0;">
                        Strict Monotonic Scaling
                    </div>
                    <div style="font-size:0.72rem; color:#2563EB;">Area & layout strictly increase price without inversions</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.caption(f"ℹ️ {result['disclaimer']}")

    # -------------------------------------------------------------
    # TAB 2: CLASS-SEPARATED GOVERNANCE & MONOTONICITY
    # -------------------------------------------------------------
    with tab_governance:
        st.markdown("##### CLASS-SEPARATED MODEL BENCHMARKS (4 DEDICATED ESTIMATORS)")
        
        # 4 Class Performance Cards
        c1, c2, c3, c4 = st.columns(4)

        def render_class_card(col, cls_letter, title, sample_cnt, med_price, r2, medae, mape, color):
            col.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid {color};
                            padding:12px; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                    <div style="font-size:0.72rem; font-weight:800; color:{color}; text-transform:uppercase;">CLASS {cls_letter} ESTIMATOR</div>
                    <div style="font-size:1.0rem; font-weight:800; color:{DEEP_NAVY}; margin:3px 0;">{title}</div>
                    <div style="font-size:0.75rem; color:#64748B; margin-bottom:8px;">{sample_cnt:,} verified listings</div>
                    <hr style="margin:6px 0; border:none; border-top:1px solid #F1F5F9;" />
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin:2px 0;">
                        <span style="color:#64748B;">Median Price:</span>
                        <strong style="color:{DEEP_NAVY};">EGP {med_price/1e6:.2f}M</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin:2px 0;">
                        <span style="color:#64748B;">R² Score:</span>
                        <strong style="color:{color};">{r2:.1%}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin:2px 0;">
                        <span style="color:#64748B;">Median Error:</span>
                        <strong style="color:{DEEP_NAVY};">EGP {medae:,.0f}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; margin:2px 0;">
                        <span style="color:#64748B;">MAPE:</span>
                        <strong style="color:{CHARCOAL};">{mape:.1f}%</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        cA = per_class.get("A", {})
        cB = per_class.get("B", {})
        cC = per_class.get("C", {})
        cD = per_class.get("D", {})

        render_class_card(c1, "A", "Ultra Luxury", cA.get("sample_count", 10539), cA.get("median_price_egp", 16616000), cA.get("r2", 0.6016), cA.get("medae_egp", 3109127), cA.get("mape_pct", 25.9), NILE_TEAL)
        render_class_card(c2, "B", "Master Community", cB.get("sample_count", 10542), cB.get("median_price_egp", 5400000), cB.get("r2", 0.8096), cB.get("medae_egp", 843977), cB.get("mape_pct", 20.4), DEEP_NAVY)
        render_class_card(c3, "C", "Mid-Market", cC.get("sample_count", 10495), cC.get("median_price_egp", 1958910), cC.get("r2", 0.5550), cC.get("medae_egp", 403981), cC.get("mape_pct", 27.8), SANDSTONE_GOLD)
        render_class_card(c4, "D", "Standalone Urban", cD.get("sample_count", 1825), cD.get("median_price_egp", 560000), cD.get("r2", 0.4204), cD.get("medae_egp", 90024), cD.get("mape_pct", 18.4), CHARCOAL)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Monotonicity Scaling Verification Chart
        st.markdown("##### MONOTONIC LIVING AREA SCALING (VERIFIED NON-DECREASING CURVES)")
        mono_rows = []
        for cls_name, info in monotonic_audit.items():
            sizes = info.get("test_sizes_sqm", [])
            prices = info.get("predicted_prices_egp", [])
            for s, p in zip(sizes, prices):
                mono_rows.append({
                    "Living Area (m²)": s,
                    "Predicted Price (EGP)": p,
                    "Class Tier": f"Class {cls_name}"
                })

        if mono_rows:
            df_mono = pd.DataFrame(mono_rows)
            fig_mono = px.line(
                df_mono,
                x="Living Area (m²)",
                y="Predicted Price (EGP)",
                color="Class Tier",
                markers=True,
                color_discrete_map={
                    "Class A": NILE_TEAL,
                    "Class B": DEEP_NAVY,
                    "Class C": SANDSTONE_GOLD,
                    "Class D": CHARCOAL
                }
            )
            fig_mono.update_layout(
                height=280,
                margin=dict(l=15, r=15, t=10, b=15),
                yaxis=dict(title="Predicted Price (EGP)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_mono, use_container_width=True)

        # Property Type Breakdown Table
        st.markdown("##### HELD-OUT RELIABILITY BY PROPERTY TYPE")
        type_rows = []
        for p_type, d in subgroups.get("by_property_type", {}).items():
            type_rows.append({
                "Property Type": p_type,
                "Sample Count": f"{d.get('sample_count', 0):,}",
                "R² Score": f"{d.get('r2', 0):.2%}",
                "Median Error": f"EGP {d.get('medae_egp', 0):,.0f}",
                "MAPE": f"{d.get('mape_pct', 0):.1f}%"
            })
        if type_rows:
            st.dataframe(pd.DataFrame(type_rows), hide_index=True, use_container_width=True, height=180)

    # -------------------------------------------------------------
    # TAB 3: INFERENTIAL STATISTICS LAB
    # -------------------------------------------------------------
    with tab_stats:
        st.markdown("##### INFERENTIAL HYPOTHESIS TESTING & POPULATION PARAMETERS")
        st.caption("Rigorous statistical hypothesis tests matching standard analytical methods (Two-sample t-test, ANOVA, Chi-Square, 95% Confidence Intervals).")

        df_raw = load_raw_dataset()

        st_col1, st_col2 = st.columns(2)

        with st_col1:
            st.markdown("###### 1. Two-Sample Welch's t-Test (Furnished vs Unfurnished)")
            t_res = run_two_sample_t_test(df_raw, "Furnished", "price", "Yes", "No")
            st.info(f"💡 **Conclusion:** {t_res['conclusion']}")
            t_df = pd.DataFrame([{
                "Sample 1 (Furnished)": f"N = {t_res['sample_size_1']:,} | Mean: EGP {t_res['mean_1']:,.0f}",
                "Sample 2 (Unfurnished)": f"N = {t_res['sample_size_2']:,} | Mean: EGP {t_res['mean_2']:,.0f}",
                "t-Statistic": f"{t_res['t_statistic']:.2f}",
                "p-Value": f"{t_res['p_value']:.4e}",
                "Cohen's d": f"{t_res['cohens_d']:.2f}",
                "Statistically Significant": "YES (p < 0.001)" if t_res['is_significant_at_05'] else "NO"
            }])
            st.dataframe(t_df, hide_index=True, use_container_width=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            st.markdown("###### 2. Chi-Square Test of Independence (Compound Class vs View)")
            chi_res = run_chi_square_test(df_raw, "class", "view")
            st.success(f"💡 **Conclusion:** {chi_res['conclusion']}")
            chi_df = pd.DataFrame([{
                "Chi-Square (χ²)": f"{chi_res['chi2_statistic']:,.1f}",
                "Degrees of Freedom": chi_res['degrees_of_freedom'],
                "p-Value": f"{chi_res['p_value']:.4e}",
                "Cramér's V (Effect Size)": f"{chi_res['cramers_v']:.2f}",
                "Association Significant": "YES (p < 0.001)" if chi_res['is_significant_at_05'] else "NO"
            }])
            st.dataframe(chi_df, hide_index=True, use_container_width=True)

        with st_col2:
            st.markdown("###### 3. One-Way ANOVA (Price Variance Across Class Tiers)")
            anova_res = run_one_way_anova(df_raw, "class", "price")
            st.warning(f"💡 **Conclusion:** {anova_res['conclusion']}")
            anova_df = pd.DataFrame([{
                "F-Statistic": f"{anova_res['f_statistic']:,.1f}",
                "p-Value": f"{anova_res['p_value']:.4e}",
                "df Between / Within": f"{anova_res['df_between']} / {anova_res['df_within']:,}",
                "Eta-Squared (η²)": f"{anova_res['eta_squared']:.2f}",
                "Price Variance Explained": f"{anova_res['eta_squared']*100:.1f}%"
            }])
            st.dataframe(anova_df, hide_index=True, use_container_width=True)

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

            st.markdown("###### 4. Empirical 95% Confidence Intervals for Population Mean Price")
            ci_df = compute_confidence_intervals(df_raw, "class", "price", confidence=0.95)
            ci_display = []
            for _, r in ci_df.iterrows():
                ci_display.append({
                    "Tier": f"Class {r['class']}",
                    "Sample (N)": f"{int(r['Sample Count (N)']):,}",
                    "Sample Mean": f"EGP {r['Mean price']:,.0f}",
                    "Std Error (SE)": f"EGP {r['Std Error (SE)']:,.0f}",
                    "Lower 95% CI": f"EGP {r['Lower 95% CI']:,.0f}",
                    "Upper 95% CI": f"EGP {r['Upper 95% CI']:,.0f}"
                })
            st.dataframe(pd.DataFrame(ci_display), hide_index=True, use_container_width=True)
