# -*- coding: utf-8 -*-
"""
Test Suite: Inferential Statistics & Class-Separated Valuation Suite
File: test_inferential_stats.py
Verifies:
1. Two-sample Welch's t-test executes and computes valid t-stat, p-value, and CI.
2. One-Way ANOVA computes valid F-stat, p-value, and effect size Eta-squared.
3. Pearson Chi-Square Test of Independence computes valid chi2-stat, dof, and Cramér's V.
4. Empirical 95% Confidence Intervals compute sample mean, SE, and proper bounds.
5. Class-Separated Valuation Suite maintains strict hierarchical pricing: Class A > B > C > D.
6. Living area monotonicity holds strictly non-decreasing across all tiers.
"""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

from src.inferential_statistics import (
    run_two_sample_t_test,
    run_one_way_anova,
    run_chi_square_test,
    compute_confidence_intervals,
    compute_correlation_matrix
)
from src.data_loader import load_raw_dataset
from ml_engine import predict_property_price, get_model_pipeline


def test_two_sample_welch_t_test():
    """Verify Welch's t-test computes valid test statistics."""
    df = load_raw_dataset()
    res = run_two_sample_t_test(df, "Furnished", "price", "Yes", "No")

    assert res["test_type"] == "Welch's Two-Sample t-test"
    assert res["sample_size_1"] > 0
    assert res["sample_size_2"] > 0
    assert 0.0 <= res["p_value"] <= 1.0
    assert res["ci_95_diff_lower"] < res["mean_difference"] < res["ci_95_diff_upper"]
    assert "conclusion" in res


def test_one_way_anova():
    """Verify One-Way ANOVA computes valid F-statistic and effect size."""
    df = load_raw_dataset()
    res = run_one_way_anova(df, "class", "price")

    assert res["test_type"] == "One-Way ANOVA (F-Test)"
    assert res["num_groups"] == 4
    assert res["f_statistic"] > 0.0
    assert 0.0 <= res["p_value"] <= 1.0
    assert 0.0 <= res["eta_squared"] <= 1.0
    assert "conclusion" in res


def test_chi_square_independence():
    """Verify Chi-Square test computes valid test statistics and contingency table."""
    df = load_raw_dataset()
    res = run_chi_square_test(df, "class", "view")

    assert res["test_type"] == "Pearson's Chi-Square Test of Independence"
    assert res["chi2_statistic"] > 0.0
    assert res["degrees_of_freedom"] > 0
    assert 0.0 <= res["p_value"] <= 1.0
    assert 0.0 <= res["cramers_v"] <= 1.0
    assert len(res["contingency_table"]) > 0


def test_confidence_intervals_bounds():
    """Verify 95% Confidence Interval calculations and mathematical ordering."""
    df = load_raw_dataset()
    ci_df = compute_confidence_intervals(df, "class", "price", confidence=0.95)

    assert len(ci_df) == 4
    for _, r in ci_df.iterrows():
        assert r["Lower 95% CI"] < r["Mean price"] < r["Upper 95% CI"]
        assert r["Std Error (SE)"] > 0


def test_correlation_matrix_properties():
    """Verify correlation matrices are symmetric and bounded [-1, 1]."""
    df = load_raw_dataset()
    pearson, spearman = compute_correlation_matrix(df)

    assert pearson.shape[0] == pearson.shape[1]
    assert np.all(pearson.values >= -1.0) and np.all(pearson.values <= 1.0)
    assert np.allclose(np.diag(pearson.values), 1.0)


def test_class_separated_pricing_hierarchy():
    """Verify that Class A > Class B > Class C > Class D for identical physical specifications."""
    p_a = predict_property_price(size_sqm=160, class_tier="Class A", property_type="Apartment")["predicted_price_egp"]
    p_b = predict_property_price(size_sqm=160, class_tier="Class B", property_type="Apartment")["predicted_price_egp"]
    p_c = predict_property_price(size_sqm=160, class_tier="Class C", property_type="Apartment")["predicted_price_egp"]
    p_d = predict_property_price(size_sqm=160, class_tier="Class D", property_type="Apartment")["predicted_price_egp"]

    assert p_a > p_b > p_c > p_d, f"Hierarchy violation: A={p_a}, B={p_b}, C={p_c}, D={p_d}"
    assert p_a > 8_000_000, "Class A 160m2 apartment must command luxury pricing (>8M EGP)"
    assert p_d < 1_000_000, "Class D 160m2 apartment must command budget pricing (<1M EGP)"


def test_class_monotonicity_all_tiers():
    """Verify that within every single class, size increases price non-decreasingly."""
    for cls in ["Class A", "Class B", "Class C", "Class D"]:
        p80 = predict_property_price(size_sqm=80, class_tier=cls, property_type="Apartment")["predicted_price_egp"]
        p160 = predict_property_price(size_sqm=160, class_tier=cls, property_type="Apartment")["predicted_price_egp"]
        p300 = predict_property_price(size_sqm=300, class_tier=cls, property_type="Apartment")["predicted_price_egp"]

        assert p80 <= p160 <= p300, f"Monotonicity violation in {cls}: 80m={p80}, 160m={p160}, 300m={p300}"
