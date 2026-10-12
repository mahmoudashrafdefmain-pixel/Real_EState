# -*- coding: utf-8 -*-
import math
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import streamlit as st
from .config import (
    AVG_PROPERTY_PRICE,
    MINIMUM_AGE,
    MINIMUM_MONTHLY_NET_INCOME,
    MINIMUM_CASH_RATIO,
    MAX_INSTALLMENT_RATIO,
    MINIMUM_COMFORTABLE_PAYMENT_RATIO,
    ALLOWED_TERMS,
    MAXIMUM_LTV,
    MINIMUM_DOWN_PAYMENT_RATIO,
    PROJECT_FINANCING_RULES
)

# encapsulate monthly installment result supporting dual unpacked tuple
class MonthlyInstallmentResult(float):
    def __new__(cls, pmt: float, total_cost: float = 0.0, total_paid: float = 0.0):
        obj = super().__new__(cls, pmt)
        obj.pmt = pmt
        obj.total_cost = total_cost
        obj.total_paid = total_paid
        return obj

    def __iter__(self):
        return iter((self.pmt, self.total_cost, self.total_paid))

    def __getitem__(self, idx):
        return (self.pmt, self.total_cost, self.total_paid)[idx]

# validate customer profile against simulation minimum rules
def validate_customer_profile(
    profile: Dict[str, Any],
    rules: Optional[Dict[str, Any]] = None
) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    age = int(profile.get("age", 0))
    income = float(profile.get("monthly_income", profile.get("monthly_net_income", 0.0)))
    cash = float(profile.get("available_cash", profile.get("available_down_payment", 0.0)))
    comfort = float(profile.get("comfortable_payment", profile.get("user_comfortable_payment", 0.0)))
    term = profile.get("financing_term_years", profile.get("preferred_term_years", 15))

    if age < MINIMUM_AGE:
        reasons.append("Your age is below the minimum age required for this simulation.")

    if income < MINIMUM_MONTHLY_NET_INCOME:
        reasons.append("Your monthly net income is below the minimum income required by this simulation.")

    min_cash = round(income * MINIMUM_CASH_RATIO, 2)
    if cash < min_cash:
        shortfall = round(min_cash - cash, 2)
        reasons.append(
            f"Your available cash is below the minimum required amount for this simulation. "
            f"(Required minimum cash: EGP {min_cash:,.0f}, Your available cash: EGP {cash:,.0f}, Shortfall: EGP {shortfall:,.0f})"
        )

    min_comfort = round(income * MINIMUM_COMFORTABLE_PAYMENT_RATIO, 2)
    if comfort < min_comfort:
        diff = round(min_comfort - comfort, 2)
        reasons.append(
            f"Your selected comfortable monthly payment is below the minimum required payment level for this simulation. "
            f"(Minimum simulation payment: EGP {min_comfort:,.0f}, Your selected payment: EGP {comfort:,.0f}, Difference: EGP {diff:,.0f})"
        )

    try:
        term_val = int(term)
        if term_val not in ALLOWED_TERMS:
            reasons.append("Financing term must be either 15 Years or 20 Years.")
    except Exception:
        reasons.append("Financing term must be either 15 Years or 20 Years.")

    return len(reasons) == 0, reasons

# calculate maximum allowed monthly housing installment
def calculate_max_installment(
    monthly_income: float,
    max_installment_ratio: float = MAX_INSTALLMENT_RATIO
) -> float:
    if monthly_income <= 0:
        return 0.0
    return round(float(monthly_income * max_installment_ratio), 2)

# calculate minimum required available cash savings
def calculate_minimum_cash(
    monthly_income: float,
    min_cash_ratio: float = MINIMUM_CASH_RATIO
) -> float:
    if monthly_income <= 0:
        return 0.0
    return round(float(monthly_income * min_cash_ratio), 2)

# calculate maximum affordable financing principal from installment
def calculate_max_financing(
    max_installment: float,
    annual_rate: float,
    term_years: int
) -> float:
    if max_installment <= 0 or term_years <= 0:
        return 0.0
    r = (annual_rate / 100.0) / 12.0
    n = int(term_years * 12)
    if r == 0:
        return round(float(max_installment * n), 2)
    p = max_installment * (((1.0 + r) ** n) - 1.0) / (r * ((1.0 + r) ** n))
    return round(float(p), 2)

