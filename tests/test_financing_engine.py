# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

from src.config import (
    AVG_PROPERTY_PRICE,
    MINIMUM_AGE,
    MINIMUM_MONTHLY_NET_INCOME,
    MINIMUM_CASH_RATIO,
    MAX_INSTALLMENT_RATIO,
    MINIMUM_COMFORTABLE_PAYMENT_RATIO,
    PROJECT_FINANCING_RULES
)
from src.financing_engine import (
    validate_customer_profile,
    calculate_max_installment,
    calculate_minimum_cash,
    calculate_max_financing,
    calculate_max_property_price,
    determine_simulation_interest_rate,
    calculate_required_down_payment,
    calculate_financing_amount,
    calculate_monthly_installment,
    calculate_total_financing_cost,
    calculate_required_income,
    calculate_financing_gap,
    calculate_cash_gap,
    calculate_expected_future_price,
    calculate_expected_gain,
    evaluate_property,
    rank_properties,
    build_customer_financing_standard,
    build_customer_matches_dataframe
)

# test scenario 1: applicant age below minimum age
def test_scenario_1_age_below_minimum():
    profile = {
        "age": 19,
        "monthly_income": 35000.0,
        "available_cash": 200000.0,
        "comfortable_payment": 22000.0,
        "financing_term_years": 15
    }
    is_valid, reasons = validate_customer_profile(profile)
    assert is_valid is False
    assert any("below the minimum age required" in r for r in reasons)

# test scenario 2: monthly income below twenty thousand egp
def test_scenario_2_income_below_minimum():
    profile = {
        "age": 30,
        "monthly_income": 18000.0,
        "available_cash": 200000.0,
        "comfortable_payment": 12000.0,
        "financing_term_years": 15
    }
    is_valid, reasons = validate_customer_profile(profile)
    assert is_valid is False
    assert any("below the minimum income required" in r for r in reasons)

# test scenario 3: available cash below fifty percent income
def test_scenario_3_cash_below_fifty_percent():
    profile = {
        "age": 30,
        "monthly_income": 40000.0,
        "available_cash": 15000.0,
        "comfortable_payment": 25000.0,
        "financing_term_years": 15
    }
    is_valid, reasons = validate_customer_profile(profile)
    assert is_valid is False
    assert any("below the minimum required amount" in r for r in reasons)

# test scenario 4: comfortable payment below sixty percent income
def test_scenario_4_comfortable_payment_below_sixty_percent():
    profile = {
        "age": 30,
        "monthly_income": 40000.0,
        "available_cash": 300000.0,
        "comfortable_payment": 20000.0,
        "financing_term_years": 15
    }
    is_valid, reasons = validate_customer_profile(profile)
    assert is_valid is False
    assert any("below the minimum required payment level" in r for r in reasons)

# test scenario 5: valid applicant profile passing all checks
def test_scenario_5_valid_customer_profile():
    profile = {
        "age": 32,
        "monthly_income": 35000.0,
        "available_cash": 600000.0,
        "comfortable_payment": 22000.0,
        "financing_term_years": 15,
        "marital_status": "Single"
    }
    is_valid, reasons = validate_customer_profile(profile)
    assert is_valid is True
    assert len(reasons) == 0
    standard = build_customer_financing_standard(profile)
    assert standard["maximum_installment"] == 10500.0
    assert standard["maximum_affordable_financing"] > 0
    assert standard["maximum_affordable_property_price"] > 0

# test scenario 6: property installment exceeding thirty percent cap
def test_scenario_6_property_installment_exceeds_cap():
    standard = {
        "monthly_income": 30000.0,
        "maximum_installment": 9000.0,
        "available_cash": 5000000.0,
        "maximum_affordable_property_price": 10000000.0,
        "financing_term_years": 15
    }
    property_data = {"Price_Numeric": 6000000.0}
    res = evaluate_property(property_data, standard)
    assert res["customer_match_status"] == "NOT MATCHED"
    assert res["failure_reason_code"] == "INSTALLMENT_TOO_HIGH"
    assert "exceeds 30%" in res["failure_reason"]

# test scenario 7: property price exceeding maximum budget
def test_scenario_7_property_price_exceeds_maximum():
    standard = {
        "monthly_income": 35000.0,
        "maximum_installment": 10500.0,
        "available_cash": 400000.0,
        "maximum_affordable_property_price": 2000000.0,
        "financing_term_years": 15
    }
    property_data = {"Price_Numeric": 2500000.0}
    res = evaluate_property(property_data, standard)
    assert res["customer_match_status"] == "NOT MATCHED"

