import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def forecast_arima(df, horizon="1 Week"):
    steps = {"1 Day": 1, "1 Week": 5, "1 Month": 21}.get(horizon, 5)
    close = df["Close"].dropna()

    # If empty or too short, return fallback
    if close.empty or len(close) < 10:
        return pd.Series([100.0] * steps)  # fallback dummy value

    try:
        model = ARIMA(close, order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return forecast.reset_index(drop=True)
    except Exception as e:
        print(f"[ARIMA ERROR] {e}")
        return pd.Series([close.iloc[-1]] * steps)