# calculate maximum affordable property price from limits
def calculate_max_property_price(
    available_cash: float,
    max_financing_amount: float,
    min_down_payment_ratio: float = MINIMUM_DOWN_PAYMENT_RATIO,
    max_ltv: float = MAXIMUM_LTV
) -> float:
    if available_cash <= 0:
        return 0.0
    price_by_cash = available_cash / min_down_payment_ratio if min_down_payment_ratio > 0 else 0.0
    price_by_loan = max_financing_amount / max_ltv if max_ltv > 0 else 0.0
    price_by_sum = available_cash + max_financing_amount
    max_p = min(price_by_cash, price_by_loan, price_by_sum)
    return round(float(max_p), 2)

# determine project simulation interest rate for apartment
def determine_simulation_interest_rate(
    property_price: float,
    customer_profile: Optional[Dict[str, Any]] = None,
    financing_term: int = 15,
    financing_amount: float = 0.0
) -> float:
    if property_price <= 3000000.0:
        base_rate = 8.0
    elif property_price <= AVG_PROPERTY_PRICE:
        base_rate = 10.5
    else:
        base_rate = 12.5

    cust = customer_profile or {}
    income = float(cust.get("monthly_income", cust.get("monthly_net_income", 35000.0)))
    debt = float(cust.get("existing_debt", cust.get("existing_monthly_debt", 0.0)))
    cash = float(cust.get("available_cash", cust.get("available_down_payment", 0.0)))
    age = int(cust.get("age", 32))

    rate = base_rate
    if income >= 50000.0:
        rate -= 0.5
    elif income < 30000.0:
        rate += 0.5

    dti = (debt / income) if income > 0 else 0.0
    if dti > 0.15:
        rate += 0.5

    if property_price > 0 and (cash / property_price) >= 0.30:
        rate -= 0.5

    if age > 50:
        rate += 0.5

    return round(float(np.clip(rate, 7.5, 14.5)), 2)

# calculate minimum required down payment for property
def calculate_required_down_payment(
    property_price: float,
    min_down_payment_ratio: float = MINIMUM_DOWN_PAYMENT_RATIO,
    max_ltv: float = MAXIMUM_LTV
) -> float:
    if property_price <= 0:
        return 0.0
    effective_ratio = max(min_down_payment_ratio, 1.0 - max_ltv)
    return round(float(property_price * effective_ratio), 2)

# calculate financing amount constrained by maximum ltv
def calculate_financing_amount(
    property_price: float,
    down_payment: float,
    max_ltv: float = MAXIMUM_LTV,
    max_property_value: Any = None
) -> Tuple[float, str]:
    if property_price <= 0:
        return 0.0, "INVALID_PRICE"
    if max_property_value and property_price > max_property_value:
        return 0.0, "PROPERTY_TOO_EXPENSIVE"
    unconstrained = property_price - down_payment
    max_allowed = property_price * max_ltv
    loan = min(unconstrained, max_allowed)
    if loan <= 0:
        return 0.0, "DOWN_PAYMENT_COVERS_PRICE"
    return round(float(loan), 2), "ELIGIBLE"

# calculate amortizing monthly installment using annuity formula
def calculate_monthly_installment(
    financing_amount: float = 0.0,
    annual_rate: float = 0.0,
    term_years: Optional[int] = None,
    term_months: Optional[int] = None,
    rate_type: str = "amortizing",
    principal: Optional[float] = None
) -> MonthlyInstallmentResult:
    p = float(principal if principal is not None else financing_amount)
    if term_months is not None:
        n = int(term_months)
    elif term_years is not None:
        n = int(term_years * 12)
    else:
        n = 180
    if p <= 0 or n <= 0:
        return MonthlyInstallmentResult(0.0, 0.0, 0.0)
    r = (annual_rate / 100.0) / 12.0
    if r == 0:
        pmt = round(float(p / n), 2)
        return MonthlyInstallmentResult(pmt, 0.0, round(float(p), 2))
    pmt = p * (r * ((1.0 + r) ** n)) / (((1.0 + r) ** n) - 1.0)
    tot_paid = pmt * n
    tot_cost = tot_paid - p
    return MonthlyInstallmentResult(round(float(pmt), 2), round(float(tot_cost), 2), round(float(tot_paid), 2))

