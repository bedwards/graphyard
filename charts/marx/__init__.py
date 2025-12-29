"""
Marx retrospective article data loaders.
"""

from .data import (
    load_top10_income_share,
    load_gini_index,
    load_financial_sector_growth,
    load_manufacturing_share,
    load_services_share,
    load_unemployment_rate,
    load_world_gdp_growth,
    load_capital_formation,
    load_gdp_per_capita_growth,
    load_us_sector_transformation,
    load_us_inequality_timeline,
    load_crisis_markers,
    load_global_inequality_comparison,
    load_us_financialization,
)

__all__ = [
    "load_top10_income_share",
    "load_gini_index",
    "load_financial_sector_growth",
    "load_manufacturing_share",
    "load_services_share",
    "load_unemployment_rate",
    "load_world_gdp_growth",
    "load_capital_formation",
    "load_gdp_per_capita_growth",
    "load_us_sector_transformation",
    "load_us_inequality_timeline",
    "load_crisis_markers",
    "load_global_inequality_comparison",
    "load_us_financialization",
]
