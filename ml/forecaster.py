"""
Time Series Forecasters

Gradient boosting models optimized for economic time series:
- XGBoost: Depth-wise tree growth, good general performance
- LightGBM: Leaf-wise growth, faster training, lower memory
- CatBoost: Best for categorical features, handles missing values natively

All models run on CPU for Apple Silicon (GPU not yet supported for these).
For deep learning, use PyTorch with MPS backend.

Based on 2025 benchmarks and best practices.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Literal, Any
import numpy as np
import pandas as pd

import xgboost as xgb
import lightgbm as lgb
import catboost as cb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


@dataclass
class ForecastResult:
    """Results from a forecast model."""
    model_name: str
    predictions: np.ndarray
    actuals: Optional[np.ndarray]
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None
    feature_importance: Optional[dict] = None
    forecast_horizon: int = 1
    confidence_intervals: Optional[tuple] = None


@dataclass
class ModelConfig:
    """Configuration for gradient boosting models."""
    n_estimators: int = 100
    max_depth: int = 6
    learning_rate: float = 0.1
    early_stopping_rounds: int = 10
    random_state: int = 42
    extra_params: dict = field(default_factory=dict)


class BaseForecaster(ABC):
    """Abstract base for all forecasters."""

    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self.model = None
        self.feature_names: list[str] = []

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaseForecaster":
        """Fit the model."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate predictions."""
        pass

    def evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> ForecastResult:
        """Evaluate model on test data."""
        predictions = self.predict(X)
        actuals = y.values

        return ForecastResult(
            model_name=self.__class__.__name__,
            predictions=predictions,
            actuals=actuals,
            mae=mean_absolute_error(actuals, predictions),
            rmse=np.sqrt(mean_squared_error(actuals, predictions)),
            r2=r2_score(actuals, predictions),
            feature_importance=self.get_feature_importance(),
        )

    @abstractmethod
    def get_feature_importance(self) -> dict:
        """Get feature importance scores."""
        pass


class XGBoostForecaster(BaseForecaster):
    """
    XGBoost forecaster for time series.

    Advantages:
    - Excellent accuracy on tabular data
    - Handles missing values automatically
    - Regularization to prevent overfitting
    """

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "XGBoostForecaster":
        self.feature_names = list(X.columns)

        self.model = xgb.XGBRegressor(
            n_estimators=self.config.n_estimators,
            max_depth=self.config.max_depth,
            learning_rate=self.config.learning_rate,
            random_state=self.config.random_state,
            early_stopping_rounds=self.config.early_stopping_rounds,
            **self.config.extra_params,
        )

        # Use validation set for early stopping
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


class LightGBMForecaster(BaseForecaster):
    """
    LightGBM forecaster for time series.

    Advantages:
    - Faster training than XGBoost
    - Lower memory usage
    - Leaf-wise tree growth captures complex patterns
    """

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LightGBMForecaster":
        self.feature_names = list(X.columns)

        self.model = lgb.LGBMRegressor(
            n_estimators=self.config.n_estimators,
            max_depth=self.config.max_depth,
            learning_rate=self.config.learning_rate,
            random_state=self.config.random_state,
            **self.config.extra_params,
        )

        # Use validation set for early stopping
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(self.config.early_stopping_rounds)],
        )

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


class CatBoostForecaster(BaseForecaster):
    """
    CatBoost forecaster for time series.

    Advantages:
    - Handles categorical features natively
    - Robust to overfitting
    - Ordered boosting reduces prediction shift
    """

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "CatBoostForecaster":
        self.feature_names = list(X.columns)

        self.model = cb.CatBoostRegressor(
            iterations=self.config.n_estimators,
            depth=self.config.max_depth,
            learning_rate=self.config.learning_rate,
            random_seed=self.config.random_state,
            early_stopping_rounds=self.config.early_stopping_rounds,
            verbose=False,
            **self.config.extra_params,
        )

        # Use validation set for early stopping
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        self.model.fit(
            X_train, y_train,
            eval_set=(X_val, y_val),
        )

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X)

    def get_feature_importance(self) -> dict:
        if self.model is None:
            return {}
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


