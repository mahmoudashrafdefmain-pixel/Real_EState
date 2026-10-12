# -*- coding: utf-8 -*-
import math
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import pandas as pd
import streamlit as st

from .config import (
    PROPERTY_SCORE_STANDARD,
    USER_FRIENDLY_FACTOR_NAMES,
    FACTOR_EDUCATIONAL_EXPLANATIONS,
    SCORE_TIERS,
    SCORE_DISCLAIMER,
    NON_BUILDING_TYPES
)

# calculate factor 1 air quality score out of 25 points
def calculate_air_quality_score(aqi: Optional[float]) -> Tuple[float, str, str, bool]:
    if aqi is None or (isinstance(aqi, float) and (math.isnan(aqi) or aqi < 0)):
        return 12.0, "Estimated Baseline", "Air quality data estimated from regional baseline standard.", False

    aqi_val = float(aqi)
    standards = PROPERTY_SCORE_STANDARD["air_quality"]
    for item in standards:
        if aqi_val <= item["max"]:
            score = float(item["score"])
            band = str(item["band"])
            label = str(item.get("label", band))
            reason = (
                f"The area AQI is {aqi_val:.1f} ({label}), placing it in the {band} band "
                f"and awarding {score:.0f} out of 25 Air Quality points."
            )
            return score, band, reason, True

    last = standards[-1]
    return float(last["score"]), str(last["band"]), f"The area AQI is {aqi_val:.1f}, placing it in {last['band']} band (0/25 pts).", True

# calculate factor 2 green space score out of 25 points
def calculate_green_coverage_score(coverage_pct: Optional[float]) -> Tuple[float, str, str, bool]:
    if coverage_pct is None or (isinstance(coverage_pct, float) and (math.isnan(coverage_pct) or coverage_pct < 0)):
        return 10.0, "Estimated Baseline", "Green space coverage estimated from regional baseline.", False

    pct_val = float(coverage_pct)
    if 0.0 < pct_val <= 1.0:
        pct_val = pct_val * 100.0

    standards = PROPERTY_SCORE_STANDARD["green_coverage"]
    for item in standards:
        if pct_val >= item["min"]:
            score = float(item["score"])
            band = str(item["band"])
            label = str(item.get("label", band))
            reason = (
                f"The district has {pct_val:.1f}% green coverage ({label}), placing it in "
                f"the {band} standard ({score:.0f}/25 pts)."
            )
            return score, band, reason, True

    last = standards[-1]
    return float(last["score"]), str(last["band"]), f"District has {pct_val:.1f}% green coverage (0/25 pts).", True

# calculate factor 3 price value score relative to area median
def calculate_price_value_score(
    price_per_m2: Optional[float],
    area_median_ppm: Optional[float] = None
) -> Tuple[float, float, str, str, bool]:
    if price_per_m2 is None or (isinstance(price_per_m2, float) and math.isnan(price_per_m2)) or price_per_m2 <= 0:
        return 14.0, 1.0, "Market Standard", "Price benchmark is not available.", False

    if area_median_ppm is None or (isinstance(area_median_ppm, float) and math.isnan(area_median_ppm)) or area_median_ppm <= 0:
        if price_per_m2 < 10.0:
            ratio = round(float(price_per_m2), 3)
            ppm = ratio * 35000.0
            med = 35000.0
        else:
            return 14.0, 1.0, "Market Standard", "Local area median benchmark is not available.", False
    else:
        ppm = float(price_per_m2)
        med = float(area_median_ppm)
        ratio = round(ppm / med, 3)

    standards = PROPERTY_SCORE_STANDARD["price_value"]
    for item in standards:
        if ratio <= item["max_ratio"]:
            score = float(item["score"])
            band = str(item["band"])
            diff_pct = abs((ratio - 1.0) * 100.0)
            if ratio < 1.0:
                rel_str = f"{diff_pct:.1f}% below local benchmark median"
            elif ratio > 1.0:
                rel_str = f"{diff_pct:.1f}% above local benchmark median"
            else:
                rel_str = "exactly matching local benchmark median"

            reason = (
                f"Unit priced at EGP {ppm:,.0f}/m², which is {rel_str} "
                f"(median: EGP {med:,.0f}/m²), scoring {score:.0f}/25 pts."
            )
            return score, ratio, band, reason, True

    last = standards[-1]
    return float(last["score"]), ratio, str(last["band"]), f"Price per m² ratio ({ratio:.2f}) exceeds benchmark (2/25 pts).", True

