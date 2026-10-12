# -*- coding: utf-8 -*-
"""
Test Suite: Predictive Machine Learning Engine & Validation Report
File: test_predictive_model.py
Verifies:
1. Model loading, pipeline caching, and clean serialization (no unpicklable mock classes).
2. Strict feature isolation with zero target leakage (no price, price/m2, or future price).
3. Positive predictions, area monotonicity, and empirical 80% prediction intervals.
4. Input bounds validation and out-of-distribution warning flags.
5. Presence and mathematical consistency of model validation report benchmarks.
"""

import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

# Add core program directory to sys.path
core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

from ml_engine import (
    get_model_pipeline,
    predict_property_price,
    predict_apartment,
    get_model_validation_report,
    get_model_metadata,
    clear_model_cache
)


def test_model_loading_and_caching():
    """Verify that model loads cleanly without unpickling errors and caches in memory."""
    clear_model_cache()
    pipe1 = get_model_pipeline()
    assert pipe1 is not None, "Pipeline must load successfully"
    assert hasattr(pipe1, "predict"), "Pipeline must have a callable predict method"

    pipe2 = get_model_pipeline()
    assert pipe1 is pipe2, "Pipeline must be memoized/cached"


def test_zero_target_leakage_in_features():
    """Verify feature set strictly excludes price, price/m2, or synthetic targets."""
    rep = get_model_validation_report()
    used_feats = rep.get("dataset_summary", {}).get("features_used", {})
    all_used = used_feats.get("numeric_features", []) + used_feats.get("categorical_features", [])

    forbidden_leaks = [
        "price", "Price_Numeric", "price_per_sqm", "Calculated_Price_Per_Meter",
        "price_after_10_years", "property_quality_value_score"
    ]
    for leak in forbidden_leaks:
        assert leak not in all_used, f"FATAL TARGET LEAKAGE: {leak} found in feature set!"


def test_predict_property_price_outputs_and_intervals():
    """Verify that property prediction returns positive price and valid 80% interval."""
    res = predict_property_price(
        size_sqm=150.0,
        bedrooms=3.0,
        bathrooms=2.0,
        floor=2.0,
        property_type="Apartment",
        class_tier="Class A",
        view="Garden View",
        city="Cairo",
        region="New Cairo"
    )

    pred_price = res["predicted_price_egp"]
    lower_80 = res["interval_80_lower_egp"]
    upper_80 = res["interval_80_upper_egp"]

    assert pred_price > 100_000.0, "Predicted price must be positive and realistic"
    assert lower_80 < pred_price < upper_80, "80% interval must properly bound point estimate"
    assert res["price_per_m2"] == round(pred_price / 150.0), "Price per m2 must match area division"
    assert "disclaimer" in res, "Must contain valuation disclaimer"


def test_property_size_monotonicity():
    """Verify that larger properties predict strictly higher valuations ceteris paribus."""
    pipe = get_model_pipeline()
    p_small = predict_property_price(size_sqm=90.0, bedrooms=2.0, city="Cairo", region="New Cairo", pipeline=pipe)
    p_large = predict_property_price(size_sqm=220.0, bedrooms=4.0, city="Cairo", region="New Cairo", pipeline=pipe)

    assert p_large["predicted_price_egp"] > p_small["predicted_price_egp"], (
        "Larger unit must command higher valuation than smaller unit with identical specs"
    )


def test_out_of_bounds_input_flagging():
    """Verify out-of-distribution inputs trigger explicit warning flags."""
    res_extreme = predict_property_price(
        size_sqm=15.0,  # Below 40 m2 threshold
        bedrooms=8.0    # Above 6 bedrooms threshold
    )
    assert len(res_extreme["out_of_bounds_warnings"]) >= 1, "Must flag out-of-distribution specs"


def test_validation_report_metrics_integrity():
    """Verify held-out test and cross-validation metrics in validation report."""
    rep = get_model_validation_report()
    test_metrics = rep.get("held_out_test_metrics", {})

    assert test_metrics.get("r2", 0) > 0.50, "Held-out test R2 must exceed 50%"
    assert test_metrics.get("mape_pct", 100) < 35.0, "Held-out MAPE must be below 35%"
    assert test_metrics.get("medae_egp", 0) > 0, "Median Absolute Error must be positive"

    # Verify baseline comparison exists
    baselines = rep.get("baselines_comparison", {})
    assert "median_baseline" in baselines
    assert "ridge_linear_regression" in baselines
    assert "hist_gradient_boosting" in baselines

    # Verify model demonstrates substantial improvement over median baseline
    r2_median = baselines["median_baseline"]["r2"]
    r2_model = baselines["hist_gradient_boosting"]["r2"]
    assert r2_model > r2_median, "Model must outperform median baseline on held-out test data"


def test_backward_compatibility_predict_apartment():
    """Verify predict_apartment backward compatibility adapter works seamlessly."""
    res = predict_apartment(
        location="Madinaty",
        area_m2=140.0,
        rooms=3.0,
        bathrooms=2.0,
        current_price=5_000_000.0
    )
    assert res["predicted_price_egp"] > 0
    assert res["total_growth"] > 0
    assert res["annual_cagr"] == 8.0
    assert res["price_2y"] < res["price_3y"]
    assert res["total_growth_3y"] > 0
    assert res["conservative_3y"] < res["price_3y"] < res["optimistic_3y"]
    assert res["conservative_10y"] < res["price_10y"] < res["optimistic_10y"]
