# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Set

# define centralized project financing simulation constants and rules
MINIMUM_AGE: int = 21
MAXIMUM_AGE: int = 65
MINIMUM_MONTHLY_NET_INCOME: float = 20000.0
MIN_MONTHLY_INCOME: float = 20000.0
MINIMUM_CASH_RATIO: float = 0.50
MIN_CASH_INCOME_RATIO: float = 0.50
MAX_INSTALLMENT_RATIO: float = 0.30
MAX_INSTALLMENT_INCOME_RATIO: float = 0.30
MINIMUM_COMFORTABLE_PAYMENT_RATIO: float = 0.60
MAX_COMFORT_INCOME_RATIO: float = 0.60
ALLOWED_TERMS = [15, 20]
ALLOWED_FINANCE_TERMS = [15, 20]
AVG_PROPERTY_PRICE: float = 5990259.0
MAXIMUM_LTV: float = 0.80
MINIMUM_DOWN_PAYMENT_RATIO: float = 0.20
CLOSE_MATCH_THRESHOLD: float = 0.05

# define non building property types without floor evaluation
NON_BUILDING_TYPES: Set[str] = {
    "villa",
    "stand alone villa",
    "townhouse",
    "twin house",
    "chalet",
    "ivilla",
    "roof"
}

# define institutional project financing rule dictionary
PROJECT_FINANCING_RULES: Dict[str, Any] = {
    "model_name": "Project Financing Simulation Standard",
    "minimum_age": MINIMUM_AGE,
    "maximum_age": MAXIMUM_AGE,
    "minimum_monthly_net_income": MINIMUM_MONTHLY_NET_INCOME,
    "minimum_cash_ratio": MINIMUM_CASH_RATIO,
    "max_installment_ratio": MAX_INSTALLMENT_RATIO,
    "minimum_comfortable_payment_ratio": MINIMUM_COMFORTABLE_PAYMENT_RATIO,
    "allowed_terms": ALLOWED_TERMS,
    "avg_property_price": AVG_PROPERTY_PRICE,
    "maximum_ltv": MAXIMUM_LTV,
    "minimum_down_payment_ratio": MINIMUM_DOWN_PAYMENT_RATIO,
    "close_match_threshold": CLOSE_MATCH_THRESHOLD,
    "tier_low_rate": 8.0,
    "tier_mid_rate": 10.5,
    "tier_high_rate": 12.5
}
general_financing_rules = PROJECT_FINANCING_RULES

# define regulatory and simulation disclaimer notices
FINANCING_DISCLAIMER: str = (
    "This application is a financing simulation based on project assumptions and available property data. "
    "Passing the simulation does not mean a bank has approved financing. Actual lending decisions depend on "
    "the lender's current policy, underwriting, credit assessment, documentation, valuation, rates, fees, and other conditions."
)

# define investment future value disclaimer notice
INVESTMENT_DISCLAIMER: str = (
    "Projected future prices and gains are analytical estimates based on the available dataset and selected "
    "assumptions. They are not guaranteed returns."
)