# calculate total cumulative financing costs over term
def calculate_total_financing_cost(
    monthly_installment: float,
    term_years: int,
    financing_amount: float
) -> float:
    if monthly_installment <= 0 or term_years <= 0:
        return 0.0
    n = term_years * 12 if term_years <= 30 else term_years
    total_paid = monthly_installment * n
    return round(float(total_paid - financing_amount), 2)

# calculate certified income required for installment
def calculate_required_income(
    monthly_installment: float,
    max_installment_ratio: float = MAX_INSTALLMENT_RATIO
) -> float:
    if monthly_installment <= 0 or max_installment_ratio <= 0:
        return 0.0
    return round(float(monthly_installment / max_installment_ratio), 2)

# calculate monthly installment financing gap against budget
def calculate_financing_gap(
    monthly_installment: float,
    customer_max_installment: float
) -> float:
    return round(float(monthly_installment - customer_max_installment), 2)

# calculate required down payment gap against savings
def calculate_cash_gap(
    required_down_payment: float,
    customer_available_cash: float
) -> float:
    return round(float(required_down_payment - customer_available_cash), 2)

# calculate projected future property price over horizon
def calculate_expected_future_price(
    property_price: float,
    years: int = 10,
    annual_growth_rate: float = 0.08
) -> float:
    if property_price <= 0:
        return 0.0
    val = property_price * ((1.0 + annual_growth_rate) ** years)
    return round(float(val), 2)

# calculate projected investment gain net of costs
def calculate_expected_gain(
    expected_future_price: float,
    purchase_price: float,
    total_financing_cost: float = 0.0
) -> float:
    if expected_future_price <= 0 or purchase_price <= 0:
        return 0.0
    return round(float(expected_future_price - purchase_price - total_financing_cost), 2)

# generate transparent itemized match or decline explanations
def generate_match_reason(
    is_match: bool,
    installment_gap: float,
    cash_gap: float,
    price_gap: float,
    distance_km: Optional[float] = None
) -> List[str]:
    reasons: List[str] = []
    if is_match:
        reasons.append("Monthly installment is below your maximum allowed installment.")
        reasons.append("Required down payment is within your available cash.")
        reasons.append("Property price is within your estimated maximum property budget.")
        if distance_km is not None and not np.isnan(distance_km):
            reasons.append(f"Property is within {distance_km:.1f} km of your preferred location.")
    else:
        if installment_gap > 0:
            reasons.append(f"Monthly installment exceeds 30% of your monthly net income by EGP {installment_gap:,.0f}.")
        if cash_gap > 0:
            reasons.append(f"Required down payment exceeds available cash by EGP {cash_gap:,.0f}.")
        if price_gap > 0:
            reasons.append(f"Property price exceeds your calculated maximum property budget by EGP {price_gap:,.0f}.")
    return reasons

# evaluate individual property match against customer standard
def evaluate_property(
    property_data: Dict[str, Any],
    customer_standard: Dict[str, Any]
) -> Dict[str, Any]:
    price = float(property_data.get("Price_Numeric", property_data.get("price", 0.0)))
    max_price = float(customer_standard.get("maximum_affordable_property_price", 0.0))
    max_pmt = float(customer_standard.get("maximum_installment", 0.0))
    cash = float(customer_standard.get("available_cash", 0.0))
    term = int(customer_standard.get("financing_term_years", 15))

    rate = determine_simulation_interest_rate(price, customer_standard, term)
    down = calculate_required_down_payment(price)
    loan, _ = calculate_financing_amount(price, down)
    pmt_res = calculate_monthly_installment(loan, rate, term)
    pmt = float(pmt_res)
    tot_cost = calculate_total_financing_cost(pmt, term, loan)

    inst_gap = calculate_financing_gap(pmt, max_pmt)
    cash_gap = calculate_cash_gap(down, cash)
    price_gap = round(float(price - max_price), 2)

    is_valid_price = price > 0
    is_down_ok = down <= cash
    is_pmt_ok = pmt <= max_pmt
    is_price_ok = price <= max_price

    is_match = is_valid_price and is_down_ok and is_pmt_ok and is_price_ok
    status = "MATCH" if is_match else "NOT MATCHED"

    code = "NONE"
    fail_msg = "Matches your financing standard."
    if not is_valid_price:
        code = "MISSING_DATA"
        fail_msg = "Property price unavailable or invalid."
    elif not is_pmt_ok:
        code = "INSTALLMENT_TOO_HIGH"
        fail_msg = "Monthly installment exceeds 30% of your monthly net income."
    elif not is_down_ok:
        code = "DOWN_PAYMENT_TOO_HIGH"
        fail_msg = "The required down payment exceeds your available cash."
    elif not is_price_ok:
        code = "PROPERTY_TOO_EXPENSIVE"
        fail_msg = "The apartment price exceeds your calculated maximum property budget."

    reasons = generate_match_reason(is_match, inst_gap, cash_gap, price_gap)

    return {
        "property_price": price,
        "required_down_payment": down,
        "financing_amount": loan,
        "financing_rate": rate,
        "financing_term_years": term,
        "financing_term_months": term * 12,
        "monthly_installment": pmt,
        "total_financing_cost": tot_cost,
        "customer_match_status": status,
        "failure_reason_code": code,
        "failure_reason": fail_msg,
        "installment_gap": inst_gap,
        "cash_gap": cash_gap,
        "property_price_gap": price_gap,
        "match_reasons": reasons
    }

