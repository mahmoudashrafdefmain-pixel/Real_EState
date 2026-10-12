# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
import streamlit as st

from .config import NON_BUILDING_TYPES

# validate customer profile against business boundaries
def validate_customer_profile(profile: Dict[str, Any], rules: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    income = profile.get("monthly_net_income", 0.0)
    debt = profile.get("existing_monthly_debt", 0.0)
    down_payment = profile.get("available_down_payment", 0.0)
    max_payment = profile.get("user_comfortable_payment", 0.0)
    age = profile.get("age", 30)
    term_years = profile.get("preferred_term_years", 15)

    if income <= 0:
        errors.append("Monthly net income must be greater than zero.")
    if debt < 0:
        errors.append("Existing monthly debt cannot be negative.")
    if debt >= income and income > 0:
        errors.append("Existing debt exceeds monthly income, leaving zero capacity.")
    if down_payment < 0:
        errors.append("Available down payment cannot be negative.")
    if max_payment < 0:
        errors.append("Comfortable monthly payment cannot be negative.")
    min_age = rules.get("minimum_age", 21)
    max_age = rules.get("maximum_age", 65)
    if age < min_age:
        errors.append(f"Applicant age ({age}) must be at least {min_age} years.")
    if age > max_age:
        errors.append(f"Applicant age ({age}) exceeds maximum allowed age ({max_age}).")
    if (age + term_years) > max_age:
        errors.append(f"Applicant age plus financing term ({age + term_years}) exceeds maximum age {max_age}.")
    min_term = rules.get("minimum_term_years", 5)
    max_term = rules.get("maximum_term_years", 20)
    if term_years < min_term or term_years > max_term:
        errors.append(f"Financing term must be between {min_term} and {max_term} years.")

    return len(errors) == 0, errors

# clean and normalize raw real estate dataframe
@st.cache_data(show_spinner=False)
def validate_and_normalize_properties(df_raw: pd.DataFrame, df_coords: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    df = df_raw.copy()

    # normalize price columns from raw dataset
    if "price" in df.columns and "Price_Numeric" not in df.columns:
        df["Price_Numeric"] = pd.to_numeric(df["price"], errors="coerce")
    else:
        df["Price_Numeric"] = pd.to_numeric(df.get("Price_Numeric", np.nan), errors="coerce")

    # normalize price per square meter from raw dataset
    if "price_per_sqm" in df.columns and "Calculated_Price_Per_Meter" not in df.columns:
        df["Calculated_Price_Per_Meter"] = pd.to_numeric(df["price_per_sqm"], errors="coerce")
    else:
        df["Calculated_Price_Per_Meter"] = pd.to_numeric(df.get("Calculated_Price_Per_Meter", np.nan), errors="coerce")

    df["is_price_valid"] = (df["Price_Numeric"] > 0) & df["Price_Numeric"].notna()
    df["is_ppm_valid"] = (df["Calculated_Price_Per_Meter"] > 0) & df["Calculated_Price_Per_Meter"].notna()

    # derive living area in square meters
    if "size_sqm" in df.columns and "Area" not in df.columns:
        df["Area"] = pd.to_numeric(df["size_sqm"], errors="coerce")
    elif "Area" in df.columns:
        df["Area"] = pd.to_numeric(df["Area"], errors="coerce")
    else:
        df["Area"] = np.where(
            df["is_price_valid"] & df["is_ppm_valid"],
            (df["Price_Numeric"] / df["Calculated_Price_Per_Meter"]).round(1),
            np.nan
        )

    mask_recalc = (df["Area"].isna() | (df["Area"] <= 0)) & df["is_price_valid"] & df["is_ppm_valid"]
    df.loc[mask_recalc, "Area"] = (df.loc[mask_recalc, "Price_Numeric"] / df.loc[mask_recalc, "Calculated_Price_Per_Meter"]).round(1)
    df["is_area_valid"] = (df["Area"] > 0) & df["Area"].notna()

    # derive price per meter when missing
    mask_calc_ppm = (df["Calculated_Price_Per_Meter"].isna() | (df["Calculated_Price_Per_Meter"] <= 0)) & df["is_price_valid"] & df["is_area_valid"]
    df.loc[mask_calc_ppm, "Calculated_Price_Per_Meter"] = (df.loc[mask_calc_ppm, "Price_Numeric"] / df.loc[mask_calc_ppm, "Area"]).round(1)

    # normalize bedrooms and room counts
    if "bedrooms" in df.columns and "Rooms" not in df.columns:
        df["Rooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").fillna(3.0)
    else:
        df["Rooms"] = pd.to_numeric(df.get("Rooms", 3.0), errors="coerce").fillna(3.0)

    # normalize bathrooms count to numeric value
    if "bathrooms" in df.columns and "Bathrooms_num" not in df.columns:
        df["Bathrooms_num"] = pd.to_numeric(df["bathrooms"], errors="coerce").fillna(2.0)
    elif "Bathrooms_num" in df.columns:
        df["Bathrooms_num"] = pd.to_numeric(df["Bathrooms_num"], errors="coerce").fillna(2.0)
    elif "Bathrooms" in df.columns:
        extracted = df["Bathrooms"].astype(str).str.extract(r"(\d+)")[0]
        df["Bathrooms_num"] = pd.to_numeric(extracted, errors="coerce").fillna(2.0)
    else:
        df["Bathrooms_num"] = 2.0

    # parse floor level and building unit eligibility
    if "floor" in df.columns:
        df["floor_level"] = pd.to_numeric(df["floor"], errors="coerce")
        df["Floor Level"] = df["floor_level"]
    elif "Floor Level" in df.columns:
        df["floor_level"] = pd.to_numeric(df["Floor Level"], errors="coerce")
    else:
        df["floor_level"] = np.nan
        df["Floor Level"] = np.nan

    # parse property type and purpose classification
    if "type" in df.columns:
        df["property_type"] = df["type"].astype(str).str.strip()
        df["Type"] = df["property_type"]
    elif "Type" in df.columns:
        df["property_type"] = df["Type"].astype(str).str.strip()
    else:
        df["property_type"] = "Apartment"
        df["Type"] = "Apartment"

    # classify building versus non building unit
    type_clean = df["property_type"].astype(str).str.strip().str.lower()
    df["is_building_unit"] = (~type_clean.isin(NON_BUILDING_TYPES)) & df["floor_level"].notna()

    # clean geographic locations and macro cities
    if "region" in df.columns:
        df["region"] = df["region"].fillna("Greater Cairo").astype(str).str.strip()
        df["Location"] = df["region"]
    elif "Location" in df.columns:
        df["Location"] = df["Location"].fillna("Greater Cairo").astype(str).str.strip()
        df["region"] = df["Location"]
    else:
        df["Location"] = "Greater Cairo"
        df["region"] = "Greater Cairo"

    if "city" in df.columns:
        df["city"] = df["city"].fillna("Cairo").astype(str).str.strip()
    else:
        df["city"] = "Cairo"

    # clean compound class and community amenities
    if "class" in df.columns:
        df["class"] = df["class"].fillna("Class B").astype(str).str.strip()
        if not df["class"].str.startswith("Class").all():
            df["class"] = df["class"].apply(lambda c: f"Class {c}" if len(str(c)) == 1 else str(c))
        df["Amenities"] = df["class"].apply(lambda c: "B(Compound)" if "A" in c or "B" in c else "C(BASICS)")
    elif "Amenities" in df.columns:
        df["Amenities"] = df["Amenities"].fillna("C(BASICS)").astype(str).str.strip()
        df["class"] = df["Amenities"].apply(lambda a: "Class A" if "Compound" in a else "Class B")
    else:
        df["class"] = "Class B"
        df["Amenities"] = "C(BASICS)"

    # clean view orientation categories
    if "view" in df.columns:
        df["view"] = df["view"].fillna("Standard / Not Specified").astype(str).str.strip()
        df["view"] = df["view"].replace({"?": "Standard / Not Specified", "-": "Standard / Not Specified"})
    else:
        df["view"] = "Standard / Not Specified"

    # clean furnishing status
    if "Furnished" in df.columns:
        df["Furnished"] = df["Furnished"].fillna("No").astype(str).str.strip().str.title()
    else:
        df["Furnished"] = "No"

    # clean delivery finishing specifications
    if "finishing_type" not in df.columns:
        df["finishing_type"] = df["class"].apply(lambda c: "superlux" if "A" in c else ("semi" if "B" in c else "lux"))
    else:
        df["finishing_type"] = df["finishing_type"].fillna("semi").astype(str).str.strip()

    # parse air quality index
    if "air_quality" in df.columns:
        df["us_aqi"] = pd.to_numeric(df["air_quality"], errors="coerce")
    elif "us_aqi" in df.columns:
        df["us_aqi"] = pd.to_numeric(df["us_aqi"], errors="coerce")
    else:
        df["us_aqi"] = np.nan

    # parse green space coverage percentage
    if "green_space" in df.columns:
        df["green_coverage_pct"] = pd.to_numeric(df["green_space"], errors="coerce")
    elif "green_coverage_pct" in df.columns:
        df["green_coverage_pct"] = pd.to_numeric(df["green_coverage_pct"], errors="coerce")
    else:
        df["green_coverage_pct"] = np.nan

    # impute missing environmental data from city median
    city_aqi_medians = df.groupby("city")["us_aqi"].transform("median").fillna(68.0)
    city_green_medians = df.groupby("city")["green_coverage_pct"].transform("median").fillna(4.0)
    df["us_aqi"] = df["us_aqi"].fillna(city_aqi_medians)
    df["green_coverage_pct"] = df["green_coverage_pct"].fillna(city_green_medians)

    # attach latitude and longitude coordinates
    known_centers = {
        "New Cairo - El Tagamoa": (30.015, 31.485),
        "New Cairo City": (30.025, 31.490),
        "6 October City": (29.975, 30.935),
        "6th of October": (29.975, 30.935),
        "Sheikh Zayed City": (30.048, 30.985),
        "Sheikh Zayed": (30.048, 30.985),
        "Ras Al Hekma": (31.140, 27.850),
        "Hurghada": (27.257, 33.812),
        "Madinaty": (30.108, 31.625),
        "New Capital City": (30.010, 31.740),
        "Sidi Abdel Rahman": (30.965, 28.720),
        "Qesm Marsa Matrouh": (31.350, 27.240),
        "Shorouk City": (30.138, 31.615),
        "Mostakbal City - Future City": (30.082, 31.660),
        "Qesm Ad Dabaah": (31.030, 28.435),
        "Al Ain Al Sokhna": (29.600, 32.320),
        "Al Alamein": (30.835, 28.956),
        "Nasr City": (30.055, 31.345),
        "Rehab City": (30.060, 31.493),
        "Obour City": (30.220, 31.460),
        "Maadi": (29.960, 31.265),
        "Heliopolis": (30.090, 31.330),
        "Zamalek": (30.061, 31.220),
        "Dokki": (30.040, 31.210),
        "Alexandria": (31.215, 29.955),
        "Cairo": (30.044, 31.235),
        "Giza": (29.987, 31.211),
        "North Coast": (30.950, 28.800),
        "Red Sea": (27.257, 33.812),
        "Suez": (29.966, 32.549)
    }

    def resolve_coords(row):
        reg = row.get("region", "")
        cty = row.get("city", "")
        if reg in known_centers:
            lat, lon = known_centers[reg]
        elif cty in known_centers:
            lat, lon = known_centers[cty]
        else:
            lat, lon = (30.044, 31.235)
        # add tiny deterministic jitter based on index
        idx_hash = (hash(str(row.name)) % 100 - 50) * 0.0001
        return lat + idx_hash, lon + idx_hash

    coords = df.apply(resolve_coords, axis=1)
    df["latitude"] = [c[0] for c in coords]
    df["longitude"] = [c[1] for c in coords]
    df["has_valid_coordinates"] = True

    df["is_valid_property"] = df["is_price_valid"] & df["is_area_valid"]
    return df
