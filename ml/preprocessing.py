"""
Time Series Preprocessing

Handles the key challenges of economic time series data:
1. Missing values (gaps in data collection)
2. Different start dates across countries
3. Creating optimal lag features
4. Panel data normalization

Based on 2025 best practices from:
- Skforecast documentation
- S4M framework for missing data
- Economic forecasting literature
"""

import numpy as np
import pandas as pd
from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class DataQualityReport:
    """Report on data quality issues."""
    total_rows: int
    missing_count: int
    missing_percent: float
    first_year: int
    last_year: int
    gap_years: list[int]
    missingness_type: Literal["MCAR", "MAR", "MNAR", "unknown"]


def analyze_missingness(
    df: pd.DataFrame,
    value_col: str,
    time_col: str = "year",
    entity_col: Optional[str] = None,
) -> dict[str, DataQualityReport]:
    """
    Analyze missing data patterns in time series.

    Identifies:
    - MCAR (Missing Completely At Random): Random gaps
    - MAR (Missing At Random): Gaps correlated with other variables
    - MNAR (Missing Not At Random): Gaps related to the value itself

    Returns report per entity (country) or single report for univariate.
    """
    reports = {}

    if entity_col:
        entities = df[entity_col].unique()
    else:
        entities = ["all"]
        df = df.copy()
        df["_entity"] = "all"
        entity_col = "_entity"

    for entity in entities:
        subset = df[df[entity_col] == entity].copy()
        total = len(subset)
        missing = subset[value_col].isna().sum()

        # Find gaps
        years = subset[time_col].dropna().sort_values()
        if len(years) > 0:
            first_year = int(years.min())
            last_year = int(years.max())
            expected_years = set(range(first_year, last_year + 1))
            actual_years = set(years.astype(int))
            gap_years = sorted(expected_years - actual_years)
        else:
            first_year = last_year = 0
            gap_years = []

        # Simple missingness classification
        if missing == 0:
            miss_type = "MCAR"  # No missing
        elif len(gap_years) > 0:
            miss_type = "MAR"  # Structured gaps
        else:
            miss_type = "unknown"

        reports[entity] = DataQualityReport(
            total_rows=total,
            missing_count=missing,
            missing_percent=100 * missing / total if total > 0 else 0,
            first_year=first_year,
            last_year=last_year,
            gap_years=gap_years,
            missingness_type=miss_type,
        )

    return reports