# calculate factor 4 compound class and view quality score out of 25 points
def calculate_class_view_score(
    prop_class: Optional[str],
    view: Optional[str],
    furnished: Optional[str]
) -> Tuple[float, str, str, bool]:
    c_raw = str(prop_class or "Class B").strip().upper()
    c_clean = c_raw.replace("CLASS", "").strip()
    cls_map = {"A": 12.0, "B": 9.0, "C": 6.0, "D": 3.0}
    c_score = cls_map.get(c_clean, 9.0)
    c_str = f"Class {c_clean}" if c_clean in cls_map else c_raw

    v_str = str(view or "Standard").strip().lower()
    if any(k in v_str for k in ["sea", "lagoon", "lake", "golf", "water"]):
        v_score = 9.0
        v_disp = "Premium Scenic View"
    elif any(k in v_str for k in ["garden", "green", "pool"]):
        v_score = 7.0
        v_disp = "Pleasant Green / Pool View"
    elif "open" in v_str:
        v_score = 6.0
        v_disp = "Open View"
    else:
        v_score = 4.0
        v_disp = "Standard / Street View"

    f_str = str(furnished or "No").strip().lower()
    f_score = 4.0 if f_str in ["yes", "1", "true"] else 2.0
    total = round(c_score + v_score + f_score, 1)

    reason = (
        f"Community {c_str} ({c_score:.0f} pts) paired with {v_disp} ({v_score:.0f} pts) "
        f"and {'furnished' if f_score == 4.0 else 'unfurnished'} status ({f_score:.0f} pts)."
    )
    return total, f"{c_str} / {v_disp}", reason, True

# calculate factor 5 floor level score for building units
def calculate_floor_score(
    floor: Optional[float],
    is_building_unit: bool
) -> Tuple[Optional[float], str, str, bool]:
    if not is_building_unit or floor is None or (isinstance(floor, float) and math.isnan(floor)):
        return (
            None,
            "Excluded (Standalone / Non-Building Unit)",
            "Floor level is excluded from scoring as this property is a standalone / non-building unit.",
            False
        )

    fl = float(floor)
    standards = PROPERTY_SCORE_STANDARD.get("floor_standards", [])
    for item in standards:
        if item["min_fl"] <= fl <= item["max_fl"]:
            score = float(item["score"])
            label = str(item["label"])
            reason = f"Floor {fl:.0f} qualifies as {label} ({score:.0f}/25 pts)."
            return score, label, reason, True

    if 2.0 <= fl <= 4.0:
        return 25.0, "Optimal Middle Floor", f"Floor {fl:.0f} provides optimal light, privacy, and noise buffer (25/25 pts).", True
    elif fl in (1.0, 5.0):
        return 21.0, "Preferred Floor", f"Floor {fl:.0f} provides convenient accessibility (21/25 pts).", True
    elif fl == 0.0:
        return 17.0, "Ground Floor", "Ground floor unit with private ground access (17/25 pts).", True
    return 14.0, f"Floor {fl:.0f}", f"Floor {fl:.0f} positioned in upper building tier (14/25 pts).", True

