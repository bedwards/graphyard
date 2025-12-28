"""
GDP Forecasting with Machine Learning

Applies gradient boosting models to forecast GDP for major economies.
Uses walk-forward validation and proper time series preprocessing.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.preprocessing import prepare_panel_data, analyze_missingness
from ml.forecaster import TimeSeriesForecaster, ModelConfig, ForecastResult
from charts.gdp.data import get_db_connection


# Major economies to forecast
MAJOR_ECONOMIES = [
    'USA', 'CHN', 'JPN', 'DEU', 'IND', 'GBR', 'FRA', 'BRA', 'ITA', 'CAN',
    'RUS', 'KOR', 'AUS', 'ESP', 'MEX'
]

ECONOMY_NAMES = {
    'USA': 'United States',
    'CHN': 'China',
    'JPN': 'Japan',
    'DEU': 'Germany',
    'IND': 'India',
    'GBR': 'United Kingdom',
    'FRA': 'France',
    'BRA': 'Brazil',
    'ITA': 'Italy',
    'CAN': 'Canada',
    'RUS': 'Russia',
    'KOR': 'South Korea',
    'AUS': 'Australia',
    'ESP': 'Spain',
    'MEX': 'Mexico',
}


def load_gdp_panel(
    countries: list[str] = None,
    start_year: int = 1960,
    end_year: int = 2024,
    use_growth: bool = False,
) -> pd.DataFrame:
    """
    Load GDP data for panel forecasting.

    Args:
        countries: List of country codes (None for all)
        start_year: First year to include
        end_year: Last year to include
        use_growth: If True, use GDP growth rate instead of level

    Returns:
        DataFrame with entity_code, year, value columns
    """
    conn = get_db_connection()

    indicator = 'NY.GDP.MKTP.KD.ZG' if use_growth else 'NY.GDP.MKTP.CD'

    if countries:
        placeholders = ','.join(['%s'] * len(countries))
        query = f"""
            SELECT
                cd.entity_code,
                e.entity_name,
                cd.year,
                cd.value
            FROM country_data cd
            JOIN entities e ON cd.entity_code = e.entity_code
            WHERE cd.indicator_code = %s
              AND cd.year BETWEEN %s AND %s
              AND cd.entity_code IN ({placeholders})
            ORDER BY cd.entity_code, cd.year
        """
        params = [indicator, start_year, end_year] + countries
    else:
        query = """
            SELECT
                cd.entity_code,
                e.entity_name,
                cd.year,
                cd.value
            FROM country_data cd
            JOIN entities e ON cd.entity_code = e.entity_code
            WHERE cd.indicator_code = %s
              AND cd.year BETWEEN %s AND %s
            ORDER BY cd.entity_code, cd.year
        """
        params = [indicator, start_year, end_year]

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    return df


def load_gdp_with_features(countries: list[str] = None) -> pd.DataFrame:
    """
    Load GDP with additional economic indicators as features.

    Features used:
    - GDP growth rate (lagged)
    - Population (for per-capita trends)
    - Trade openness (exports + imports / GDP)
    - Inflation rate
    """
    conn = get_db_connection()

    # Main indicators to use as features
    indicators = {
        'NY.GDP.MKTP.CD': 'gdp',           # GDP current USD
        'NY.GDP.MKTP.KD.ZG': 'gdp_growth',  # GDP growth
        'SP.POP.TOTL': 'population',        # Total population
        'NE.TRD.GNFS.ZS': 'trade_pct',      # Trade % of GDP
        'FP.CPI.TOTL.ZG': 'inflation',      # Inflation rate
    }

    placeholders = ','.join(['%s'] * len(indicators))

    if countries:
        country_placeholders = ','.join(['%s'] * len(countries))
        query = f"""
            SELECT
                cd.entity_code,
                cd.year,
                cd.indicator_code,
                cd.value
            FROM country_data cd
            WHERE cd.indicator_code IN ({placeholders})
              AND cd.year BETWEEN 1960 AND 2024
              AND cd.entity_code IN ({country_placeholders})
            ORDER BY cd.entity_code, cd.year
        """
        params = list(indicators.keys()) + countries
    else:
        query = f"""
            SELECT
                cd.entity_code,
                cd.year,
                cd.indicator_code,
                cd.value
            FROM country_data cd
            WHERE cd.indicator_code IN ({placeholders})
              AND cd.year BETWEEN 1960 AND 2024
            ORDER BY cd.entity_code, cd.year
        """
        params = list(indicators.keys())

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Pivot to wide format
    df_wide = df.pivot_table(
        index=['entity_code', 'year'],
        columns='indicator_code',
        values='value'
    ).reset_index()

    # Rename columns
    df_wide.columns.name = None
    df_wide = df_wide.rename(columns=indicators)

    return df_wide


def prepare_forecast_features(
    df: pd.DataFrame,
    target_col: str = 'gdp',
    lags: list[int] = [1, 2, 3, 4, 5],
) -> tuple[pd.DataFrame, list[str]]:
    """
    Prepare features for forecasting.

    Returns DataFrame with features and list of feature column names.
    """
    # Use the preprocessing module
    df_prepared, metadata = prepare_panel_data(
        df,
        value_col=target_col,
        time_col='year',
        entity_col='entity_code',
        lags=lags,
        rolling_windows=[3, 5],
        rolling_stats=['mean'],
        handle_missing='linear',
        min_years=20,
    )

    # Feature columns (exclude identifiers and target)
    feature_cols = [
        col for col in df_prepared.columns
        if col not in ['entity_code', 'year', 'entity_name', target_col]
        and not col.startswith('_')
    ]

    return df_prepared, feature_cols


def train_gdp_forecaster(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str = 'gdp',
) -> tuple[TimeSeriesForecaster, dict[str, ForecastResult]]:
    """
    Train forecasting models and compare performance.

    Uses walk-forward validation (TimeSeriesSplit) which is the
    correct approach for time series (unlike k-fold which leaks
    future information into training).
    """
    # Drop rows with missing target or features
    df_clean = df.dropna(subset=feature_cols + [target_col])

    X = df_clean[feature_cols]
    y = df_clean[target_col]

    # Configure models
    config = ModelConfig(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        early_stopping_rounds=20,
        random_state=42,
    )

    # Train and compare
    forecaster = TimeSeriesForecaster(
        models=['xgboost', 'lightgbm', 'catboost'],
        config=config,
    )

    results = forecaster.fit_and_compare(X, y, n_splits=5)

    # Fit best model on full data
    forecaster.fit_best(X, y)

    return forecaster, results


def generate_future_features(
    df: pd.DataFrame,
    last_year: int,
    forecast_years: int,
    feature_cols: list[str],
    target_col: str = 'gdp',
) -> dict[str, pd.DataFrame]:
    """
    Generate feature matrices for future predictions.

    For each country, create feature rows for forecast years
    using the recursive forecasting approach.
    """
    future_features = {}

    for entity in df['entity_code'].unique():
        entity_df = df[df['entity_code'] == entity].copy()
        entity_df = entity_df.sort_values('year')

        if len(entity_df) < 10:
            continue

        # Get the last few years of data for lag features
        recent = entity_df.tail(10).copy()

        future_rows = []
        for future_year in range(last_year + 1, last_year + forecast_years + 1):
            row = {'entity_code': entity, 'year': future_year}

            # Calculate lag features from historical data
            for lag in [1, 2, 3, 4, 5]:
                lag_year = future_year - lag
                lag_data = entity_df[entity_df['year'] == lag_year]
                if len(lag_data) > 0:
                    row[f'{target_col}_lag_{lag}'] = lag_data[target_col].values[0]
                else:
                    row[f'{target_col}_lag_{lag}'] = np.nan

            # Rolling features (use last 5 years)
            last_5_years = entity_df[entity_df['year'] > future_year - 6][target_col]
            if len(last_5_years) >= 3:
                row[f'{target_col}_roll_3_mean'] = last_5_years.tail(3).mean()
                row[f'{target_col}_roll_5_mean'] = last_5_years.tail(5).mean()

            # Copy other features from most recent year
            latest = entity_df[entity_df['year'] == last_year]
            if len(latest) > 0:
                for col in feature_cols:
                    if col not in row and col in latest.columns:
                        row[col] = latest[col].values[0]

            future_rows.append(row)

        if future_rows:
            future_features[entity] = pd.DataFrame(future_rows)

    return future_features


def forecast_gdp(
    countries: list[str] = None,
    forecast_years: int = 6,
) -> dict:
    """
    Main forecasting function.

    Returns dict with:
    - model_results: Performance metrics for each model
    - forecasts: Predicted GDP by country and year
    - feature_importance: Top features driving predictions
    - best_model: Name of best performing model
    """
    if countries is None:
        countries = MAJOR_ECONOMIES

    print(f"Loading GDP data for {len(countries)} countries...")
    df = load_gdp_panel(countries, use_growth=False)

    print("Preparing features...")
    df_features, feature_cols = prepare_forecast_features(df, target_col='value')

    print(f"Training models with {len(feature_cols)} features...")
    forecaster, results = train_gdp_forecaster(
        df_features,
        feature_cols,
        target_col='value'
    )

    print(f"\nModel Performance (MAE in trillion USD):")
    for name, result in results.items():
        mae_trillion = result.mae / 1e12
        print(f"  {name}: {mae_trillion:.3f}T (R²: {result.r2:.3f})")

    print(f"\nBest model: {forecaster.best_model}")

    # Generate forecasts
    print(f"\nGenerating {forecast_years}-year forecasts...")
    last_year = df['year'].max()

    future_features = generate_future_features(
        df_features,
        last_year=last_year,
        forecast_years=forecast_years,
        feature_cols=feature_cols,
        target_col='value',
    )

    forecasts = {}
    for entity, future_df in future_features.items():
        # Fill any remaining NaN with forward fill
        future_df = future_df.ffill()

        # Get features that exist in both training and prediction
        available_features = [f for f in feature_cols if f in future_df.columns]
        X_future = future_df[available_features].fillna(0)

        if len(X_future) > 0:
            try:
                preds = forecaster.forecast(X_future)
                forecasts[entity] = {
                    'years': future_df['year'].tolist(),
                    'predictions': preds.tolist(),
                    'country_name': ECONOMY_NAMES.get(entity, entity),
                }
            except Exception as e:
                print(f"  Warning: Could not forecast {entity}: {e}")

    # Get feature importance from best model
    best_result = results[forecaster.best_model]
    feature_importance = best_result.feature_importance or {}

    # Sort by importance
    top_features = sorted(
        feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return {
        'model_results': {
            name: {
                'mae': result.mae,
                'rmse': result.rmse,
                'r2': result.r2,
            }
            for name, result in results.items()
        },
        'forecasts': forecasts,
        'feature_importance': dict(top_features),
        'best_model': forecaster.best_model,
        'last_historical_year': last_year,
        'forecast_years': list(range(last_year + 1, last_year + forecast_years + 1)),
    }


def get_forecast_data_for_chart(forecast_results: dict) -> pd.DataFrame:
    """Convert forecast results to DataFrame for charting."""
    rows = []

    for entity, data in forecast_results['forecasts'].items():
        for year, pred in zip(data['years'], data['predictions']):
            rows.append({
                'entity_code': entity,
                'country': data['country_name'],
                'year': year,
                'gdp_forecast': pred,
                'gdp_trillion': pred / 1e12,
            })

    return pd.DataFrame(rows)


def get_historical_and_forecast(
    countries: list[str],
    forecast_results: dict,
    historical_years: int = 10,
) -> pd.DataFrame:
    """
    Combine historical GDP with forecasts for visualization.
    """
    last_year = forecast_results['last_historical_year']
    start_year = last_year - historical_years + 1

    # Load historical data
    df_hist = load_gdp_panel(countries, start_year=start_year, end_year=last_year)
    df_hist = df_hist.rename(columns={'value': 'gdp'})
    df_hist['type'] = 'Historical'
    df_hist['gdp_trillion'] = df_hist['gdp'] / 1e12

    # Get forecast data
    df_forecast = get_forecast_data_for_chart(forecast_results)
    df_forecast = df_forecast.rename(columns={'gdp_forecast': 'gdp'})
    df_forecast['type'] = 'Forecast'

    # Combine
    df_combined = pd.concat([
        df_hist[['entity_code', 'year', 'gdp', 'gdp_trillion', 'type']],
        df_forecast[['entity_code', 'year', 'gdp', 'gdp_trillion', 'type']],
    ], ignore_index=True)

    # Add country names
    df_combined['country'] = df_combined['entity_code'].map(ECONOMY_NAMES)

    return df_combined.sort_values(['entity_code', 'year'])


if __name__ == '__main__':
    # Run forecasting
    results = forecast_gdp(MAJOR_ECONOMIES[:5], forecast_years=6)

    print("\n" + "="*60)
    print("FORECAST RESULTS")
    print("="*60)

    for entity, data in results['forecasts'].items():
        print(f"\n{data['country_name']}:")
        for year, pred in zip(data['years'], data['predictions']):
            print(f"  {year}: ${pred/1e12:.2f} trillion")

    print("\n\nTop Features:")
    for feature, importance in results['feature_importance'].items():
        print(f"  {feature}: {importance:.4f}")