def handle_missing_values(
    df: pd.DataFrame,
    value_col: str,
    time_col: str = "year",
    method: Literal["linear", "forward", "backward", "mean", "zero", "drop"] = "linear",
    entity_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Handle missing values in time series data.

    Methods:
    - linear: Linear interpolation (best for short gaps, stable trends)
    - forward: Forward fill (LOCF - last observation carried forward)
    - backward: Backward fill
    - mean: Fill with column mean
    - zero: Fill with zeros (use with caution - may bias models)
    - drop: Remove rows with missing values

    For panel data, applies method within each entity group.
    """
    df = df.copy()

    if entity_col:
        groups = df.groupby(entity_col)
    else:
        groups = [(None, df)]

    result_frames = []

    for name, group in groups:
        group = group.sort_values(time_col)

        if method == "linear":
            group[value_col] = group[value_col].interpolate(method="linear")
        elif method == "forward":
            group[value_col] = group[value_col].ffill()
        elif method == "backward":
            group[value_col] = group[value_col].bfill()
        elif method == "mean":
            group[value_col] = group[value_col].fillna(group[value_col].mean())
        elif method == "zero":
            group[value_col] = group[value_col].fillna(0)
        elif method == "drop":
            group = group.dropna(subset=[value_col])

        result_frames.append(group)

    return pd.concat(result_frames, ignore_index=True)


def create_lag_features(
    df: pd.DataFrame,
    value_col: str,
    lags: list[int],
    time_col: str = "year",
    entity_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Create lag features for time series forecasting.

    Based on research:
    - 4-9 lags typically optimal for annual economic data
    - More lags can "confuse" the model (diminishing returns after 9-12)
    - XGBoost/LightGBM handle NaN from lags automatically

    Args:
        df: Input DataFrame
        value_col: Column to create lags for
        lags: List of lag periods (e.g., [1, 2, 3, 4] for t-1 through t-4)
        time_col: Time column name
        entity_col: Entity column for panel data

    Returns:
        DataFrame with added lag columns (value_col_lag_1, etc.)
    """
    df = df.copy()

    if entity_col:
        groups = df.groupby(entity_col)
    else:
        groups = [(None, df)]

    result_frames = []

    for name, group in groups:
        group = group.sort_values(time_col)

        for lag in lags:
            col_name = f"{value_col}_lag_{lag}"
            group[col_name] = group[value_col].shift(lag)

        result_frames.append(group)

    return pd.concat(result_frames, ignore_index=True)


def create_rolling_features(
    df: pd.DataFrame,
    value_col: str,
    windows: list[int],
    stats: list[str] = ["mean", "std"],
    time_col: str = "year",
    entity_col: Optional[str] = None,
) -> pd.DataFrame:
    """
    Create rolling window features.

    Common configurations:
    - window_sizes=[3, 5, 7] for moving averages
    - stats=["mean", "std", "min", "max"] for comprehensive features

    Args:
        df: Input DataFrame
        value_col: Column to create rolling features for
        windows: List of window sizes
        stats: Statistics to compute ("mean", "std", "min", "max", "sum")
        time_col: Time column name
        entity_col: Entity column for panel data
    """
    df = df.copy()

    if entity_col:
        groups = df.groupby(entity_col)
    else:
        groups = [(None, df)]

    result_frames = []

    for name, group in groups:
        group = group.sort_values(time_col)

        for window in windows:
            rolling = group[value_col].rolling(window=window, min_periods=1)

            for stat in stats:
                col_name = f"{value_col}_roll_{window}_{stat}"
                if stat == "mean":
                    group[col_name] = rolling.mean()
                elif stat == "std":
                    group[col_name] = rolling.std()
                elif stat == "min":
                    group[col_name] = rolling.min()
                elif stat == "max":
                    group[col_name] = rolling.max()
                elif stat == "sum":
                    group[col_name] = rolling.sum()

        result_frames.append(group)

    return pd.concat(result_frames, ignore_index=True)


def prepare_panel_data(
    df: pd.DataFrame,
    value_col: str,
    time_col: str = "year",
    entity_col: str = "entity_code",
    lags: list[int] = [1, 2, 3, 4, 5],
    rolling_windows: list[int] = [3, 5],
    rolling_stats: list[str] = ["mean"],
    handle_missing: str = "linear",
    min_years: int = 10,
) -> tuple[pd.DataFrame, dict]:
    """
    Prepare panel data for ML forecasting.

    This is the main entry point that handles:
    1. Filtering entities with insufficient data
    2. Handling missing values
    3. Creating lag and rolling features
    4. Generating a metadata report

    Args:
        df: Raw panel data
        value_col: Target variable column
        time_col: Year/time column
        entity_col: Country/entity column
        lags: Lag periods to create
        rolling_windows: Rolling window sizes
        rolling_stats: Statistics for rolling windows
        handle_missing: Method for missing values
        min_years: Minimum years of data required per entity

    Returns:
        Tuple of (prepared DataFrame, metadata dict)
    """
    # Analyze before processing
    quality_reports = analyze_missingness(df, value_col, time_col, entity_col)

    # Filter entities with insufficient data
    valid_entities = [
        entity for entity, report in quality_reports.items()
        if (report.last_year - report.first_year + 1) >= min_years
    ]

    df_filtered = df[df[entity_col].isin(valid_entities)].copy()

    # Handle missing values
    df_clean = handle_missing_values(
        df_filtered, value_col, time_col, handle_missing, entity_col
    )

    # Create features
    df_features = create_lag_features(
        df_clean, value_col, lags, time_col, entity_col
    )

    df_features = create_rolling_features(
        df_features, value_col, rolling_windows, rolling_stats, time_col, entity_col
    )

    metadata = {
        "original_entities": len(quality_reports),
        "valid_entities": len(valid_entities),
        "dropped_entities": len(quality_reports) - len(valid_entities),
        "lags_created": lags,
        "rolling_windows": rolling_windows,
        "missing_handling": handle_missing,
        "quality_reports": quality_reports,
    }

    return df_features, metadata
