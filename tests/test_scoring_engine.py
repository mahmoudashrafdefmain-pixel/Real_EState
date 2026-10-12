# -*- coding: utf-8 -*-
import sys
from pathlib import Path
core_dir = Path(__file__).resolve().parent.parent / "dashboard"
if str(core_dir) not in sys.path:
    sys.path.insert(0, str(core_dir))

import math
import numpy as np
import pandas as pd
import pytest

from src.scoring_engine import (
    calculate_air_quality_score,
    calculate_green_coverage_score,
    calculate_price_value_score,
    calculate_class_view_score,
    calculate_floor_score,
    calculate_finishing_score,
    calculate_property_quality_score,
    build_property_score_dataframe
)
from src.config import PROPERTY_SCORE_STANDARD, NON_BUILDING_TYPES

# test factor 1 air quality score across threshold bands
def test_air_quality_score_all_bands():
    # pristine 0-50 (25 pts)
    s, b, r, av = calculate_air_quality_score(45.0)
    assert s == 25.0 and av is True

    # clean 51-65 (23 pts)
    s, b, r, av = calculate_air_quality_score(58.0)
    assert s == 23.0 and av is True

    # moderate 66-75 (20 pts)
    s, b, r, av = calculate_air_quality_score(70.0)
    assert s == 20.0 and av is True

    # acceptable 76-85 (15 pts)
    s, b, r, av = calculate_air_quality_score(80.0)
    assert s == 15.0 and av is True

    # missing/none handling
    s, b, r, av = calculate_air_quality_score(None)
    assert av is False

# test factor 2 green living score across all bands
def test_green_coverage_score_all_bands():
    # exceptional >= 25% (25 pts)
    s, b, r, av = calculate_green_coverage_score(30.0)
    assert s == 25.0 and av is True

    # high 15% - <25% (22 pts)
    s, b, r, av = calculate_green_coverage_score(18.0)
    assert s == 22.0 and av is True

    # medium 7% - <15% (18 pts)
    s, b, r, av = calculate_green_coverage_score(10.0)
    assert s == 18.0 and av is True

    # decimal scale 0.18 -> 18%
    s, b, r, av = calculate_green_coverage_score(0.18)
    assert s == 22.0 and av is True

# test factor 3 price value score relative to local median
def test_price_value_score_all_ratio_bands():
    median_ppm = 40000.0

    # deep value <= 0.80 (25 pts)
    s, rat, b, r, av = calculate_price_value_score(30000.0, median_ppm)
    assert s == 25.0 and rat == 0.75 and av is True

    # attractive value 0.81-0.90 (23 pts)
    s, rat, b, r, av = calculate_price_value_score(34000.0, median_ppm)
    assert s == 23.0 and rat == 0.85 and av is True

    # fair value 0.91-1.00 (21 pts)
    s, rat, b, r, av = calculate_price_value_score(38000.0, median_ppm)
    assert s == 21.0 and rat == 0.95 and av is True

    # premium 1.16-1.30 (10 pts)
    s, rat, b, r, av = calculate_price_value_score(48000.0, median_ppm)
    assert s == 10.0 and rat == 1.20 and av is True

# test factor 4 class and view quality score
def test_class_view_score():
    # Class A, Sea View, Furnished (12 + 9 + 4 = 25 pts)
    s, disp, r, av = calculate_class_view_score("Class A", "Sea View", "Yes")
    assert s == 25.0 and av is True

    # Class B, Garden View, Unfurnished (9 + 7 + 2 = 18 pts)
    s, disp, r, av = calculate_class_view_score("Class B", "Garden / Green View", "No")
    assert s == 18.0 and av is True

    # Class D, Street View, Unfurnished (3 + 4 + 2 = 9 pts)
    s, disp, r, av = calculate_class_view_score("Class D", "Street View", "No")
    assert s == 9.0 and av is True

# test factor 5 floor score and strict exclusion for non building units
def test_floor_score_rule():
    # building unit on floor 3 (middle floor -> 25 pts)
    s, b, r, av = calculate_floor_score(3.0, is_building_unit=True)
    assert s == 25.0 and av is True and "Optimal" in b

    # building unit on ground floor (17 pts)
    s, b, r, av = calculate_floor_score(0.0, is_building_unit=True)
    assert s == 17.0 and av is True

    # non building unit (e.g. villa, townhouse, chalet) -> STRICTLY EXCLUDED
    s, b, r, av = calculate_floor_score(None, is_building_unit=False)
    assert s is None and av is False and "Excluded" in b

    # non building unit even if floor number happens to be present -> STILL EXCLUDED
    s, b, r, av = calculate_floor_score(1.0, is_building_unit=False)
    assert s is None and av is False and "Excluded" in b

