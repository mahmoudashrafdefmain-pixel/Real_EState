# -*- coding: utf-8 -*-
import math
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from .data_loader import load_raw_dataset
from .data_validation import validate_and_normalize_properties
from .scoring_engine import build_property_score_dataframe
from .formatting import format_currency, format_area, inject_zero_scroll_css

# define executive theme color constants
DEEP_NAVY = "#1B2A4A"
NILE_TEAL = "#2A9D8F"
SANDSTONE_GOLD = "#E9B44C"
CORAL_RED = "#E85D4C"
SOFT_SAGE = "#8FB996"
CHARCOAL = "#264653"
LIGHT_BG = "#F8F9FA"

# load and cache complete scored real estate dataset
@st.cache_data(show_spinner=False)
def get_cached_dashboard_dataset() -> pd.DataFrame:
    df_raw = load_raw_dataset()
    df_norm = validate_and_normalize_properties(df_raw)
    df_scored = build_property_score_dataframe(df_norm)
    return df_scored

# render dynamic multi factor real estate intelligence dashboard
def render_dynamic_dashboard_page():
    inject_zero_scroll_css()

    df_full = get_cached_dashboard_dataset()
    total_market_count = len(df_full)

    # render executive market intelligence header banner
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {DEEP_NAVY} 0%, #2A4365 100%);
                    padding: 12px 20px; border-radius: 8px; margin-bottom: 12px; color: #FFFFFF;
                    display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div>
                <h2 style="margin: 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.3px;">
                    EGYPT REAL ESTATE INTELLIGENCE — DYNAMIC MARKET DASHBOARD
                </h2>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 2px;">
                    Multi-Factor Environmental & Quality Valuation Engine | Audited Dataset
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: rgba(233, 180, 76, 0.2); border: 1px solid {SANDSTONE_GOLD};
                             color: {SANDSTONE_GOLD}; padding: 4px 10px; border-radius: 20px;
                             font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">
                    {total_market_count:,} TOTAL LISTINGS
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # render streamlined high-impact market filter bar (reduced to essential drivers)
    with st.expander("STREAMLINED MARKET FILTER SUITE (4 Core Drivers)", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        with f_col1:
            all_cities = sorted(df_full["city"].dropna().unique().tolist())
            selected_cities = st.multiselect("1. Macro City", options=all_cities, default=all_cities[:3])
            if not selected_cities:
                selected_cities = all_cities

        with f_col2:
            all_classes = sorted(df_full["class"].dropna().unique().tolist())
            selected_classes = st.multiselect("2. Compound Class Tier", options=all_classes, default=[])

        with f_col3:
            all_types = sorted(df_full["property_type"].dropna().unique().tolist())
            selected_types = st.multiselect("3. Property Type", options=all_types, default=[])

        with f_col4:
            max_p = min(60.0, float(df_full["Price_Numeric"].max()) / 1_000_000.0)
            price_range = st.slider("4. Price Range (EGP Millions)", min_value=0.5, max_value=max_p, value=(0.5, max_p), step=0.5)

    # filter dataframe according to user selections
    df_filtered = df_full.copy()
    df_filtered = df_filtered[df_filtered["city"].isin(selected_cities)]

    if selected_classes:
        df_filtered = df_filtered[df_filtered["class"].isin(selected_classes)]

    if selected_types:
        df_filtered = df_filtered[df_filtered["property_type"].isin(selected_types)]

    df_filtered = df_filtered[
        (df_filtered["Price_Numeric"] >= price_range[0] * 1_000_000.0) &
        (df_filtered["Price_Numeric"] <= price_range[1] * 1_000_000.0)
    ]

    active_count = len(df_filtered)
    if active_count == 0:
        st.warning("No listings match the current filter selection. Please broaden your filter parameters.")
        return

    # calculate executive market key performance indicators
    active_pct = (active_count / total_market_count) * 100.0
    med_price = float(df_filtered["Price_Numeric"].median())
    med_ppm = float(df_filtered["Calculated_Price_Per_Meter"].median())
    avg_score = float(df_filtered["property_quality_value_score"].mean())
    avg_aqi = float(df_filtered["us_aqi"].mean())
    avg_green = float(df_filtered["green_coverage_pct"].mean())
    num_deserves = int((df_filtered["property_quality_value_score"] >= 65.0).sum())
    pct_deserves = (num_deserves / active_count) * 100.0 if active_count > 0 else 0.0

    # render executive key metric strip
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    def render_metric_box(col, title, value, subtext, color=DEEP_NAVY):
        col.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top: 3px solid {color};
                        padding: 10px 12px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.03);">
                <div style="font-size:0.68rem; font-weight:800; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;">
                    {title}
                </div>
                <div style="font-size:1.25rem; font-weight:800; color:{DEEP_NAVY}; margin: 2px 0;">
                    {value}
                </div>
                <div style="font-size:0.72rem; color:{color}; font-weight:600;">
                    {subtext}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    render_metric_box(kpi1, "Active Listings", f"{active_count:,}", f"{active_pct:.1f}% of Market", NILE_TEAL)
    render_metric_box(kpi2, "Median Price", f"EGP {med_price/1e6:.2f}M", "Active Sample Median", DEEP_NAVY)
    render_metric_box(kpi3, "Median Rate", f"EGP {med_ppm:,.0f}/m²", "Base Living Meter", CHARCOAL)
    render_metric_box(kpi4, "Average Quality", f"{avg_score:.1f} / 100", f"{num_deserves:,} ({pct_deserves:.0f}%) Deserve", NILE_TEAL)
    render_metric_box(kpi5, "Average Air AQI", f"{avg_aqi:.1f} AQI", "EPA Air Quality Index", SANDSTONE_GOLD)
    render_metric_box(kpi6, "Average Green Space", f"{avg_green:.1f}%", "Satellite Vegetation", SOFT_SAGE)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # render dynamic interactive visualization section
    c_left, c_right = st.columns(2)

    with c_left:
        # render price versus property quality score scatter matrix
        fig_scatter = px.scatter(
            df_filtered.head(1000),
            x="Calculated_Price_Per_Meter",
            y="property_quality_value_score",
            color="property_type",
            size="Area",
            hover_name="region",
            hover_data={
                "city": True,
                "Price_Numeric": ":,.0f",
                "us_aqi": ":.1f",
                "green_coverage_pct": ":.1f",
                "floor_score_band": True
            },
            title="Price per m² vs. Property Quality & Value Score",
            labels={
                "Calculated_Price_Per_Meter": "Price per m² (EGP)",
                "property_quality_value_score": "Quality & Value Score (/100)",
                "property_type": "Type"
            },
            color_discrete_sequence=[NILE_TEAL, DEEP_NAVY, SANDSTONE_GOLD, CORAL_RED, SOFT_SAGE, CHARCOAL]
        )
        fig_scatter.update_layout(
            height=340,
            margin=dict(l=15, r=15, t=35, b=15),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(size=11)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with c_right:
        # render regional benchmark comparison chart
        top_regions = df_filtered["region"].value_counts().head(8).index.tolist()
        df_top_reg = df_filtered[df_filtered["region"].isin(top_regions)]
        reg_summary = df_top_reg.groupby("region").agg({
            "Calculated_Price_Per_Meter": "median",
            "property_quality_value_score": "mean"
        }).reset_index()

        fig_bench = go.Figure()
        fig_bench.add_trace(go.Bar(
            x=reg_summary["region"],
            y=reg_summary["Calculated_Price_Per_Meter"],
            name="Median Price/m² (EGP)",
            marker_color=DEEP_NAVY,
            yaxis="y1"
        ))
        fig_bench.add_trace(go.Scatter(
            x=reg_summary["region"],
            y=reg_summary["property_quality_value_score"],
            name="Avg Score (/100)",
            marker_color=SANDSTONE_GOLD,
            mode="lines+markers",
            yaxis="y2"
        ))
        fig_bench.update_layout(
            title="Top Districts: Median Rate vs. Average Quality Score",
            height=340,
            margin=dict(l=15, r=15, t=35, b=15),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(title="Price per m² (EGP)", showgrid=True, gridcolor="#F1F5F9"),
            yaxis2=dict(title="Quality Score", overlaying="y", side="right", range=[40, 100]),
            legend=dict(orientation="h", y=1.12, x=0.0),
            font=dict(size=11)
        )
        st.plotly_chart(fig_bench, use_container_width=True)

    # render second row of environmental analysis and property type breakdown
    e_left, e_right = st.columns(2)

    with e_left:
        # render air quality index versus green space coverage by district
        env_reg = df_filtered.groupby("region").agg({
            "us_aqi": "mean",
            "green_coverage_pct": "mean",
            "property_quality_value_score": "count"
        }).reset_index().rename(columns={"property_quality_value_score": "listing_count"})
        env_reg = env_reg[env_reg["listing_count"] >= 5].head(15)

        fig_env = px.scatter(
            env_reg,
            x="green_coverage_pct",
            y="us_aqi",
            text="region",
            size="listing_count",
            title="Environmental Matrix: Green Coverage vs. Air Pollution Index",
            labels={
                "green_coverage_pct": "Green Coverage (%)",
                "us_aqi": "Air Quality Index (AQI - Lower is Cleaner)"
            },
            color="us_aqi",
            color_continuous_scale="Tealgrn_r"
        )
        fig_env.update_traces(textposition="top center")
        fig_env.update_layout(
            height=320,
            margin=dict(l=15, r=15, t=35, b=15),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(size=11)
        )
        st.plotly_chart(fig_env, use_container_width=True)

    with e_right:
        # render property type and class inventory distribution
        type_counts = df_filtered["property_type"].value_counts().reset_index()
        type_counts.columns = ["Property Type", "Count"]

        fig_types = px.bar(
            type_counts.head(7),
            x="Count",
            y="Property Type",
            orientation="h",
            title="Inventory Breakdown by Property Type",
            color="Count",
            color_continuous_scale=[[0, SOFT_SAGE], [1, DEEP_NAVY]]
        )
        fig_types.update_layout(
            height=320,
            margin=dict(l=15, r=15, t=35, b=15),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            yaxis=dict(autorange="reversed"),
            font=dict(size=11)
        )
        st.plotly_chart(fig_types, use_container_width=True)

    # render interactive property inventory table and score inspector
    st.markdown("<hr style='margin: 14px 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
            <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:{DEEP_NAVY};">
                INTERACTIVE PROPERTY INVENTORY & DETAILED FACTOR INSPECTOR
            </h3>
            <span style="font-size:0.78rem; color:#64748B;">
                Showing top 1,000 matches (Sorted by Quality & Value Score)
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    display_df = df_filtered.sort_values(by="property_quality_value_score", ascending=False)
    candidate_cols = [
        "property_type", "region", "city", "Price_Numeric", "Calculated_Price_Per_Meter",
        "Area", "Rooms", "Bathrooms_num", "floor_level", "class", "view",
        "us_aqi", "green_coverage_pct", "property_quality_value_score", "deserves_price_badge", "score_tier_label", "floor_score_band"
    ]
    cols_to_show = [c for c in candidate_cols if c in display_df.columns]

    st.dataframe(
        display_df[cols_to_show].head(1000),
        height=320,
        hide_index=False,
        column_config={
            "property_type": st.column_config.TextColumn("Type", width="small"),
            "region": st.column_config.TextColumn("District / Region", width="medium"),
            "city": st.column_config.TextColumn("City", width="small"),
            "Price_Numeric": st.column_config.NumberColumn("Price (EGP)", format="%d"),
            "Calculated_Price_Per_Meter": st.column_config.NumberColumn("Price/m²", format="%d"),
            "Area": st.column_config.NumberColumn("Area (m²)", format="%.0f"),
            "Rooms": st.column_config.NumberColumn("Beds", format="%d"),
            "Bathrooms_num": st.column_config.NumberColumn("Baths", format="%d"),
            "floor_level": st.column_config.NumberColumn("Floor", format="%.0f"),
            "class": st.column_config.TextColumn("Class"),
            "view": st.column_config.TextColumn("View"),
            "us_aqi": st.column_config.NumberColumn("AQI", format="%.1f"),
            "green_coverage_pct": st.column_config.NumberColumn("Green %", format="%.1f%%"),
            "property_quality_value_score": st.column_config.NumberColumn("Quality Score (/100)", format="%.0f"),
            "deserves_price_badge": st.column_config.TextColumn("Deserves Price? (≥65)", width="medium"),
            "score_tier_label": st.column_config.TextColumn("Score Tier"),
            "floor_score_band": st.column_config.TextColumn("Floor Assessment")
        },
        use_container_width=True
    )

    # render single unit score inspection deep dive
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            f"""
            <div style="background:#F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px 18px; margin-top: 8px;">
                <h4 style="margin:0 0 10px 0; color:{DEEP_NAVY}; font-size:1.05rem; font-weight:800;">
                    🔍 SINGLE UNIT DEEP-DIVE FACTOR INSPECTOR
                </h4>
                <p style="font-size:0.80rem; color:#475569; margin:0 0 12px 0;">
                    Select any unit row index from the active filtered inventory to inspect its multi-factor scoring calculation.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        top_indices = display_df.head(100).index.tolist()
        if top_indices:
            selected_idx = st.selectbox(
                "Select Listing Index to Inspect",
                options=top_indices,
                format_func=lambda idx: f"Row #{idx}: {display_df.loc[idx, 'property_type']} in {display_df.loc[idx, 'region']} — EGP {display_df.loc[idx, 'Price_Numeric']/1e6:.2f}M | Score: {display_df.loc[idx, 'property_quality_value_score']:.0f}/100"
            )

            unit = display_df.loc[selected_idx]
            u_score = unit["property_quality_value_score"]
            u_tier = unit["score_tier_label"]
            u_color = unit.get("score_tier_color", NILE_TEAL)
            u_is_bldg = unit["is_building_unit"]
            u_deserves = u_score >= 65.0
            deserves_bg = "#ECFDF5" if u_deserves else "#FEF2F2"
            deserves_border = "#10B981" if u_deserves else "#EF4444"
            deserves_text = "#065F46" if u_deserves else "#991B1B"
            deserves_badge = "✅ DESERVES ASKING PRICE (≥65)" if u_deserves else "❌ OVERPRICED FOR QUALITY (<65)"

            # render unit factor score breakdown grid
            u_col1, u_col2 = st.columns([1, 2])

            with u_col1:
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 2px solid {u_color}; border-radius: 8px; padding: 16px; text-align: center;">
                        <span style="font-size: 0.75rem; font-weight:800; color:#64748B; text-transform:uppercase;">TOTAL COMPOSITE SCORE</span>
                        <div style="font-size: 2.8rem; font-weight: 900; color: {u_color}; line-height: 1.1; margin: 4px 0;">
                            {u_score:.0f} <span style="font-size:1.2rem; color:#64748B;">/ 100</span>
                        </div>
                        <span style="background:{u_color}; color:#FFFFFF; padding: 3px 12px; border-radius: 20px; font-size:0.80rem; font-weight:700;">
                            {u_tier}
                        </span>
                        <div style="margin-top: 10px; background: {deserves_bg}; border: 1px solid {deserves_border}; border-radius: 6px; padding: 6px 8px;">
                            <span style="font-size:0.75rem; font-weight:800; color:{deserves_text}; display:block;">
                                {deserves_badge}
                            </span>
                        </div>
                        <div style="margin-top: 12px; font-size: 0.80rem; color: #475569; text-align: left; line-height: 1.4;">
                            <strong>Type:</strong> {unit['property_type']}<br>
                            <strong>Location:</strong> {unit['region']}, {unit['city']}<br>
                            <strong>Price:</strong> EGP {unit['Price_Numeric']:,.0f}<br>
                            <strong>Unit Rate:</strong> EGP {unit['Calculated_Price_Per_Meter']:,.0f}/m²<br>
                            <strong>Area:</strong> {unit['Area']:.0f} m² | {unit['Rooms']:.0f} Beds | {unit['Bathrooms_num']:.0f} Baths
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with u_col2:
                # factor 1 air quality
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 1px solid #E2E8F0; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700;">
                            <span>1. Air Quality (US AQI: {unit['us_aqi']:.1f})</span>
                            <span style="color:{NILE_TEAL};">{unit['air_quality_score']:.0f} / 25 pts</span>
                        </div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:2px;">{unit['air_quality_reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # factor 2 green space
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 1px solid #E2E8F0; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700;">
                            <span>2. Green Space Coverage ({unit['green_coverage_pct']:.1f}%)</span>
                            <span style="color:{NILE_TEAL};">{unit['green_coverage_score']:.0f} / 25 pts</span>
                        </div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:2px;">{unit['green_coverage_reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # factor 3 price value
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 1px solid #E2E8F0; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700;">
                            <span>3. Price Value vs. Local Benchmark (Ratio: {unit['price_ratio']:.2f}x)</span>
                            <span style="color:{NILE_TEAL};">{unit['price_value_score']:.0f} / 25 pts</span>
                        </div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:2px;">{unit['price_value_reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # factor 4 class and view
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 1px solid #E2E8F0; border-radius:6px; padding:8px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700;">
                            <span>4. Community Class, View & Furnishing ({unit['class']} | {unit['view']})</span>
                            <span style="color:{NILE_TEAL};">{unit['class_view_score']:.0f} / 25 pts</span>
                        </div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:2px;">{unit['class_view_reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # factor 5 floor level (conditional)
                if u_is_bldg and pd.notna(unit['floor_score']):
                    floor_display = f"{unit['floor_score']:.0f} / 25 pts"
                    floor_color = NILE_TEAL
                    floor_detail = unit['floor_score_reason']
                else:
                    floor_display = "EXCLUDED (No Penalty)"
                    floor_color = SANDSTONE_GOLD
                    floor_detail = "This property is a standalone / non-building unit (villa, townhouse, chalet). Under project domain rules, floor level is strictly excluded from its scoring system, and its score is calculated fairly out of the remaining factors (100% scale)."

                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border: 1px solid #E2E8F0; border-radius:6px; padding:8px 12px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700;">
                            <span>5. Floor Level Positioning</span>
                            <span style="color:{floor_color};">{floor_display}</span>
                        </div>
                        <div style="font-size:0.74rem; color:#64748B; margin-top:2px;">{floor_detail}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
