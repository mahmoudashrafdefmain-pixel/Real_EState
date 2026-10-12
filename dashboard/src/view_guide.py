# -*- coding: utf-8 -*-
"""
Egypt Real Estate Intelligence Platform
Module: view_guide.py
Purpose:
    Application User Manual & Comprehensive Dashboard Guide (Requirement 18).
    Provides structured, accessible documentation covering Sections A through I:
    A. Getting Started
    B. Dashboard Modes (Dynamic vs. Statistical)
    C. Navigation & Page Directory
    D. Filters & Controls
    E. Charts & Statistical Analysis
    F. Predictive Model
    G. Investment Feasibility Lab
    H. Understanding Results & Limitations
    I. Quick-Start Workflow
"""

import pandas as pd
import streamlit as st
from .formatting import inject_zero_scroll_css


DEEP_NAVY = "#1B2A4A"
NILE_TEAL = "#2A9D8F"
SANDSTONE_GOLD = "#E9B44C"
CORAL_RED = "#E85D4C"
SOFT_SAGE = "#8FB996"
CHARCOAL = "#264653"


def render_guide_page():
    """Renders the comprehensive Dashboard Guide & User Manual."""
    inject_zero_scroll_css()

    # Top Navigation Banner with Return to Workspace Button
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {DEEP_NAVY} 0%, #2A4365 100%);
                    padding: 14px 20px; border-radius: 8px; margin-bottom: 12px; color: #FFFFFF;
                    display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div>
                <h2 style="margin: 0; color: #FFFFFF; font-size: 1.35rem; font-weight: 800; letter-spacing: -0.3px;">
                    EGYPT REAL ESTATE INTELLIGENCE — DASHBOARD GUIDE & SYSTEM MANUAL
                </h2>
                <div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 2px;">
                    Comprehensive Architectural Manual, Controls Directory & Statistical Interpretation Guide
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: rgba(233, 180, 76, 0.25); border: 1px solid {SANDSTONE_GOLD};
                             color: {SANDSTONE_GOLD}; padding: 4px 12px; border-radius: 20px;
                             font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">
                    VERSION 2.0 AUDITED
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Return to Workspace Quick Button
    c_btn1, c_btn2 = st.columns([1, 4])
    with c_btn1:
        if st.button("⬅️ RETURN TO PREVIOUS PAGE", type="primary", use_container_width=True):
            prev_page = st.session_state.get("previous_active_page", "1. 🏦 Bank System & Financing Calculator")
            st.session_state["nav_page_selection"] = prev_page
            st.rerun()
    with c_btn2:
        st.caption("You are currently viewing the built-in system user manual. Use the button on the left to return to your analytical workspace at any time.")

    st.markdown("<hr style='margin: 10px 0 16px 0;'>", unsafe_allow_html=True)

    # Tabbed Navigation across the 9 Guide Sections A through I
    guide_tabs = st.tabs([
        "A. Getting Started",
        "B. Dashboard Modes",
        "C. Page Directory",
        "D. Filters & Controls",
        "E. Charts & Statistics",
        "F. Predictive Model",
        "G. Feasibility Lab",
        "H. Limitations & Caveats",
        "I. Quick-Start Workflow"
    ])

    # -------------------------------------------------------------
    # TAB A: GETTING STARTED
    # -------------------------------------------------------------
    with guide_tabs[0]:
        st.markdown("### 🏁 Section A: Getting Started")
        st.markdown(
            """
            #### 1. What is the Egypt Real Estate Intelligence Platform?
            The **Egypt Real Estate Intelligence Platform** is an institutional-grade decision support system 
            designed for residential property buyers, mortgage underwriters, real estate developers, and institutional 
            investors navigating the Egyptian housing market.
            
            #### 2. What Decisions Does It Support?
            - **Central Bank Mortgage Qualification**: Determines exact bank eligibility, loan ceiling, monthly installment burden, and Debt-to-Income (DTI) compliance under Central Bank of Egypt banking regulations.
            - **Price Justification & Fair Valuation**: Assesses whether a seller's asking price is justified based on a multi-factor hedonic scoring standard (evaluating rate/m² vs. regional benchmarks, compound class, floor level, satellite green space, and EPA air quality).
            - **Off-Plan Delivery Feasibility Underwriting**: Evaluates realistic Egyptian delivery cycles (2-year construction milestone, 3-year handover delivery), leveraged equity returns (ROI), and rental cash flows.
            - **Predictive Market Valuation**: Generates machine-learning estimated market prices with empirical 80% confidence intervals based purely on physical and geographic listing characteristics.

            #### 3. How to Begin Using the Platform:
            1. **First-Time Homebuyers & Borrowers**: Begin on **Page 1 (Bank System & Financing Calculator)** to establish your financing capacity and maximum affordable property price.
            2. **Market Researchers & Analysts**: Open **Page 2 (Dynamic Market & Quality Dashboard)** to filter 33,401 verified listings across Cairo, Giza, Alexandria, and coastal expansion zones.
            3. **Underwriters & Model Auditors**: Review **Page 3 (AI Valuation Model & Validation Report)** to inspect transparent cross-validation benchmarks and test live properties against our trained hedonic model.
            """
        )

    # -------------------------------------------------------------
    # TAB B: DASHBOARD MODES
    # -------------------------------------------------------------
    with guide_tabs[1]:
        st.markdown("### 🔄 Section B: Dashboard Modes")
        st.markdown(
            """
            The platform provides two distinct, complementary user modes tailored for different analytical workflows:
            """
        )
        mode_col1, mode_col2 = st.columns(2)
        with mode_col1:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid #2A9D8F; padding:16px; border-radius:8px;">
                    <h4 style="color:#1B2A4A; margin-top:0;">🌟 Dynamic Dashboard Mode (Streamlit & Operations)</h4>
                    <p style="font-size:0.82rem; color:#475569; line-height:1.5;">
                        <strong>Purpose:</strong> Interactive transactional decision-making, live mortgage simulation, inventory filtering, and customized valuation modeling.
                    </p>
                    <ul style="font-size:0.80rem; color:#334155; padding-left:18px;">
                        <li><strong>Target Audience:</strong> Homebuyers, mortgage loan officers, and active property seekers.</li>
                        <li><strong>Key Outputs:</strong> Personal financing certificate, matching inventory list, multi-factor property scores (0–100), and custom scenario bounds.</li>
                        <li><strong>Interaction:</strong> Full two-way reactivity with sliders, number inputs, dropdowns, and dynamic cross-filtering.</li>
                        <li><strong>How to Access:</strong> Launched via <code>run_streamlit.py</code> or the top navigation bar.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        with mode_col2:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-top:4px solid #E9B44C; padding:16px; border-radius:8px;">
                    <h4 style="color:#1B2A4A; margin-top:0;">📊 Statistical Dashboard Mode (Standalone BI Suite)</h4>
                    <p style="font-size:0.82rem; color:#475569; line-height:1.5;">
                        <strong>Purpose:</strong> Macroeconomic market exploration, econometric distributions, regional price density heatmaps, and cross-sectional comparisons.
                    </p>
                    <ul style="font-size:0.80rem; color:#334155; padding-left:18px;">
                        <li><strong>Target Audience:</strong> Real estate economists, portfolio managers, and institutional analysts.</li>
                        <li><strong>Key Outputs:</strong> 20 distinct analytical charts, 5 focused statistical slides, furnished price premiums, and spatial density maps.</li>
                        <li><strong>Interaction:</strong> Slide-based presentation, chart type togglers, and macro governorate slicing.</li>
                        <li><strong>How to Access:</strong> Switch via the top navigation switcher in <code>index.html</code> (click <strong>Statistics Suite</strong>).</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------------------------------------
    # TAB C: NAVIGATION & PAGE DIRECTORY
    # -------------------------------------------------------------
    with guide_tabs[2]:
        st.markdown("### 🗺️ Section C: Navigation & Page Directory")
        st.markdown(
            """
            This section documents every actual page and slide implemented in the application:
            """
        )
        st.markdown("#### 1. Streamlit Application Pages (Interactive Decision Engine)")
        pages_data = [
            {
                "Page Name": "1. 🏦 Bank System & Financing Calculator",
                "Primary Purpose": "Personal mortgage underwriting against CBE banking standards.",
                "Questions Answered": "Can I qualify for a loan? What is my maximum property budget? What is my monthly installment at 30% DTI?",
                "Principal Outputs": "Financing Approval/Decline Dossier, Max Affordable Price (EGP), Loan Amortization Schedule, Matching Pre-Approved Properties."
            },
            {
                "Page Name": "2. 🌟 Dynamic Market & Quality Dashboard",
                "Primary Purpose": "Interactive inventory filtering & multi-factor hedonic scoring across 33,401 listings.",
                "Questions Answered": "Which districts offer the highest quality per EGP? Does this unit deserve its asking price? Where is clean air located?",
                "Principal Outputs": "Adaptive Quality Scores (/100), Price/m² vs Score Scatter Matrix, Regional Rates vs Quality Benchmarks, Sortable Inventory Table."
            },
            {
                "Page Name": "3. 🤖 AI Valuation Model & Validation Report",
                "Primary Purpose": "Empirical model audit, baseline benchmarks, and live property price estimation.",
                "Questions Answered": "What is the true market price of this property? How accurate is the ML model? What is the 80% confidence interval?",
                "Principal Outputs": "Model Validation Dossier, Baseline Comparison Matrix, 5-Fold CV Scores, Subgroup Reliability Tables, Live Price Calculator."
            },
            {
                "Page Name": "4. 📖 Dashboard Guide & System Manual",
                "Primary Purpose": "Centralized documentation, control directory, and statistical interpretation guide.",
                "Questions Answered": "What do the buttons do? How should I interpret these charts? What are the limitations of the data?",
                "Principal Outputs": "Nine comprehensive user guide sections (A–I) with instant 1-click return to active workspace."
            }
        ]
        st.dataframe(pd.DataFrame(pages_data), hide_index=True, use_container_width=True)

        st.markdown("#### 2. Standalone HTML Dashboard Slides (Executive BI Presentation)")
        st.markdown(
            """
            - **Operations Section (8 Slides)**:
              1. *Executive Overview*: Macro market KPIs, property types, and median prices.
              2. *Geospatial Map*: Interactive Cairo & Giza location hubs with density and price heatmaps.
              3. *Price Dynamics & Drivers*: Rate per m² distributions and finishing breakdown.
              4. *Bank Financing & 3-Year Delivery Feasibility*: Customer qualification, CBE 30% DTI rules, and 3-year delivery equity simulator.
              5. *Approved Units*: Pre-approved bank candidates with Compare Top 3 units feature.
              6. *Affordability Matrix*: Salary vs. down payment reverse underwriting table.
              7. *Quality of Life*: EPA air quality index vs. satellite NDVI green vegetation.
              8. *Inventory Registry*: Complete 33,401 listing registry with **Inspect Modal** and **Side-by-Side Comparison Matrix**.
            - **Statistics Section (5 Slides / 20 Charts)**:
              1. *Slide 1 - Macro Overview*: Market composition, pricing gauges, regional shares, price tiers.
              2. *Slide 2 - Market Structure*: Rates by type, finishing premiums, furnished delta (+38%), area spreads.
              3. *Slide 3 - Physical Layout*: Bedroom distributions, bathroom ratios, view premiums, layout density.
              4. *Slide 4 - Spatial Hubs*: Listing volume by city, top rate hubs, compound penetration.
              5. *Slide 5 - Econometric Price Analysis*: Price histograms, price elasticity curves, boxplot spreads, correlation matrices.
            """
        )

    # -------------------------------------------------------------
    # TAB D: FILTERS & CONTROLS
    # -------------------------------------------------------------
    with guide_tabs[3]:
        st.markdown("### 🎛️ Section D: Filters & Controls")
        st.markdown(
            """
            Every filter in the platform adjusts the active sample size and dynamically recalibrates statistical KPIs:
            """
        )
        filters_data = [
            {
                "Control Name": "Macro City / Governorate",
                "Target Variable": "city",
                "Behavior": "Filters dataset to selected administrative governorates (Cairo, Giza, Alexandria, Red Sea, North Coast).",
                "Scope": "Page-Specific (Recalibrates district options dynamically)."
            },
            {
                "Control Name": "District / Sub-Region",
                "Target Variable": "region",
                "Behavior": "Restricts data to specific submarkets (New Cairo, Zayed, 6th of October, Maadi, etc.).",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Property Type",
                "Target Variable": "type",
                "Behavior": "Isolates specific architectural typologies (Apartment, Duplex, Penthouse, Standalone Villa, Townhouse, Studio).",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Compound Class Tier",
                "Target Variable": "class",
                "Behavior": "Filters by gated community standard: Class A (Ultra Luxury Gated), Class B (Master Planned), Class C (Urban Mid-Market), Class D (Standalone).",
                "Scope": "Shared."
            },
            {
                "Control Name": "Floor Positioning",
                "Target Variable": "floor",
                "Behavior": "Filters building units by floor position (Ground, Mid Floors 2-4, High Floors 5+), or isolates standalone villas where floor is excluded.",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Price Worthiness Gate",
                "Target Variable": "property_quality_value_score",
                "Behavior": "Restricts to units scoring ≥ 65 points ('Deserves Asking Price') or identifies overpriced properties (< 65 points).",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Price Range (M EGP)",
                "Target Variable": "Price_Numeric",
                "Behavior": "Sets lower and upper boundaries on total property purchase price in Millions of EGP.",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Living Area Range (m²)",
                "Target Variable": "size_sqm / Area",
                "Behavior": "Restricts unit physical size in square meters.",
                "Scope": "Page-Specific."
            },
            {
                "Control Name": "Monthly Income & Debt",
                "Target Variable": "Income / Debt Profile",
                "Behavior": "Calculates borrowing capacity under Central Bank 30% Debt-to-Income (DTI) ceiling.",
                "Scope": "Bank Page."
            }
        ]
        st.dataframe(pd.DataFrame(filters_data), hide_index=True, use_container_width=True)

    # -------------------------------------------------------------
    # TAB E: CHARTS & STATISTICAL ANALYSIS
    # -------------------------------------------------------------
    with guide_tabs[4]:
        st.markdown("### 📈 Section E: Charts & Statistical Analysis")
        st.markdown(
            """
            This section provides practical guidance on interpreting the statistical charts and metrics used throughout the dashboard:
            
            #### 1. Median vs. Mean in Real Estate
            - **Median Price**: The exact middle value when listings are ordered from lowest to highest. In Egyptian real estate, the median (EGP 4.80M) is far more representative of typical property transactions than the mean (EGP 10.46M).
            - **Mean Price**: Heavily skewed upward by multi-hundred-million-pound luxury mansions in Katameya Heights or coastal palaces in Ras El Hekma. Always use the **Median** for budgeting.
            
            #### 2. Scatter Plots & Parity Lines
            - **Price/m² vs. Quality Score**: Plots price on the horizontal axis and overall quality score on the vertical axis. Properties in the **top-left quadrant** represent superior investment value (high quality, below-average rate).
            - **Actual vs. Predicted 1:1 Parity Line**: In model validation, points lying along the dashed 45-degree diagonal represent perfect predictions. Points above indicate model under-prediction; points below indicate over-prediction.
            
            #### 3. Correlation Matrices (Structural vs. Total)
            - **Structural Matrix**: Evaluates dependencies between physical traits (Area, Bedrooms, Bathrooms, Floor, AQI) without total Price to avoid spurious collinearity.
            - **Overall Matrix**: Demonstrates that physical living area and gated compound status are the primary empirical drivers of total property valuation.
            
            #### 4. Environmental Quality Metrics
            - **US AQI (Air Quality Index)**: Standard EPA index measuring particulate pollution (PM2.5 and PM10). Lower numbers indicate cleaner air (0–50 is Good; 51–100 is Moderate; >100 is Unhealthy).
            - **Green Space %**: High-resolution satellite NDVI measurement of vegetation and landscaped parklands within 1km radius of the property location.
            """
        )

    # -------------------------------------------------------------
    # TAB F: PREDICTIVE MODEL
    # -------------------------------------------------------------
    with guide_tabs[5]:
        st.markdown("### 🤖 Section F: Predictive Model & Inferential Statistics")
        st.markdown(
            r"""
            #### 1. Class-Separated Hedonic Architecture
            Rather than pooling disparate luxury estates with budget apartments, the valuation engine deploys **4 dedicated, isolated estimators**:
            - **Class A Estimator**: Models gated communities and ultra-luxury developments ($R^2 \approx 71.4\%$, Median EGP 16.6M).
            - **Class B Estimator**: Models master-planned residential communities ($R^2 \approx 84.0\%$, Median EGP 5.4M).
            - **Class C Estimator**: Models mid-market urban developments ($R^2 \approx 63.4\%$, Median EGP 2.0M).
            - **Class D Estimator**: Models standalone budget urban properties (MedAE = EGP 90,024, Median EGP 560k).

            #### 2. Guaranteed Monotonic Price Scaling
            The engine mathematically enforces monotonic constraints on physical features (`monotonic_cst`):
            - As living area increases, predicted price cannot decrease.
            - Higher bedroom and bathroom counts strictly scale valuation upward.

            #### 3. Empirical Class-Specific 80% Prediction Intervals
            Uncertainty is calibrated specifically within each class tier based on held-out test residuals:
            - **Class A**: $[\text{Estimate} \times 0.689, \; \text{Estimate} \times 1.490]$
            - **Class B**: $[\text{Estimate} \times 0.718, \; \text{Estimate} \times 1.369]$
            - **Class C**: $[\text{Estimate} \times 0.651, \; \text{Estimate} \times 1.496]$
            - **Class D**: $[\text{Estimate} \times 0.753, \; \text{Estimate} \times 1.298]$

            #### 4. Inferential Statistics & Hypothesis Testing Lab
            Provides institutional statistical tests matching standard methodology:
            - **Welch's Two-Sample t-Test**: Tests furnished vs. unfurnished listings and gated vs. standalone pricing.
            - **One-Way ANOVA (F-Test)**: Measures variance explanation across compound tiers and macro governorates.
            - **Chi-Square Test of Independence**: Examines associations between categorical variables (tier vs. view orientation).
            - **Empirical 95% Confidence Intervals**: Population mean estimates per tier.
            """
        )

    # -------------------------------------------------------------
    # TAB G: INVESTMENT FEASIBILITY LAB
    # -------------------------------------------------------------
    with guide_tabs[6]:
        st.markdown("### 💼 Section G: Investment Feasibility Lab & 3-Year Delivery Simulator")
        st.markdown(
            """
            Located on **Slide 4** of the executive presentation, the simulator models realistic Egyptian off-plan delivery cycles:
            
            #### 1. Core Financial Metrics Calculated:
            - **Exit Valuation (3-Year Delivery)**: Projected property delivery valuation at Year 3 handover (with intermediate Year 2 milestone) compounded by empirical compound class appreciation.
            - **Equity Multiple (MOIC)**: Total cash returned divided by initial down payment cash equity invested.
            - **Compound Annual Growth Rate (CAGR)**: Annualized compounding rate over 3-year off-plan delivery window:
              $$\\text{CAGR} = (\\text{MOIC})^{1/3} - 1$$
            - **Leveraged Equity ROI**: Net equity return over initial down payment cash stake accounting for debt principal amortization.
            
            #### 2. Realistic Egyptian Handover Horizons
            Evaluates off-plan units across a 1 to 5 year holding window, highlighting the **2-Year Handover Milestone (Phase 1)** and **3-Year Full Delivery Handover (Phase 2)**.
            
            #### 3. Assumptions vs. Empirical Data:
            - **Empirical Base**: Initial property purchase price, rate per $m^2$, and historical compound class appreciation tiers.
            - **User Assumptions**: Down payment equity stake (10%–100%), mortgage tenure, and dynamic CBE interest rates.
            """
        )

    # -------------------------------------------------------------
    # TAB H: UNDERSTANDING RESULTS & LIMITATIONS
    # -------------------------------------------------------------
    with guide_tabs[7]:
        st.markdown("### ⚠️ Section H: Understanding Results & Limitations")
        st.markdown(
            """
            To use this platform responsibly, keep the following real-world market principles in mind:
            
            1. **Asking Prices vs. Closed Sales (Negotiation Haircut)**:
               - The dataset reflects digital portal listing prices. In the Egyptian market, completed transactions typically clear at a **5% to 10% cash negotiation discount** below listing price.
            2. **Correlation vs. Causation**:
               - Gated compounds correlate strongly with higher prices (+454% median delta). However, high prices are driven by integrated security, clubhouse amenities, infrastructure quality, and developer reputation—not simply the compound label itself.
            3. **Inflation & Currency Fluctuations**:
               - Rapid fluctuations in the Egyptian Pound (EGP) and construction inflation can alter developer replacement costs. Statistical models reflect current market clearing levels and require periodic recalibration.
            4. **Off-Plan Delivery Risks**:
               - Listings under development (2026–2030 handovers) carry construction schedule dependencies. Modeled future capital appreciation assumes successful, on-schedule project completion.
            """
        )

    # -------------------------------------------------------------
    # TAB I: QUICK-START WORKFLOW
    # -------------------------------------------------------------
    with guide_tabs[8]:
        st.markdown("### 🚀 Section I: Quick-Start Workflow")
        st.markdown(
            """
            Follow this 8-step workflow to make informed, data-backed real estate decisions:
            
            1. **Step 1: Choose Your Dashboard Mode**: Use Streamlit for interactive property search and financing; use the HTML dashboard for macro BI and slide presentations.
            2. **Step 2: Enter Your Financing Parameters** *(Page 1)*: Input your net income, available cash down payment, and preferred loan term to compute your strict Central Bank budget ceiling.
            3. **Step 3: Filter the Active Market** *(Page 2)*: Select target cities and districts to narrow down matching listings within your affordable price ceiling.
            4. **Step 4: Inspect Property Quality Scores**: Focus on units scoring **≥ 65 points** ('Deserves Asking Price') to avoid paying inflated premiums relative to local benchmarks.
            5. **Step 5: Run Independent Model Valuation** *(Page 3)*: Use the AI Valuation Simulator to generate an objective predicted price and inspect the 80% confidence interval.
            6. **Step 6: Underwrite Long-Term Returns** *(Feasibility Lab)*: If purchasing for investment, evaluate 10-year leveraged IRR and MOIC under conservative rental growth assumptions.
            7. **Step 7: Apply Negotiation Haircut**: When preparing an offer, factor in an anticipated 5%–10% negotiation discount from the asking price.
            8. **Step 8: Final Due Diligence**: Confirm title deed registration, developer track record, and on-site construction progress before executing contracts.
            """
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 RESUME ANALYSIS IN ACTIVE WORKSPACE", type="primary", use_container_width=True):
            prev_page = st.session_state.get("previous_active_page", "1. 🏦 Bank System & Financing Calculator")
            st.session_state["nav_page_selection"] = prev_page
            st.rerun()