# test single property quality score for non building unit (villa)
def test_villa_quality_score_has_floor_excluded():
    villa_row = pd.Series({
        "property_type": "Villa",
        "Price_Numeric": 15000000.0,
        "Calculated_Price_Per_Meter": 30000.0,
        "Area": 500.0,
        "class": "Class A",
        "view": "Sea View",
        "Furnished": "Yes",
        "floor_level": np.nan,
        "is_building_unit": False,
        "us_aqi": 48.0,
        "green_coverage_pct": 28.0
    })

    res = calculate_property_quality_score(villa_row, area_median_ppm=40000.0)

    # floor must be strictly excluded without penalty
    assert res["floor_available"] is False
    assert math.isnan(res["floor_score"])
    assert "Excluded" in res["floor_score_band"]

    # max scores on 4 factors: Air(25) + Green(25) + Value(25) + Class/View(25) = 100
    assert res["air_quality_score"] == 25.0
    assert res["green_coverage_score"] == 25.0
    assert res["price_value_score"] == 25.0
    assert res["class_view_score"] == 25.0
    assert res["property_quality_value_score"] == 100.0
    assert res["score_tier_label"] == "Exceptional"
    assert "Excluded" in res["property_score_summary"]

# test single property quality score for building unit (apartment)
def test_apartment_quality_score_includes_floor():
    apt_row = pd.Series({
        "property_type": "Apartment",
        "Price_Numeric": 4000000.0,
        "Calculated_Price_Per_Meter": 24000.0,
        "Area": 160.0,
        "class": "Class A",
        "view": "Sea View",
        "Furnished": "Yes",
        "floor_level": 3.0,
        "is_building_unit": True,
        "us_aqi": 48.0,
        "green_coverage_pct": 28.0
    })

    res = calculate_property_quality_score(apt_row, area_median_ppm=30000.0)

    # floor must be included
    assert res["floor_available"] is True
    assert res["floor_score"] == 25.0
    assert res["property_quality_value_score"] == 100.0
    assert res["score_tier_label"] == "Exceptional"
    assert res["deserves_price"] is True
    assert "YES" in res["deserves_price_label"]

# test 65 point price justification rule
def test_65_point_price_justification_rule():
    high_score_row = pd.Series({
        "property_type": "Apartment",
        "Price_Numeric": 3000000.0,
        "Calculated_Price_Per_Meter": 20000.0,
        "Area": 150.0,
        "class": "Class A",
        "view": "Garden / Green View",
        "Furnished": "Yes",
        "floor_level": 3.0,
        "is_building_unit": True,
        "us_aqi": 50.0,
        "green_coverage_pct": 20.0
    })
    res_high = calculate_property_quality_score(high_score_row, area_median_ppm=25000.0)
    assert res_high["property_quality_value_score"] >= 65.0
    assert res_high["deserves_price"] is True
    assert "YES" in res_high["deserves_price_label"]

    low_score_row = pd.Series({
        "property_type": "Apartment",
        "Price_Numeric": 8000000.0,
        "Calculated_Price_Per_Meter": 80000.0,
        "Area": 100.0,
        "class": "Class D",
        "view": "Street View",
        "Furnished": "No",
        "floor_level": 10.0,
        "is_building_unit": True,
        "us_aqi": 110.0,
        "green_coverage_pct": 0.5
    })
    res_low = calculate_property_quality_score(low_score_row, area_median_ppm=30000.0)
    assert res_low["property_quality_value_score"] < 65.0
    assert res_low["deserves_price"] is False
    assert "NO" in res_low["deserves_price_label"]

# test vectorized scoring across mixed property types
def test_vectorized_scoring_mixed_dataframe():
    df = pd.DataFrame([
        {
            "property_type": "Villa",
            "Price_Numeric": 12000000.0,
            "Calculated_Price_Per_Meter": 30000.0,
            "Area": 400.0,
            "class": "Class B",
            "view": "Garden / Green View",
            "Furnished": "No",
            "floor_level": np.nan,
            "is_building_unit": False,
            "us_aqi": 68.0,
            "green_coverage_pct": 12.0,
            "city": "Cairo",
            "region": "New Cairo"
        },
        {
            "property_type": "Apartment",
            "Price_Numeric": 3500000.0,
            "Calculated_Price_Per_Meter": 25000.0,
            "Area": 140.0,
            "class": "Class B",
            "view": "Street View",
            "Furnished": "No",
            "floor_level": 2.0,
            "is_building_unit": True,
            "us_aqi": 72.0,
            "green_coverage_pct": 4.0,
            "city": "Cairo",
            "region": "New Cairo"
        }
    ])

    df_scored = build_property_score_dataframe(df)

    assert "property_quality_value_score" in df_scored.columns
    assert "floor_available" in df_scored.columns
    assert "deserves_price" in df_scored.columns
    assert "deserves_price_badge" in df_scored.columns
    assert df_scored.loc[0, "floor_available"] == False
    assert df_scored.loc[1, "floor_available"] == True
    assert 0 <= df_scored.loc[0, "property_quality_value_score"] <= 100
    assert 0 <= df_scored.loc[1, "property_quality_value_score"] <= 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