# calculate finishing score maintained for legacy compatibility
def calculate_finishing_score(finishing_raw: Optional[str]) -> Tuple[float, str, str, str, bool]:
    if finishing_raw is None or (isinstance(finishing_raw, float) and math.isnan(finishing_raw)):
        return 14.0, "semi", "Semi Finished", "Finishing specification baseline standard.", False

    raw_str = str(finishing_raw).strip().lower()
    clean_key = raw_str.replace("-", " ").replace("_", " ").strip()

    mapping = PROPERTY_SCORE_STANDARD.get("finishing", {})
    if clean_key in mapping:
        entry = mapping[clean_key]
        score = float(entry["score"])
        disp = str(entry["display"])
        reason = f"Classified as {disp} ({score:.0f}/25 pts)."
        return score, clean_key, disp, reason, True

    if "super" in clean_key:
        return 24.0, "superlux", "Super Lux", "Super Lux specification (24/25 pts).", True
    elif "semi" in clean_key:
        return 14.0, "semi", "Semi Finished", "Semi Finished specification (14/25 pts).", True
    elif "without" in clean_key or "unfinish" in clean_key or "brick" in clean_key:
        return 3.0, "without", "Unfinished", "Core and shell brick state (3/25 pts).", True
    elif "lux" in clean_key:
        return 22.0, "lux", "Lux", "Lux specification (22/25 pts).", True

    return 14.0, clean_key, clean_key.title(), f"Mapped to baseline standard (14/25 pts).", True

# calculate composite property quality and value score for single property
def calculate_property_quality_score(
    property_row: pd.Series,
    area_median_ppm: float
) -> Dict[str, Any]:
    aqi_val = property_row.get("us_aqi", np.nan)
    green_val = property_row.get("green_coverage_pct", np.nan)
    ppm_val = property_row.get("Calculated_Price_Per_Meter", np.nan)
    prop_class = property_row.get("class", "Class B")
    view_val = property_row.get("view", "Standard / Not Specified")
    furnished_val = property_row.get("Furnished", "No")
    floor_val = property_row.get("floor_level", property_row.get("Floor Level", np.nan))
    is_building = bool(property_row.get("is_building_unit", False))

    s_air, b_air, r_air, av_air = calculate_air_quality_score(aqi_val)
    s_green, b_green, r_green, av_green = calculate_green_coverage_score(green_val)
    s_price, rat_price, b_price, r_price, av_price = calculate_price_value_score(ppm_val, area_median_ppm)
    s_cv, disp_cv, r_cv, av_cv = calculate_class_view_score(prop_class, view_val, furnished_val)
    s_floor, b_floor, r_floor, av_floor = calculate_floor_score(floor_val, is_building)

    # adapt composite score calculation based on building status using empirical data-driven hedonic weights
    # calibrated from canonical Egyptian real estate market distributions (after_env.csv)
    if av_floor and s_floor is not None:
        # Building unit (Apartment/Duplex/Penthouse):
        # 35% Price Value, 35% Class & View, 10% Floor Level, 10% Air Quality, 10% Green Space
        total_score = round((s_price * 0.35 + s_cv * 0.35 + s_floor * 0.10 + s_air * 0.10 + s_green * 0.10) * 4.0, 1)
        strongest_candidates = {
            "Price Value": s_price,
            "Class & View": s_cv,
            "Floor Level": s_floor,
            "Air Quality": s_air,
            "Green Space": s_green
        }
    else:
        # Non-building unit (Villa/Townhouse/Chalet): floor is excluded without penalty;
        # weights re-scaled across the 4 factors (38.9% Price Value, 38.9% Class & View, 11.1% Air, 11.1% Green)
        total_score = round(((s_price * 0.35 + s_cv * 0.35 + s_air * 0.10 + s_green * 0.10) / 0.90) * 4.0, 1)
        strongest_candidates = {
            "Price Value": s_price,
            "Class & View": s_cv,
            "Air Quality": s_air,
            "Green Space": s_green
        }

    total_score = float(max(0.0, min(100.0, total_score)))
    total_pct = total_score

    tier_label = "Entry / Developing"
    tier_color = "#C5221F"
    for t in SCORE_TIERS:
        if total_score >= t["min"]:
            tier_label = str(t["label"])
            tier_color = str(t["color"])
            break

    max_v = max(strongest_candidates.values())
    min_v = min(strongest_candidates.values())
    strongest = [k for k, v in strongest_candidates.items() if v == max_v]
    weakest = [k for k, v in strongest_candidates.items() if v == min_v]

    strongest_str = ", ".join([f"{f} ({strongest_candidates[f]:.0f}/25)" for f in strongest])
    weakest_str = ", ".join([f"{f} ({strongest_candidates[f]:.0f}/25)" for f in weakest])

    prop_type_label = str(property_row.get("property_type", "Unit"))
    if not av_floor:
        floor_note = "Floor factor: Excluded (Standalone / Non-building property)."
    else:
        floor_note = f"Floor level: {s_floor:.0f}/25 pts ({b_floor})."

    deserves_price = bool(total_score >= 65.0)
    deserves_label = "YES (Deserves Price)" if deserves_price else "NO (Overpriced for Quality)"
    deserves_badge = "✅ Deserves Price" if deserves_price else "❌ Overpriced"
    deserves_verdict = (
        f"✅ DESERVES ASKING PRICE: Score {total_score:.0f}/100 meets or exceeds the 65-point benchmark (Fair Value / High Quality)."
        if deserves_price else
        f"❌ DOES NOT DESERVE ASKING PRICE: Score {total_score:.0f}/100 is below the 65-point benchmark (Overpriced for Delivered Quality)."
    )

    summary = (
        f"This {prop_type_label} scored {total_score:.0f}/100 ({tier_label}). "
        f"Price Justification: {deserves_label}. "
        f"Strongest factor: {strongest_str}. {floor_note}"
    )

    return {
        "air_quality_value": aqi_val if av_air else np.nan,
        "air_quality_score": s_air,
        "air_quality_band": b_air,
        "air_quality_reason": r_air,
        "air_quality_available": av_air,

        "green_coverage_value": green_val if av_green else np.nan,
        "green_coverage_score": s_green,
        "green_coverage_band": b_green,
        "green_coverage_reason": r_green,
        "green_coverage_available": av_green,

        "price_per_m2": ppm_val if av_price else np.nan,
        "area_median_price_per_m2": area_median_ppm,
        "price_ratio": rat_price,
        "price_value_score": s_price,
        "price_value_band": b_price,
        "price_value_reason": r_price,
        "price_value_available": av_price,

        "class_view_display": disp_cv,
        "class_view_score": s_cv,
        "class_view_reason": r_cv,
        "class_view_available": av_cv,
        "finishing_score": s_cv,

        "floor_score": s_floor if av_floor else np.nan,
        "floor_score_band": b_floor,
        "floor_score_reason": r_floor,
        "floor_available": av_floor,
        "is_building_unit": is_building,

        "deserves_price": deserves_price,
        "deserves_price_label": deserves_label,
        "deserves_price_badge": deserves_badge,
        "deserves_price_verdict": deserves_verdict,

        "property_quality_value_score": total_score,
        "property_quality_percentage": total_pct,
        "score_tier_label": tier_label,
        "score_tier_color": tier_color,
        "strongest_factor": strongest_str,
        "weakest_factor": weakest_str,
        "property_score_summary": summary
    }