# rank matching properties using transparent ordering criteria
def rank_properties(
    df_matches: pd.DataFrame,
    sort_by: str = "Best Financial Fit"
) -> pd.DataFrame:
    df = df_matches.copy()
    if df.empty:
        return df

    if sort_by == "Highest Property Score":
        if "property_quality_value_score" in df.columns:
            return df.sort_values(by="property_quality_value_score", ascending=False)
        return df
    elif sort_by == "Lowest Property Score":
        if "property_quality_value_score" in df.columns:
            return df.sort_values(by="property_quality_value_score", ascending=True)
        return df
    elif sort_by == "Highest Air Quality Score":
        if "air_quality_score" in df.columns:
            return df.sort_values(by="air_quality_score", ascending=False)
        return df
    elif sort_by == "Highest Green Living Score":
        if "green_coverage_score" in df.columns:
            return df.sort_values(by="green_coverage_score", ascending=False)
        return df
    elif sort_by == "Highest Price Value Score":
        if "price_value_score" in df.columns:
            return df.sort_values(by="price_value_score", ascending=False)
        return df
    elif sort_by == "Highest Finishing Score":
        if "finishing_score" in df.columns:
            return df.sort_values(by="finishing_score", ascending=False)
        return df
    elif sort_by == "Lowest Price":
        return df.sort_values(by="Price_Numeric", ascending=True)
    elif sort_by == "Lowest Monthly Installment":
        return df.sort_values(by="monthly_installment", ascending=True)
    elif sort_by == "Lowest Down Payment":
        return df.sort_values(by="financing_down_payment", ascending=True)
    elif sort_by == "Lowest Price / m²":
        return df.sort_values(by="Calculated_Price_Per_Meter", ascending=True)
    elif sort_by == "Largest Area":
        return df.sort_values(by="Area", ascending=False)
    elif sort_by == "Closest Location":
        if "distance_from_selected_area" in df.columns:
            return df.sort_values(by="distance_from_selected_area", ascending=True)
        return df
    elif sort_by == "Highest Expected Gain":
        if "projected_gain" in df.columns:
            return df.sort_values(by="projected_gain", ascending=False)
        return df
    elif sort_by == "Highest Expected Gain %":
        if "expected_gain_pct" in df.columns:
            return df.sort_values(by="expected_gain_pct", ascending=False)
        return df
    else:
        sort_cols = []
        for col in ["installment_gap", "customer_cash_gap", "property_price_gap", "Price_Numeric"]:
            if col in df.columns:
                sort_cols.append(col)
        if sort_cols:
            return df.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
        return df

