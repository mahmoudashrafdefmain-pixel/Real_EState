# -*- coding: utf-8 -*-
"""
Verification and Test Suite for src/data_loader.py and src/data_validation.py
Tests:
1. Raw dataset loading from after_env.csv (33,401 records)
2. Normalization and property factor parsing
3. Non-building standalone detection (villa, townhouse, chalet)
4. Customer profile validation constraints
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Dynamically ensure core program directory is in sys.path
core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

from src.data_loader import load_raw_dataset
from src.data_validation import validate_and_normalize_properties, validate_customer_profile
from src.config import PROJECT_FINANCING_RULES, NON_BUILDING_TYPES

# test raw dataset loading
def test_load_raw_dataset():
    df = load_raw_dataset()
    assert isinstance(df, pd.DataFrame), "Raw dataset must be a DataFrame"
    assert len(df) >= 30000, f"Expected at least 30,000 listings, found {len(df)}"
    
    expected_cols = ["price", "type", "size_sqm", "city", "region", "view", "class", "air_quality", "green_space"]
    for col in expected_cols:
        assert col in df.columns, f"Expected column '{col}' in raw dataset"

# test normalization and factor cleaning
def test_validate_and_normalize_properties():
    df_raw = load_raw_dataset()
    df_norm = validate_and_normalize_properties(df_raw)
    
    assert len(df_norm) == len(df_raw), "Normalized DataFrame length must match raw length"
    assert "Price_Numeric" in df_norm.columns, "Price_Numeric must be present"
    assert "Calculated_Price_Per_Meter" in df_norm.columns, "Calculated_Price_Per_Meter must be present"
    assert "is_building_unit" in df_norm.columns, "is_building_unit flag must be present"
    assert "us_aqi" in df_norm.columns, "us_aqi must be present"
    assert "green_coverage_pct" in df_norm.columns, "green_coverage_pct must be present"
    
    # ensure price per meter is valid positive number where price and area exist
    valid_mask = df_norm["Price_Numeric"].notna() & (df_norm["Area"] > 0)
    assert (df_norm.loc[valid_mask, "Calculated_Price_Per_Meter"] > 0).all()

# test standalone property exclusion of building floor level
def test_standalone_unit_handling():
    df_raw = load_raw_dataset()
    df_norm = validate_and_normalize_properties(df_raw)
    
    # filter for standalone non-building types (villas, chalets, etc.)
    type_clean = df_norm["property_type"].astype(str).str.strip().str.lower()
    standalone_units = df_norm[type_clean.isin(NON_BUILDING_TYPES)]
    assert len(standalone_units) > 0, "Expected standalone property units in dataset"
    assert (~standalone_units["is_building_unit"]).all(), "Non-building units must not be classified as building units"

# test customer profile validation
def test_validate_customer_profile():
    rules = PROJECT_FINANCING_RULES
    
    valid_profile = {
        "monthly_net_income": 35000.0,
        "existing_monthly_debt": 3000.0,
        "available_down_payment": 600000.0,
        "user_comfortable_payment": 10000.0,
        "age": 32,
        "preferred_term_years": 15
    }
    is_valid, errors = validate_customer_profile(valid_profile, rules)
    assert is_valid is True, f"Expected profile to be valid, got errors: {errors}"
    assert len(errors) == 0

    # Underage profile
    invalid_age = valid_profile.copy()
    invalid_age["age"] = 18
    is_valid, errors = validate_customer_profile(invalid_age, rules)
    assert is_valid is False
    assert any("at least" in e for e in errors)

    # Debt exceeding income
    invalid_debt = valid_profile.copy()
    invalid_debt["existing_monthly_debt"] = 40000.0
    is_valid, errors = validate_customer_profile(invalid_debt, rules)
    assert is_valid is False
    assert any("exceeds monthly income" in e for e in errors)