# vectorize property scoring across full apartment dataframe
@st.cache_data(show_spinner=False)
def build_property_score_dataframe(
    df_properties: pd.DataFrame,
    df_environment: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    df = df_properties.copy()

    # calculate granular benchmark medians by location and type
    if "Calculated_Price_Per_Meter" not in df.columns:
        df["Calculated_Price_Per_Meter"] = np.where(
            (df.get("Price_Numeric", 0) > 0) & (df.get("Area", 0) > 0),
            (df["Price_Numeric"] / df["Area"]).round(2),
            np.nan
        )

    city_median_ppm = float(df["Calculated_Price_Per_Meter"].median())
    if math.isnan(city_median_ppm) or city_median_ppm <= 0:
        city_median_ppm = 35000.0

    group_cols = ["city", "region"] if "city" in df.columns and "region" in df.columns else ["Location"]
    area_medians = df.groupby(group_cols)["Calculated_Price_Per_Meter"].transform("median")
    df["area_median_price_per_m2"] = area_medians.fillna(city_median_ppm)

    scoring_results = []
    for _, row in df.iterrows():
        res = calculate_property_quality_score(row, row["area_median_price_per_m2"])
        scoring_results.append(res)

    res_df = pd.DataFrame(scoring_results, index=df.index)
    for col in res_df.columns:
        df[col] = res_df[col]

    return df