class TimeSeriesForecaster:
    """
    High-level time series forecaster with model comparison.

    Compares XGBoost, LightGBM, and CatBoost using walk-forward validation
    (the proper way to evaluate time series models).
    """

    def __init__(
        self,
        models: list[Literal["xgboost", "lightgbm", "catboost"]] = None,
        config: Optional[ModelConfig] = None,
    ):
        if models is None:
            models = ["xgboost", "lightgbm", "catboost"]

        self.config = config or ModelConfig()
        self.models: dict[str, BaseForecaster] = {}

        model_classes = {
            "xgboost": XGBoostForecaster,
            "lightgbm": LightGBMForecaster,
            "catboost": CatBoostForecaster,
        }

        for name in models:
            self.models[name] = model_classes[name](self.config)

        self.results: dict[str, ForecastResult] = {}
        self.best_model: Optional[str] = None

    def fit_and_compare(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5,
    ) -> dict[str, ForecastResult]:
        """
        Fit all models and compare using TimeSeriesSplit.

        Uses walk-forward validation which is the correct approach
        for time series (unlike k-fold which leaks future information).
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        results = {name: [] for name in self.models}

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            for name, model in self.models.items():
                # Create fresh model for each fold
                model_class = model.__class__
                fold_model = model_class(self.config)
                fold_model.fit(X_train, y_train)
                result = fold_model.evaluate(X_test, y_test)
                results[name].append(result)

        # Aggregate results
        self.results = {}
        best_mae = float("inf")

        for name, fold_results in results.items():
            avg_mae = np.mean([r.mae for r in fold_results])
            avg_rmse = np.mean([r.rmse for r in fold_results])
            avg_r2 = np.mean([r.r2 for r in fold_results])

            self.results[name] = ForecastResult(
                model_name=name,
                predictions=np.concatenate([r.predictions for r in fold_results]),
                actuals=np.concatenate([r.actuals for r in fold_results]),
                mae=avg_mae,
                rmse=avg_rmse,
                r2=avg_r2,
                feature_importance=fold_results[-1].feature_importance,
            )

            if avg_mae < best_mae:
                best_mae = avg_mae
                self.best_model = name

        return self.results

    def fit_best(self, X: pd.DataFrame, y: pd.Series) -> BaseForecaster:
        """Fit the best model on full data after comparison."""
        if self.best_model is None:
            raise ValueError("Run fit_and_compare first")

        self.models[self.best_model].fit(X, y)
        return self.models[self.best_model]

    def forecast(
        self,
        X_future: pd.DataFrame,
        model_name: Optional[str] = None,
    ) -> np.ndarray:
        """Generate forecasts using specified or best model."""
        name = model_name or self.best_model
        if name is None:
            raise ValueError("No model selected")
        return self.models[name].predict(X_future)


class PanelForecaster:
    """
    Forecaster for panel data (multiple entities over time).

    Handles the challenge of different countries having different
    data availability periods.
    """

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        model_type: Literal["xgboost", "lightgbm", "catboost"] = "lightgbm",
    ):
        self.config = config or ModelConfig()
        self.model_type = model_type
        self.models: dict[str, BaseForecaster] = {}

    def fit_per_entity(
        self,
        df: pd.DataFrame,
        target_col: str,
        feature_cols: list[str],
        entity_col: str = "entity_code",
    ) -> dict[str, ForecastResult]:
        """
        Fit a separate model per entity.

        Good for capturing entity-specific patterns but requires
        sufficient data per entity.
        """
        results = {}
        model_classes = {
            "xgboost": XGBoostForecaster,
            "lightgbm": LightGBMForecaster,
            "catboost": CatBoostForecaster,
        }

        for entity in df[entity_col].unique():
            subset = df[df[entity_col] == entity].dropna(subset=feature_cols + [target_col])

            if len(subset) < 10:
                continue

            X = subset[feature_cols]
            y = subset[target_col]

            model = model_classes[self.model_type](self.config)
            model.fit(X, y)
            result = model.evaluate(X, y)

            self.models[entity] = model
            results[entity] = result

        return results

    def fit_global(
        self,
        df: pd.DataFrame,
        target_col: str,
        feature_cols: list[str],
        entity_col: str = "entity_code",
    ) -> ForecastResult:
        """
        Fit a single global model across all entities.

        Better when individual entities have limited data.
        Entity can be included as a feature for entity-specific effects.
        """
        # Add entity as categorical feature
        df_model = df.dropna(subset=feature_cols + [target_col]).copy()
        df_model["entity_encoded"] = pd.Categorical(df_model[entity_col]).codes
        feature_cols_with_entity = feature_cols + ["entity_encoded"]

        X = df_model[feature_cols_with_entity]
        y = df_model[target_col]

        model_classes = {
            "xgboost": XGBoostForecaster,
            "lightgbm": LightGBMForecaster,
            "catboost": CatBoostForecaster,
        }

        self.global_model = model_classes[self.model_type](self.config)
        self.global_model.fit(X, y)

        return self.global_model.evaluate(X, y)

    def forecast_entity(
        self,
        entity: str,
        X_future: pd.DataFrame,
    ) -> np.ndarray:
        """Forecast for a specific entity using per-entity model."""
        if entity not in self.models:
            raise ValueError(f"No model for entity {entity}")
        return self.models[entity].predict(X_future)