# define property quality and value scoring standard
PROPERTY_SCORE_STANDARD: Dict[str, Any] = {
    "air_quality": [
        {"max": 50.0, "score": 25.0, "band": "0–50", "label": "Good Air Quality"},
        {"max": 65.0, "score": 23.0, "band": "51–65", "label": "Clean Coastal / Desert Air"},
        {"max": 75.0, "score": 20.0, "band": "66–75", "label": "Moderate Suburban Air"},
        {"max": 85.0, "score": 15.0, "band": "76–85", "label": "Acceptable Urban Air Quality"},
        {"max": 100.0, "score": 12.0, "band": "86–100", "label": "Mildly Elevated Pollution"},
        {"max": 150.0, "score": 6.0, "band": "101–150", "label": "Elevated Pollution Level"},
        {"max": float("inf"), "score": 0.0, "band": ">150", "label": "Very High Pollution Level"}
    ],
    "green_coverage": [
        {"min": 25.0, "score": 25.0, "band": "≥25%", "label": "Exceptional Green Canopy"},
        {"min": 15.0, "score": 22.0, "band": "15%–<25%", "label": "High Green Coverage"},
        {"min": 7.0, "score": 18.0, "band": "7%–<15%", "label": "Medium Green Coverage"},
        {"min": 3.0, "score": 14.0, "band": "3%–<7%", "label": "Standard Urban Green"},
        {"min": 1.5, "score": 9.0, "band": "1.5%–<3%", "label": "Low-Moderate Green Space"},
        {"min": 0.0, "score": 5.0, "band": "<1.5%", "label": "Minimal Urban Greenery"}
    ],
    "price_value": [
        {"max_ratio": 0.80, "score": 25.0, "band": "≤0.80", "label": "Deep Value (≥20% Below Local Median)"},
        {"max_ratio": 0.90, "score": 23.0, "band": "0.81–0.90", "label": "Attractive Value (10%–20% Below Local Median)"},
        {"max_ratio": 1.00, "score": 21.0, "band": "0.91–1.00", "label": "Fair Value (0%–10% Below Local Median)"},
        {"max_ratio": 1.15, "score": 16.0, "band": "1.01–1.15", "label": "Mild Premium (1%–15% Above Local Median)"},
        {"max_ratio": 1.30, "score": 10.0, "band": "1.16–1.30", "label": "Premium Pricing (16%–30% Above Local Median)"},
        {"max_ratio": 1.50, "score": 5.0, "band": "1.31–1.50", "label": "High Luxury Premium (31%–50% Above Local Median)"},
        {"max_ratio": float("inf"), "score": 2.0, "band": ">1.50", "label": "Substantial Premium (>50% Above Local Median)"}
    ],
    "class_weights": {
        "A": 12.0,
        "Class A": 12.0,
        "B": 9.0,
        "Class B": 9.0,
        "C": 6.0,
        "Class C": 6.0,
        "D": 3.0,
        "Class D": 3.0
    },
    "view_weights": {
        "sea view": 9.0,
        "lagoon / lake view": 9.0,
        "water view": 9.0,
        "golf view": 9.0,
        "garden / green view": 7.0,
        "pool view": 7.0,
        "open view": 6.0,
        "city view": 5.0,
        "street view": 4.0,
        "standard / not specified": 4.0
    },
    "floor_standards": [
        {"min_fl": 2.0, "max_fl": 4.0, "score": 25.0, "label": "Optimal Middle Floor (Floors 2–4)"},
        {"min_fl": 1.0, "max_fl": 1.0, "score": 21.0, "label": "Elevated First Floor (Floor 1)"},
        {"min_fl": 5.0, "max_fl": 5.0, "score": 20.0, "label": "Desirable Upper Floor (Floor 5)"},
        {"min_fl": 0.0, "max_fl": 0.0, "score": 17.0, "label": "Ground Floor"},
        {"min_fl": 6.0, "max_fl": 8.0, "score": 15.0, "label": "High Floor (Floors 6–8)"},
        {"min_fl": 9.0, "max_fl": float("inf"), "score": 12.0, "label": "Top / Sky Floor (Floor 9+)"}
    ],
    "finishing": {
        "ultra super lux": {"score": 25.0, "display": "Ultra Super Lux", "label": "Ultra Super Lux / Fully Finished Premium"},
        "ultra_super_lux": {"score": 25.0, "display": "Ultra Super Lux", "label": "Ultra Super Lux / Fully Finished Premium"},
        "superlux": {"score": 24.0, "display": "Super Lux", "label": "Super Lux Finishing"},
        "super lux": {"score": 24.0, "display": "Super Lux", "label": "Super Lux Finishing"},
        "super_lux": {"score": 24.0, "display": "Super Lux", "label": "Super Lux Finishing"},
        "lux": {"score": 22.0, "display": "Lux", "label": "Lux Standard Finishing"},
        "fully finished": {"score": 21.0, "display": "Fully Finished", "label": "Fully Finished Turnkey"},
        "fully_finished": {"score": 21.0, "display": "Fully Finished", "label": "Fully Finished Turnkey"},
        "semi": {"score": 14.0, "display": "Semi Finished", "label": "Semi Finished Structure"},
        "semi finished": {"score": 14.0, "display": "Semi Finished", "label": "Semi Finished Structure"},
        "semi_finished": {"score": 14.0, "display": "Semi Finished", "label": "Semi Finished Structure"},
        "core & shell": {"score": 8.0, "display": "Core & Shell", "label": "Core & Shell Industrial State"},
        "core and shell": {"score": 8.0, "display": "Core & Shell", "label": "Core & Shell Industrial State"},
        "without": {"score": 3.0, "display": "Unfinished", "label": "Unfinished / Brick State"},
        "unfinished": {"score": 3.0, "display": "Unfinished", "label": "Unfinished / Brick State"},
        "red brick": {"score": 3.0, "display": "Unfinished", "label": "Unfinished / Red Brick"}
    }
}

# define user friendly factor display names
USER_FRIENDLY_FACTOR_NAMES: Dict[str, str] = {
    "air_quality_score": "Air Quality",
    "green_coverage_score": "Green Space",
    "price_value_score": "Price Value",
    "class_view_score": "Class & View Quality",
    "floor_score": "Floor Level",
    "property_quality_value_score": "Property Quality & Value Score"
}

# define factor educational rationales explaining why each factor matters
FACTOR_EDUCATIONAL_EXPLANATIONS: Dict[str, str] = {
    "Air Quality": (
        "Air quality describes the environmental health of the area based on the US AQI standard, "
        "giving lower pollution areas higher ratings."
    ),
    "Green Space": (
        "Higher green coverage percentage indicates garden landscaping, parks, and tree canopy "
        "enhancing lifestyle and air purity."
    ),
    "Price Value": (
        "Evaluates the unit's price per square meter relative to the local benchmark median for that "
        "region and property type to identify high value vs luxury premiums."
    ),
    "Class & View Quality": (
        "Reflects compound community classification tier (Class A/B/C/D), scenic view orientation, "
        "and unit furnishing status."
    ),
    "Floor Level": (
        "Evaluates floor positioning for building units (favoring middle floors 2–4). "
        "Note: Standalone units like villas and chalets have this factor strictly excluded."
    )
}

# define score tier interpretations
SCORE_TIERS: List[Dict[str, Any]] = [
    {"min": 88.0, "label": "Exceptional", "color": "#137333"},
    {"min": 78.0, "label": "High Quality", "color": "#2A9D8F"},
    {"min": 68.0, "label": "Balanced Standard", "color": "#1B2A4A"},
    {"min": 55.0, "label": "Moderate Tier", "color": "#B06000"},
    {"min": 0.0, "label": "Entry / Developing", "color": "#C5221F"}
]

# define analytical score info notice
SCORE_DISCLAIMER: str = (
    "This score is a project-specific analytical benchmark based on key environmental, pricing, and structural "
    "factors. For units not in a building (e.g. villas, townhouses, chalets), floor level is excluded from their "
    "scoring system without any penalty."
)
