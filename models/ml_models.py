# models/ml_model.py

import numpy as np
import xgboost as xgb
from sklearn.linear_model import LinearRegression

def xgboost_forecast(prices: np.ndarray, forecast_horizon: int = 5) -> float:
    """
    Simple XGBoost-based forecaster using lag features.
    Returns predicted price after the forecast horizon.
    """
    if len(prices) < 30:
        return prices[-1]  # Not enough data to forecast

    # Prepare lag features
    X = []
    y = []
    lag = 5
    for i in range(lag, len(prices) - forecast_horizon):
        X.append(prices[i - lag:i])
        y.append(prices[i + forecast_horizon])
    X = np.array(X)
    y = np.array(y)

    if len(X) == 0:
        return prices[-1]

    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=3)
    model.fit(X, y)

    latest_input = np.array(prices[-lag:]).reshape(1, -1)
    forecast = model.predict(latest_input)[0]

    return forecast


def forecast_ml(prices, forecast_horizon=5):
    return xgboost_forecast(prices, forecast_horizon)
