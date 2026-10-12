# -*- coding: utf-8 -*-
import math
from typing import Dict, Any
import streamlit as st
import pandas as pd
import numpy as np

from .config import (
    AVG_PROPERTY_PRICE,
    MINIMUM_AGE,
    MINIMUM_MONTHLY_NET_INCOME,
    MINIMUM_CASH_RATIO,
    MINIMUM_COMFORTABLE_PAYMENT_RATIO,
    MAX_INSTALLMENT_RATIO,
    ALLOWED_TERMS,
    FINANCING_DISCLAIMER,
    PROJECT_FINANCING_RULES
)
from .data_loader import load_raw_dataset, load_neighborhood_coordinates
from .data_validation import validate_and_normalize_properties
from .scoring_engine import build_property_score_dataframe
from .view_score_modal import render_property_score_dialog, render_property_score_inline
from .financing_engine import (
    validate_customer_profile,
    build_customer_financing_standard,
    build_customer_matches_dataframe,
    rank_properties
)
from .location_engine import calculate_distance_vectorized, resolve_area_coordinates, get_location_catalog
from .formatting import format_currency, format_area, format_distance, inject_zero_scroll_css

# render bank rules and eligibility modal dialog
@st.dialog("Bank Eligibility, Decline & Approval Rules", width="large")
def show_bank_rules_dialog():
    st.info("All mortgage evaluations follow Central Bank guidelines and Egyptian banking lending standards. Below are the strict requirements, decline triggers, and approval calculations applied by the engine.")

    st.markdown("#### 1. Bare Minimum Requirements (Eligibility Gate)")
    rules_data = [
        {"Requirement": "Minimum Age", "Threshold": "21 Years", "Banking Rationale": "Legal credit majority in Egypt."},
        {"Requirement": "Monthly Net Income", "Threshold": "EGP 20,000", "Banking Rationale": "Credit solvency floor for long-term debt."},
        {"Requirement": "Available Cash", "Threshold": "At least 50% of Net Income", "Banking Rationale": "Mandatory liquid reserve buffer for closing fees."},
        {"Requirement": "Comfortable Payment", "Threshold": "At least 60% of Net Income", "Banking Rationale": "Committed living & housing affordability floor."},
        {"Requirement": "Max Monthly Installment", "Threshold": "Max 30% of Net Income", "Banking Rationale": "Central Bank Debt-to-Income (DTI) regulatory ceiling."},
        {"Requirement": "Minimum Down Payment", "Threshold": "20% of Property Price", "Banking Rationale": "Mandatory upfront customer cash equity."}
    ]
    st.table(pd.DataFrame(rules_data))

    st.markdown("#### 2. Decline Rules & Exact Rationale (Why the Bank Declines)")
    st.error("""
- **Underage (Age < 21):** Declined because the applicant is legally a minor under banking credit laws.
- **Low Income (Income < EGP 20,000):** Declined because the applicant falls below the solvency baseline needed to qualify for credit.
- **Insufficient Cash (Cash < 50% Income):** Declined with exact shortfall breakdown because liquid funds fail reserve adequacy.
- **Comfortable Payment < 60% Income:** Declined because declared payment capacity does not satisfy the minimum simulation standard.
- **Property Installment > 30% Income:** Property is marked **NOT MATCHED** because the monthly installment breaches the 30% DTI limit.
- **Property Price > Maximum Budget:** Property is marked **NOT MATCHED** because price exceeds total borrowing capacity plus cash equity.
- **Down Payment > Available Cash:** Property is marked **NOT MATCHED** because the required 20% down payment exceeds applicant's cash reserves.
""")

    st.markdown("#### 3. Customer Capacity & Approval Calculations")
    st.success("""
- **Maximum Monthly Installment:** `Monthly Net Income × 30%`
- **Approved Loan Capacity:** Present Value (PV) of maximum installment over 15 or 20 years at the simulated interest rate.
- **Maximum Affordable Property Price:** `Approved Loan Capacity + Available Cash Savings`
- **Required Down Payment:** `Property Price × 20%`
- **Monthly Installment:** Standard amortized mortgage formula `P × [r(1+r)^n] / [(1+r)^n - 1]`
""")

    st.markdown("#### 4. Simulated Dynamic Interest Rate & Terms")
    st.info("""
- **Financing Terms:** Strictly **15 Years** (if property price ≤ EGP 5,990,259) or **20 Years** (if property price > EGP 5,990,259).
- **Simulated Interest Rate:** Dynamically evaluated based on property price tier (8.0% to 12.5%) and adjusted for customer risk (-0.5% for high income, +0.5% for debt, etc.), bounded strictly between 7.5% and 14.5%.
""")

    if st.button("Close Rules Window", type="primary", use_container_width=True):
        st.rerun()

