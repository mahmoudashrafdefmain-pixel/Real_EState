# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

# load raw dataset from disk safely
@st.cache_data(show_spinner=False)
def load_raw_dataset(custom_path: Optional[str] = None) -> pd.DataFrame:
    # search candidate paths for raw real estate data
    candidate_paths = []
    if custom_path:
        candidate_paths.append(Path(custom_path))
    candidate_paths.extend([
        Path(__file__).resolve().parent.parent.parent / "data_analysis" / "after" / "after_env.csv",
        Path(__file__).resolve().parent.parent / "data_analysis" / "after" / "after_env.csv",
        Path(r"D:\RealEstateDashBoard\data_analysis\after\after_env.csv"),
        Path.cwd() / "data_analysis" / "after" / "after_env.csv",
        Path(__file__).resolve().parent.parent.parent / "2-data" / "after_env.csv",
        Path(r"D:\RealEstateDashBoard\2-data\after_env.csv"),
        Path.cwd() / "2-data" / "after_env.csv",
        Path.cwd().parent / "2-data" / "after_env.csv"
    ])
    for p in candidate_paths:
        if p.exists() and p.is_file():
            df = pd.read_csv(p)
            return df.copy()
    raise FileNotFoundError("Could not locate after_env.csv in expected directories.")

# load secondary location coordinates table safely
@st.cache_data(show_spinner=False)
def load_neighborhood_coordinates() -> pd.DataFrame:
    # check available coordinate reference datasets
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent / "data_analysis" / "after" / "cairo_neighborhoods_environmental.csv",
        Path(__file__).resolve().parent.parent / "data_analysis" / "after" / "cairo_neighborhoods_environmental.csv",
        Path(r"D:\RealEstateDashBoard\data_analysis\after\cairo_neighborhoods_environmental.csv"),
        Path.cwd() / "data_analysis" / "after" / "cairo_neighborhoods_environmental.csv",
        Path(__file__).resolve().parent.parent.parent / "2-data" / "cairo_neighborhoods_environmental.csv",
        Path(r"D:\RealEstateDashBoard\2-data\cairo_neighborhoods_environmental.csv"),
        Path.cwd() / "2-data" / "cairo_neighborhoods_environmental.csv"
    ]
    for p in candidate_paths:
        if p.exists() and p.is_file():
            return pd.read_csv(p)

    # Clean default coordinate centroids for verified Egyptian hubs
    coords_dict = {
        "Location": [
            "New Cairo - El Tagamoa", "New Cairo City", "6 October City", "Sheikh Zayed City",
            "Madinaty", "New Capital City", "Al Alamein", "Sidi Abdel Rahman", "Maadi", "Nasr City"
        ],
        "latitude": [30.015, 30.025, 29.975, 30.048, 30.108, 30.010, 30.835, 30.965, 29.960, 30.055],
        "longitude": [31.485, 31.490, 30.935, 30.985, 31.625, 31.740, 28.956, 28.720, 31.265, 31.345]
    }
    return pd.DataFrame(coords_dict)
