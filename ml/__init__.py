"""
Graphyard Machine Learning Framework

Predictive analytics for economic time series with:
- Handling missing data and irregular time series
- Multi-country panel data with different start dates
- Lag features and rolling window optimization
- GPU acceleration via PyTorch MPS (Apple Silicon)

Packages (2025 versions):
- PyTorch 2.9+ with MPS backend for Apple Silicon GPU
- XGBoost 3.1+ for gradient boosting
- LightGBM 4.6+ for fast leaf-wise boosting
- CatBoost 1.2+ for categorical feature handling
- Skforecast 0.19+ for time series forecasting utilities

Key Challenges Addressed:
1. Different countries start data collection at different years
2. Missing values (MCAR, MAR, MNAR patterns)
3. Optimal lag/window selection for predictions
4. Long-term vs short-term forecasting accuracy

References:
- https://skforecast.org/0.14.0/user_guides/forecasting-xgboost-lightgbm.html
- https://cienciadedatos.net/documentos/py39-forecasting-time-series-with-skforecast-xgboost-lightgbm-catboost
"""

from .forecaster import TimeSeriesForecaster, PanelForecaster
from .preprocessing import prepare_panel_data, handle_missing_values

__all__ = [
    'TimeSeriesForecaster',
    'PanelForecaster',
    'prepare_panel_data',
    'handle_missing_values',
]