# test scenario 8: required down payment exceeding available cash
def test_scenario_8_down_payment_exceeds_cash():
    standard = {
        "monthly_income": 50000.0,
        "maximum_installment": 15000.0,
        "available_cash": 100000.0,
        "maximum_affordable_property_price": 500000.0,
        "financing_term_years": 15
    }
    property_data = {"Price_Numeric": 1000000.0}
    res = evaluate_property(property_data, standard)
    assert res["customer_match_status"] == "NOT MATCHED"
    assert res["failure_reason_code"] == "DOWN_PAYMENT_TOO_HIGH"

# test scenario 9: valid matching property meeting standard
def test_scenario_9_valid_matching_property():
    standard = {
        "monthly_income": 50000.0,
        "maximum_installment": 15000.0,
        "available_cash": 1000000.0,
        "maximum_affordable_property_price": 3000000.0,
        "financing_term_years": 15
    }
    property_data = {"Price_Numeric": 1500000.0}
    res = evaluate_property(property_data, standard)
    assert res["customer_match_status"] == "MATCH"
    assert res["financing_amount"] == 1200000.0
    assert res["required_down_payment"] == 300000.0
    assert res["monthly_installment"] <= standard["maximum_installment"]

# test scenario 10: empty search results handling
def test_scenario_10_empty_results_handling():
    df_empty = pd.DataFrame(columns=["Price_Numeric", "Area", "Calculated_Price_Per_Meter"])
    res = rank_properties(df_empty)
    assert len(res) == 0

# test scenario 11: session memory profile standard reconstruction
def test_scenario_11_session_memory_reconstruction():
    profile = {
        "age": 35,
        "monthly_income": 45000.0,
        "available_cash": 800000.0,
        "comfortable_payment": 28000.0,
        "financing_term_years": 20
    }
    standard = build_customer_financing_standard(profile)
    assert standard["financing_term_years"] == 20
    assert standard["maximum_installment"] == 13500.0
    assert standard["available_cash"] == 800000.0

# test scenario 12: mortgage financing customer matching and eligibility
def test_scenario_12_mortgage_financing_property_matching():
    df_mock = pd.DataFrame({
        "Location": ["Zamalek", "Maadi"],
        "Price_Numeric": [1500000.0, 8000000.0],
        "is_valid_property": [True, True]
    })
    standard = {
        "monthly_income": 50000.0,
        "maximum_installment": 15000.0,
        "available_cash": 1000000.0,
        "maximum_affordable_property_price": 3000000.0,
        "financing_term_years": 15
    }
    df_evaluated = build_customer_matches_dataframe(df_mock, standard)
    assert "financing_status" in df_evaluated.columns
    matches = df_evaluated[df_evaluated["financing_status"] == "ELIGIBLE"]
    assert len(matches) == 1
    assert matches.iloc[0]["Location"] == "Zamalek"
    assert df_evaluated.loc[1, "financing_status"] == "INELIGIBLE"

# test zero interest installment calculation
def test_zero_interest_installment_calculation():
    pmt, cost, total = calculate_monthly_installment(principal=1200000.0, annual_rate=0.0, term_months=120)
    assert pmt == 10000.0
    assert cost == 0.0
    assert total == 1200000.0

# test normal reducing balance amortizing installment
def test_normal_amortizing_installment():
    pmt, cost, total = calculate_monthly_installment(principal=2000000.0, annual_rate=8.0, term_months=180)
    assert 19000.0 < pmt < 19200.0
    assert cost > 1400000.0

# test dynamic simulation rate calculation logic
def test_simulation_rate_logic():
    rate_low = determine_simulation_interest_rate(2500000.0, {"monthly_income": 35000.0})
    rate_high = determine_simulation_interest_rate(8000000.0, {"monthly_income": 35000.0})
    assert rate_low >= 7.5
    assert rate_high > rate_low

# test maximum affordable property price constraints
def test_max_property_price_constraints():
    price = calculate_max_property_price(available_cash=500000.0, max_financing_amount=2000000.0)
    assert price <= 2500000.0

# test reverse financing present value calculation
def test_reverse_financing_calculation():
    loan = calculate_max_financing(max_installment=10000.0, annual_rate=10.0, term_years=15)
    assert loan > 800000.0 and loan < 1200000.0

# test required income calculation for installment
def test_required_income_calculation():
    req = calculate_required_income(9000.0, max_installment_ratio=0.30)
    assert req == 30000.0

# test expected future price calculation with compounding
def test_expected_future_price_compounding():
    fut = calculate_expected_future_price(1000000.0, years=10, annual_growth_rate=0.08)
    assert fut > 2000000.0

# test expected gain calculation net of costs
def test_expected_gain_calculation():
    gain = calculate_expected_gain(expected_future_price=2500000.0, purchase_price=1000000.0, total_financing_cost=500000.0)
    assert gain == 1000000.0