# build standardized customer financing profile and capacity
def build_customer_financing_standard(
    customer_profile: Dict[str, Any]
) -> Dict[str, Any]:
    income = float(customer_profile.get("monthly_income", customer_profile.get("monthly_net_income", 0.0)))
    cash = float(customer_profile.get("available_cash", customer_profile.get("available_down_payment", 0.0)))
    comfort = float(customer_profile.get("comfortable_payment", customer_profile.get("user_comfortable_payment", 0.0)))
    age = int(customer_profile.get("age", 30))
    marital = str(customer_profile.get("marital_status", "Single"))
    term_years = int(customer_profile.get("financing_term_years", customer_profile.get("preferred_term_years", 15)))
    term_months = term_years * 12
    location = str(customer_profile.get("preferred_location", "All Greater Cairo"))

    max_pmt = calculate_max_installment(income)
    benchmark_rate = determine_simulation_interest_rate(AVG_PROPERTY_PRICE, customer_profile, term_years)
    max_loan = calculate_max_financing(max_pmt, benchmark_rate, term_years)
    max_prop_price = calculate_max_property_price(cash, max_loan)
    min_cash_req = calculate_minimum_cash(income)
    min_comfort_pmt = round(income * MINIMUM_COMFORTABLE_PAYMENT_RATIO, 2)

    return {
        "age": age,
        "marital_status": marital,
        "monthly_income": income,
        "monthly_net_income": income,
        "available_cash": cash,
        "available_down_payment": cash,
        "comfortable_payment": comfort,
        "user_comfortable_payment": comfort,
        "maximum_installment": max_pmt,
        "financing_term_years": term_years,
        "financing_term_months": term_months,
        "maximum_affordable_financing": max_loan,
        "maximum_financing_amount": max_loan,
        "maximum_affordable_property_price": max_prop_price,
        "minimum_required_down_payment": min_cash_req,
        "minimum_cash_required": min_cash_req,
        "minimum_comfortable_payment": min_comfort_pmt,
        "simulated_rate": benchmark_rate,
        "benchmark_rate": benchmark_rate,
        "simulation_interest_rate_logic": "Tiered benchmark based on property price and profile risk",
        "preferred_location": location
    }

# vectorize customer financing simulation across property records
@st.cache_data(show_spinner=False)
def build_customer_matches_dataframe(
    df_clean: pd.DataFrame,
    customer_standard: Dict[str, Any]
) -> pd.DataFrame:
    df = df_clean.copy()
    prices = df["Price_Numeric"].fillna(0.0).values
    term_years = int(customer_standard.get("financing_term_years", 15))
    term_months = term_years * 12
    max_pmt = float(customer_standard.get("maximum_installment", 0.0))
    max_price = float(customer_standard.get("maximum_affordable_property_price", 0.0))
    cash = float(customer_standard.get("available_cash", 0.0))
    income = float(customer_standard.get("monthly_income", 0.0))
    debt = float(customer_standard.get("existing_debt", 0.0))
    age = int(customer_standard.get("age", 32))

    base_rates = np.where(prices <= 3000000.0, 8.0, np.where(prices <= AVG_PROPERTY_PRICE, 10.5, 12.5))
    cust_adj = 0.0
    if income >= 50000.0:
        cust_adj -= 0.5
    elif income < 30000.0:
        cust_adj += 0.5
    if (debt / income if income > 0 else 0.0) > 0.15:
        cust_adj += 0.5
    if age > 50:
        cust_adj += 0.5

    rates = np.clip(base_rates + cust_adj, 7.5, 14.5)
    down_payments = np.round(prices * 0.20, 2)
    loans = np.round(prices * 0.80, 2)

    r = (rates / 100.0) / 12.0
    n = term_months
    factor = (r * ((1.0 + r) ** n)) / (((1.0 + r) ** n) - 1.0)
    installments = np.round(loans * factor, 2)
    total_costs = np.round((installments * n) - loans, 2)

    inst_gaps = np.round(installments - max_pmt, 2)
    cash_gaps = np.round(down_payments - cash, 2)
    price_gaps = np.round(prices - max_price, 2)

    is_valid_prop = df["is_valid_property"].values
    pmt_ok = installments <= max_pmt
    down_ok = down_payments <= cash
    price_ok = prices <= max_price

    is_overall_match = is_valid_prop & pmt_ok & down_ok & price_ok

    reasons = []
    codes = []
    for i in range(len(df)):
        if not is_valid_prop[i]:
            codes.append("MISSING_DATA")
            reasons.append("Property lacks valid price or physical area records.")
        elif not pmt_ok[i]:
            codes.append("INSTALLMENT_TOO_HIGH")
            reasons.append(f"Monthly installment of EGP {installments[i]:,.0f} exceeds 30% income limit (EGP {max_pmt:,.0f}).")
        elif not down_ok[i]:
            codes.append("DOWN_PAYMENT_TOO_HIGH")
            reasons.append(f"Required down payment of EGP {down_payments[i]:,.0f} exceeds available cash (EGP {cash:,.0f}).")
        elif not price_ok[i]:
            codes.append("PROPERTY_TOO_EXPENSIVE")
            reasons.append(f"Property price of EGP {prices[i]:,.0f} exceeds your maximum property budget (EGP {max_price:,.0f}).")
        else:
            codes.append("NONE")
            reasons.append("Matches your financing standard.")

    df["financing_down_payment"] = down_payments
    df["financing_amount"] = loans
    df["financing_term_years"] = term_years
    df["financing_term_months"] = term_months
    df["financing_rate"] = np.round(rates, 2)
    df["monthly_installment"] = installments
    df["total_financing_cost"] = total_costs
    df["required_income"] = np.round(installments / MAX_INSTALLMENT_RATIO, 2)
    df["customer_max_installment"] = max_pmt
    df["customer_max_property_price"] = max_price
    df["customer_cash_available"] = cash
    df["customer_cash_gap"] = cash_gaps
    df["installment_gap"] = inst_gaps
    df["property_price_gap"] = price_gaps
    df["financing_status"] = np.where(is_overall_match, "ELIGIBLE", "INELIGIBLE")
    df["customer_match_status"] = np.where(is_overall_match, "MATCH", "NOT MATCHED")
    df["failure_reason_code"] = codes
    df["failure_reason"] = reasons

    if "distance_km" in df.columns:
        df["distance_from_selected_area"] = df["distance_km"]
    else:
        df["distance_from_selected_area"] = np.nan

    df["bank_term_years"] = term_years
    df["bank_interest_rate"] = np.round(rates, 2)
    df["bank_required_down_payment"] = down_payments
    df["bank_financing_amount"] = loans
    df["bank_monthly_installment"] = installments
    df["bank_total_financing_cost"] = total_costs
    df["bank_max_allowed_installment"] = max_pmt
    df["bank_installment_ratio"] = np.round((installments / (income if income > 0 else 1.0)) * 100.0, 1)
    df["bank_standard_status"] = np.where(is_overall_match, "PASSED", "DECLINED")
    df["bank_decline_reason"] = reasons
    df["required_income_single"] = df["required_income"]
    df["required_income_married"] = df["required_income"]
    df["match_status"] = df["customer_match_status"]
    df["eligible_single"] = is_overall_match
    df["eligible_married"] = is_overall_match

    return df

