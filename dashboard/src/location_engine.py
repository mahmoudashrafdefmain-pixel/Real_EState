# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Tuple, Optional
import math
import numpy as np
import pandas as pd

# calculate spherical haversine distance between coordinate pairs
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # compute distance in kilometers using haversine metric
    if any(math.isnan(x) for x in [lat1, lon1, lat2, lon2]):
        return float("nan")
    r_earth = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r_earth * c, 1)

# calculate vectorized geographic distances across property dataframe
def calculate_distance_vectorized(
    df: pd.DataFrame,
    target_lat: float,
    target_lon: float
) -> pd.Series:
    # compute vectorized haversine distances in kilometers
    if math.isnan(target_lat) or math.isnan(target_lon) or "latitude" not in df.columns or "longitude" not in df.columns:
        return pd.Series(np.nan, index=df.index)

    lats = pd.to_numeric(df["latitude"], errors="coerce").values
    lons = pd.to_numeric(df["longitude"], errors="coerce").values

    valid_mask = ~np.isnan(lats) & ~np.isnan(lons)
    distances = np.full(len(df), np.nan)

    if valid_mask.any():
        lat1_rad = np.radians(target_lat)
        lon1_rad = np.radians(target_lon)
        lat2_rad = np.radians(lats[valid_mask])
        lon2_rad = np.radians(lons[valid_mask])

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * (np.sin(dlon / 2.0) ** 2)
        c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
        distances[valid_mask] = np.round(6371.0 * c, 1)

    return pd.Series(distances, index=df.index)

# resolve geographic coordinates for selected area name
def resolve_area_coordinates(df: pd.DataFrame, selected_area: str) -> Tuple[float, float]:
    # lookup median coordinates for selected area
    if not selected_area or "Location" not in df.columns:
        return float("nan"), float("nan")
    sub = df[df["Location"] == selected_area].dropna(subset=["latitude", "longitude"])
    if not sub.empty:
        return float(sub["latitude"].median()), float(sub["longitude"].median())
    return float("nan"), float("nan")

# extract sorted unique list of locations with property counts
def get_location_catalog(df: pd.DataFrame) -> List[str]:
    # return list of distinct locations ordered by inventory count
    if "Location" not in df.columns:
        return []
    counts = df["Location"].value_counts()
    return counts.index.tolist()