# render financing application primary decision page
def render_mortgage_financing_page():
    inject_zero_scroll_css()

    st.markdown("""<div style="background: linear-gradient(135deg, #1B2A4A 0%, #2A4365 100%); padding: 10px 18px; border-radius: 6px; margin-bottom: 8px; color: #FFFFFF; display:flex; justify-content:space-between; align-items:center;">
<div>
<h3 style="margin: 0; color: #FFFFFF; font-size: 1.25rem; font-weight: 800;">FINANCING APPLICATION</h3>
<div style="font-size: 0.80rem; color: #CBD5E1;">Bank Standard Customer Qualification & Matching Properties</div>
</div>
<div style="text-align:right; font-size:0.75rem; color:#E9B44C; font-weight:700;">
MIN AGE: 21 | MIN INCOME: 20K | DTI CAP: 30% | TERM: 15Y / 20Y
</div>
</div>""", unsafe_allow_html=True)

    df_raw = load_raw_dataset()
    df_coords = load_neighborhood_coordinates()
    df_clean = validate_and_normalize_properties(df_raw, df_coords)
    df_scored = build_property_score_dataframe(df_clean, df_coords)
    locations_list = ["All Greater Cairo"] + get_location_catalog(df_scored)[:80]
    types_list = ["All Property Types"] + sorted([t for t in df_scored["property_type"].dropna().unique().tolist() if t])

    tab_profile, tab_apartments = st.tabs(["📋 1. Profile & Bank Decision", "🏢 2. Matching Units & Price Ratings"])

    with tab_profile:
        col_form, col_decision = st.columns([1.05, 1.15], gap="medium")

        with col_form:
            st.markdown("##### YOUR INFORMATION")

            f_r1_c1, f_r1_c2 = st.columns(2)
            with f_r1_c1:
                age_val = st.number_input("Age (Min: 21)", min_value=18, max_value=75, value=int(st.session_state.get("age", 32)), step=1)
                st.session_state["age"] = age_val
            with f_r1_c2:
                m_opts = ["Single", "Married"]
                cur_m = st.session_state.get("marital_status", "Single")
                m_idx = 0 if cur_m == "Single" else 1
                marital_val = st.selectbox("Marital Status", options=m_opts, index=m_idx)
                st.session_state["marital_status"] = marital_val

            f_r2_c1, f_r2_c2 = st.columns(2)
            with f_r2_c1:
                income_val = st.number_input("Monthly Net (Min: EGP 20K)", min_value=5000.0, max_value=2000000.0, value=float(st.session_state.get("monthly_income", 35000.0)), step=2500.0)
                st.session_state["monthly_income"] = income_val
            with f_r2_c2:
                cash_val = st.number_input("Available Cash (Min: 50% Net)", min_value=1000.0, max_value=50000000.0, value=float(st.session_state.get("down_payment", st.session_state.get("available_cash", 600000.0))), step=25000.0)
                st.session_state["available_cash"] = cash_val
                st.session_state["down_payment"] = cash_val

            f_r3_c1, f_r3_c2 = st.columns(2)
            with f_r3_c1:
                comfort_default = max(22000.0, float(income_val * 0.60))
                comfort_val = st.number_input("Comfortable Payment (Min: 60% Net)", min_value=1000.0, max_value=1000000.0, value=float(st.session_state.get("user_max_payment", comfort_default)), step=1000.0)
                st.session_state["user_max_payment"] = comfort_val
                st.session_state["comfortable_payment"] = comfort_val
            with f_r3_c2:
                term_options = ["15 Years", "20 Years"]
                cur_term = st.session_state.get("financing_term_str", "15 Years")
                t_idx = 0 if cur_term == "15 Years" else 1
                term_str = st.selectbox("Financing Term", options=term_options, index=t_idx)
                st.session_state["financing_term_str"] = term_str
                term_years = 15 if term_str == "15 Years" else 20
                st.session_state["financing_term_years"] = term_years

            f_r4_c1, f_r4_c2 = st.columns(2)
            with f_r4_c1:
                cur_loc = st.session_state.get("preferred_location", "All Greater Cairo")
                loc_idx = locations_list.index(cur_loc) if cur_loc in locations_list else 0
                loc_val = st.selectbox("Preferred Location", options=locations_list, index=loc_idx)
                st.session_state["preferred_location"] = loc_val
            with f_r4_c2:
                cur_type = st.session_state.get("preferred_type", "All Property Types")
                type_idx = types_list.index(cur_type) if cur_type in types_list else 0
                type_val = st.selectbox("Property Type", options=types_list, index=type_idx)
                st.session_state["preferred_type"] = type_val

            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
            btn_c1, btn_c2 = st.columns([1.1, 1.1])
            with btn_c1:
                calc_clicked = st.button("CALCULATE MY FINANCING", type="primary", use_container_width=True)
            with btn_c2:
                rules_clicked = st.button("VIEW FINANCING RULES", type="secondary", use_container_width=True)

            if rules_clicked:
                show_bank_rules_dialog()

            if calc_clicked:
                st.session_state["has_calculated"] = True

        with col_decision:
            st.markdown("##### BANK DECISION & FINANCING STANDARD")

            if not st.session_state.get("has_calculated", False):
                with st.container(border=True):
                    st.markdown("### Awaiting Financing Simulation")
                    st.caption("Fill in your profile on the left and click **CALCULATE MY FINANCING** to determine your eligibility, maximum budget, and matching properties.")
                    st.info("Simulation Gates: Age ≥ 21 | Net Income ≥ EGP 20K | Cash Reserves ≥ 50% | Installment Cap: 30%")
            else:
                profile = {
                    "age": age_val,
                    "marital_status": marital_val,
                    "monthly_income": income_val,
                    "available_cash": cash_val,
                    "comfortable_payment": comfort_val,
                    "financing_term_years": term_years,
                    "preferred_location": loc_val
                }
                is_valid, decline_reasons = validate_customer_profile(profile, PROJECT_FINANCING_RULES)

                if not is_valid:
                    st.session_state["customer_status"] = "DECLINED"
                    with st.container(border=True):
                        st.error("### ✕ FINANCING SIMULATION: DECLINED")
                        st.markdown("**Your profile does not currently satisfy the minimum lending criteria:**")
                        for r in decline_reasons:
                            st.markdown(f"- **{r}**")
                        st.info("💡 **How to qualify:** Ensure your monthly net income is at least EGP 20,000, cash reserves meet 50% of income, and comfortable payment meets required thresholds.")
                else:
                    st.session_state["customer_status"] = "PASSED"
                    standard = build_customer_financing_standard(profile)
                    st.session_state["customer_financing_standard"] = standard

                    max_inst = float(standard.get("maximum_installment", 0.0))
                    max_price = float(standard.get("maximum_affordable_property_price", 0.0))
                    max_fin = float(standard.get("maximum_financing_amount", standard.get("maximum_affordable_financing", 0.0)))
                    min_cash = float(standard.get("minimum_cash_required", standard.get("minimum_required_down_payment", 0.0)))
                    sim_rate = float(standard.get("simulated_rate", standard.get("benchmark_rate", 10.5)))

                    with st.container(border=True):
                        st.success("### ✓ FINANCING PROFILE: PASSED")
                        st.caption("Pre-qualification approved. Customer financing standard established.")

                        m_c1, m_c2 = st.columns(2)
                        with m_c1:
                            st.metric("Max Monthly Installment", f"{format_currency(max_inst)}/mo", delta="30% DTI Cap", delta_color="normal")
                            st.metric("Approved Loan Capacity", format_currency(max_fin), delta=f"{term_years}Y @ {sim_rate:.1f}%", delta_color="off")
                        with m_c2:
                            st.metric("Max Property Budget", format_currency(max_price), delta="Loan + Cash Equity", delta_color="normal")
                            st.metric("Down Payment Equity", format_currency(cash_val), delta=f"Min: {format_currency(min_cash)}", delta_color="off")

                        st.info(f"📌 Rate: **{sim_rate:.1f}%** | Term: **{term_years} Years** — 👉 Click **'2. Matching Units & Price Ratings'** tab above to explore approved units and see which units deserve their price (Score ≥ 65)!")

                        # Quick price justification preview for top qualifying unit
                        matching_preview = df_scored[df_scored["Price_Numeric"] <= max_price]
                        if len(matching_preview) > 0:
                            top_deserving = matching_preview[matching_preview["property_quality_value_score"] >= 65.0]
                            num_top_deserve = len(top_deserving)
                            st.markdown(
                                f"""<div style="background:#F0FDF4; border:1px solid #86EFAC; border-radius:6px; padding:8px 12px; margin-top:8px;">
<strong style="color:#15803D; font-size:0.85rem;">⭐ Price Justification Summary:</strong>
<div style="font-size:0.80rem; color:#166534; margin-top:2px;">
<strong>{num_top_deserve:,} units</strong> within your max budget of {format_currency(max_price)} achieve a <strong>Score ≥ 65</strong> and are rated as <strong>DESERVING THEIR ASKING PRICE</strong>.
</div>
</div>""",
                                unsafe_allow_html=True
                            )

        st.caption(FINANCING_DISCLAIMER)

    with tab_apartments:
        if not st.session_state.get("has_calculated", False) or st.session_state.get("customer_status") != "PASSED":
            st.info("Complete your financing profile in Tab 1 and click CALCULATE MY FINANCING to view matching apartments.")
            st.caption(FINANCING_DISCLAIMER)
            return

        standard = st.session_state["customer_financing_standard"]

        df_working = df_scored.copy()
        if type_val != "All Property Types":
            df_working = df_working[df_working["property_type"] == type_val]
        if loc_val != "All Greater Cairo":
            t_lat, t_lon = resolve_area_coordinates(df_working, loc_val)
            if not np.isnan(t_lat) and not np.isnan(t_lon):
                df_working["distance_km"] = calculate_distance_vectorized(df_working, t_lat, t_lon)
            else:
                df_working["distance_km"] = np.nan
        else:
            df_working["distance_km"] = np.nan

        df_matches = build_customer_matches_dataframe(df_working, standard)
        st.session_state["df_customer_matches"] = df_matches

        matching_apartments = df_matches[df_matches["customer_match_status"] == "MATCH"].copy()
        num_matches = len(matching_apartments)
        num_deserve = int((matching_apartments["property_quality_value_score"] >= 65.0).sum())
        num_overpriced = num_matches - num_deserve
        pct_deserve = (num_deserve / num_matches * 100.0) if num_matches > 0 else 0.0

        st.markdown(
            f"""<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:10px 14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
<div>
<span style="font-size:0.80rem; color:#64748B; font-weight:700; text-transform:uppercase;">Bank Qualification:</span>
<strong style="font-size:1.05rem; color:#1B2A4A; margin-left:6px;">{num_matches:,} Units Fit Budget</strong>
</div>
<div style="display:flex; gap:10px; align-items:center;">
<div style="background:#E6F4EA; border:1px solid #34A853; border-radius:6px; padding:4px 10px; font-size:0.80rem; color:#137333; font-weight:700;">
⭐ Deserves Asking Price (Score ≥ 65): <strong>{num_deserve:,} units ({pct_deserve:.0f}%)</strong>
</div>
<div style="background:#FCE8E6; border:1px solid #EA4335; border-radius:6px; padding:4px 10px; font-size:0.80rem; color:#C5221F; font-weight:700;">
⚠️ Below 65 Benchmark: <strong>{num_overpriced:,} units</strong>
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

        top_c1, top_c2, top_c3, top_c4 = st.columns([1.5, 1.4, 0.9, 0.8])
        with top_c1:
            sort_opts = [
                "Highest Property Score",
                "Lowest Price",
                "Lowest Monthly Installment",
                "Lowest Down Payment",
                "Highest Air Quality Score",
                "Highest Green Living Score",
                "Highest Price Value Score",
                "Best Financial Fit",
                "Lowest Price / m²",
                "Largest Area"
            ]
            sort_choice = st.selectbox("Sort", options=sort_opts, index=0, label_visibility="collapsed")
        with top_c2:
            score_filter = st.selectbox(
                "Price Worthiness Filter",
                options=[
                    "All Budget Matches",
                    "⭐ Deserves Asking Price Only (Score ≥ 65)",
                    "⚠️ Overpriced / Below 65 Only",
                    "75+ High Quality Standard",
                    "85+ Exceptional Quality"
                ],
                index=0,
                label_visibility="collapsed"
            )
        with top_c3:
            view_mode = st.radio("Display View", options=["Table View", "Card View"], horizontal=True, label_visibility="collapsed")
        with top_c4:
            csv_export_cols = [
                "Location", "property_type", "Price_Numeric", "Area", "Calculated_Price_Per_Meter",
                "property_quality_value_score", "deserves_price_badge", "air_quality_score", "green_coverage_score",
                "price_value_score", "class_view_score", "floor_score", "score_tier_label",
                "financing_down_payment", "monthly_installment", "financing_rate", "financing_term_years"
            ]
            valid_export_cols = [c for c in csv_export_cols if c in matching_apartments.columns]
            csv_data = matching_apartments[valid_export_cols].to_csv(index=False).encode("utf-8")
            st.download_button("Export CSV", data=csv_data, file_name="matching_units_with_price_ratings.csv", mime="text/csv", use_container_width=True)

        # Apply price worthiness and score filters
        if "Deserves Asking Price Only" in score_filter:
            matching_apartments = matching_apartments[matching_apartments["property_quality_value_score"] >= 65.0]
        elif "Overpriced" in score_filter:
            matching_apartments = matching_apartments[matching_apartments["property_quality_value_score"] < 65.0]
        elif "75+" in score_filter:
            matching_apartments = matching_apartments[matching_apartments["property_quality_value_score"] >= 75.0]
        elif "85+" in score_filter:
            matching_apartments = matching_apartments[matching_apartments["property_quality_value_score"] >= 85.0]

        filtered_count = len(matching_apartments)
        df_sorted = rank_properties(matching_apartments, sort_by=sort_choice)

        if filtered_count == 0:
            st.warning("No units match your financial standard with the selected price worthiness filter.")
            st.info("Try selecting 'All Budget Matches' or adjusting your financial inputs in Tab 1.")
            st.caption(FINANCING_DISCLAIMER)
            return

        # Live Property Quality & Value Score Column Chart & Factor Inspection Panel
        st.markdown("##### 📊 PROPERTY QUALITY & VALUE SCORE — ADAPTIVE FACTOR SCORECARD")
        sel_c1, sel_c2 = st.columns([2.8, 1.2])
        with sel_c1:
            prop_indices = list(range(len(df_sorted)))
            def make_prop_label(idx):
                r = df_sorted.iloc[idx]
                worth_tag = "✅ Deserves Price" if r.get("property_quality_value_score", 0) >= 65.0 else "❌ Overpriced"
                p_type = str(r.get("property_type", "Unit"))
                return f"#{idx+1} | {p_type} in {r['Location']} | {format_currency(r['Price_Numeric'])} | Score: {r.get('property_quality_value_score', 0):.0f}/100 [{worth_tag}]"
            selected_mortgage_idx = st.selectbox(
                "Select Unit to inspect its factor score distribution & price justification verdict:",
                options=prop_indices,
                format_func=make_prop_label,
                key="selected_mortgage_prop_selector"
            )
        with sel_c2:
            st.info(f"Showing Unit #{selected_mortgage_idx + 1} of {len(df_sorted):,} sorted by **{sort_choice}**")

        selected_prop = df_sorted.iloc[selected_mortgage_idx]
        render_property_score_inline(selected_prop)

        st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)
        st.markdown(f"##### 📋 MATCHING UNITS INVENTORY ({len(df_sorted):,} UNITS)")

        if view_mode == "Table View":
            display_cols = [
                "Location", "property_type", "Price_Numeric", "Area", "Calculated_Price_Per_Meter",
                "property_quality_value_score", "deserves_price_badge",
                "air_quality_score", "green_coverage_score", "price_value_score", "class_view_score"
            ]
            if "floor_score" in df_sorted.columns:
                display_cols.append("floor_score")
            display_cols.extend([
                "financing_down_payment", "monthly_installment", "financing_rate",
                "financing_term_years"
            ])

            col_rename = {
                "Location": "Location",
                "property_type": "Type",
                "Price_Numeric": "Price (EGP)",
                "Area": "Area (m²)",
                "Calculated_Price_Per_Meter": "Price/m² (EGP)",
                "property_quality_value_score": "Score (/100)",
                "deserves_price_badge": "Deserves Price? (≥65)",
                "air_quality_score": "Air Quality (/25)",
                "green_coverage_score": "Green Space (/25)",
                "price_value_score": "Price Value (/25)",
                "class_view_score": "Class/View (/25)",
                "floor_score": "Floor (/25)",
                "financing_down_payment": "Down Payment (EGP)",
                "monthly_installment": "Installment (EGP)",
                "financing_rate": "Rate (%)",
                "financing_term_years": "Term (Yrs)"
            }
            valid_cols = [c for c in display_cols if c in df_sorted.columns]
            sub_table = df_sorted[valid_cols].rename(columns=col_rename)
            st.dataframe(sub_table, use_container_width=True, height=440)
        else:
            cards_per_page = 3
            total_pages = max(1, math.ceil(filtered_count / cards_per_page))
            if "page1_card_page" not in st.session_state:
                st.session_state["page1_card_page"] = 1

            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col1:
                if st.button("◀ Previous 3", disabled=(st.session_state["page1_card_page"] <= 1), use_container_width=True):
                    st.session_state["page1_card_page"] -= 1
                    st.rerun()
            with p_col2:
                st.markdown(f"<div style='text-align:center; padding-top:4px; font-weight:700; color:#1B2A4A; font-size:0.85rem;'>Page {st.session_state['page1_card_page']} of {total_pages} ({filtered_count:,} Available Units)</div>", unsafe_allow_html=True)
            with p_col3:
                if st.button("Next 3 ▶", disabled=(st.session_state["page1_card_page"] >= total_pages), use_container_width=True):
                    st.session_state["page1_card_page"] += 1
                    st.rerun()

            start_idx = (st.session_state["page1_card_page"] - 1) * cards_per_page
            page_cards = df_sorted.iloc[start_idx:start_idx + cards_per_page]

            card_cols = st.columns(len(page_cards))
            for i, (_, row) in enumerate(page_cards.iterrows()):
                with card_cols[i]:
                    comm_str = "Compound" if row.get("Amenities") == "B(Compound)" else "Urban"
                    tot_score = float(row.get("property_quality_value_score", 0.0))
                    tier_str = str(row.get("score_tier_label", "Moderate"))
                    tier_col = str(row.get("score_tier_color", "#1B2A4A"))
                    p_type = str(row.get("property_type", "Unit"))

                    deserves = bool(tot_score >= 65.0)
                    badge_bg = "#E6F4EA" if deserves else "#FCE8E6"
                    badge_border = "#34A853" if deserves else "#EA4335"
                    badge_color = "#137333" if deserves else "#C5221F"
                    badge_text = "✅ Deserves Price (Score ≥ 65)" if deserves else "❌ Overpriced (Score < 65)"

                    air_s = float(row.get("air_quality_score", 0.0))
                    green_s = float(row.get("green_coverage_score", 0.0))
                    price_s = float(row.get("price_value_score", 0.0))
                    finish_s = float(row.get("class_view_score", row.get("finishing_score", 0.0)))
                    floor_s = row.get("floor_score", np.nan)
                    floor_avail = bool(row.get("floor_available", False)) and pd.notna(floor_s)

                    with st.container(border=True):
                        st.markdown(
                            f"<div style='background:{badge_bg}; border:1px solid {badge_border}; color:{badge_color}; font-weight:800; font-size:0.75rem; padding:4px 8px; border-radius:4px; text-align:center; margin-bottom:6px;'>"
                            f"{badge_text}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"**{p_type} in {row['Location']}**")
                        st.markdown(
                            f"<div style='background:#F8FAFC; border:1px solid #CBD5E1; border-radius:6px; padding:6px 8px; margin-bottom:8px;'>"
                            f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                            f"<span style='font-size:0.75rem; font-weight:700; color:#1B2A4A;'>Quality Score:</span>"
                            f"<span style='font-size:0.90rem; font-weight:800; color:{tier_col};'>{tot_score:.0f} / 100 ({tot_score:.0f}%)</span>"
                            f"</div>"
                            f"<div style='display:grid; grid-template-columns:1fr 1fr; gap:4px; font-size:0.72rem;'>"
                            f"<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:3px 5px; border-radius:3px;'>"
                            f"<span style='color:#64748B;'>Air Quality:</span> <strong>{air_s:.0f} / 25</strong>"
                            f"</div>"
                            f"<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:3px 5px; border-radius:3px;'>"
                            f"<span style='color:#64748B;'>Green Living:</span> <strong>{green_s:.0f} / 25</strong>"
                            f"</div>"
                            f"<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:3px 5px; border-radius:3px;'>"
                            f"<span style='color:#64748B;'>Price Value:</span> <strong>{price_s:.0f} / 25</strong>"
                            f"</div>"
                            f"<div style='background:#FFFFFF; border:1px solid #E2E8F0; padding:3px 5px; border-radius:3px;'>"
                            f"<span style='color:#64748B;'>Class & View:</span> <strong>{finish_s:.0f} / 25</strong>"
                            f"</div>"
                            f"</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        st.caption(f"Price: **{format_currency(row['Price_Numeric'])}**")
                        st.metric("Installment", f"{format_currency(row['monthly_installment'])}/mo", delta=f"{row['financing_rate']:.1f}% ({int(row['financing_term_years'])}Y)")
                        st.caption(f"Down Payment: **{format_currency(row['financing_down_payment'])}**")
                        st.caption(f"Area: {format_area(row['Area'])} | {comm_str}")

                        if st.button("📋 Factor Breakdown", key=f"score_modal_page1_{start_idx + i}", use_container_width=True):
                            render_property_score_dialog(row)

                        with st.expander("Why this matched"):
                            st.write("• Installment within 30% DTI cap.")
                            st.write("• Down payment within cash savings.")
                            st.write("• Price within approved budget.")

        st.caption(FINANCING_DISCLAIMER)