# legacy alias for bank standard dataframe processor
def apply_bank_standard_to_properties(
    df_clean: pd.DataFrame,
    monthly_income: float = 35000.0,
    available_cash: float = 600000.0,
    comfortable_payment: float = 10000.0,
    age: int = 32,
    existing_debt: float = 0.0
) -> pd.DataFrame:
    standard = build_customer_financing_standard({
        "monthly_income": monthly_income,
        "available_cash": available_cash,
        "comfortable_payment": comfortable_payment,
        "age": age,
        "existing_debt": existing_debt,
        "financing_term_years": 15
    })
    return build_customer_matches_dataframe(df_clean, standard)

# legacy alias for applicant eligibility evaluator
def evaluate_bank_applicant_eligibility(
    monthly_income: float,
    available_cash: float,
    comfortable_payment: float,
    age: int,
    existing_debt: float = 0.0
) -> Tuple[bool, List[str]]:
    return validate_customer_profile({
        "monthly_income": monthly_income,
        "available_cash": available_cash,
        "comfortable_payment": comfortable_payment,
        "age": age,
        "existing_debt": existing_debt
    })

# legacy alias for dynamic interest rate calculator
def calculate_bank_dynamic_rate(
    property_price: float,
    monthly_income: float = 35000.0,
    existing_debt: float = 0.0,
    available_cash: float = 600000.0,
    age: int = 32,
    avg_price: float = AVG_PROPERTY_PRICE
) -> float:
    return determine_simulation_interest_rate(
        property_price,
        {
            "monthly_income": monthly_income,
            "existing_debt": existing_debt,
            "available_cash": available_cash,
            "age": age
        }
    )

# legacy alias for financing dataframe calculator
calculate_financing_dataframe = apply_bank_standard_to_properties
