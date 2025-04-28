import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import requests
import os

# --- Fetch Macro Data from FRED ---
def fetch_macro_data(series_codes):
    try:
        fred_api_key = os.getenv("FRED_API_KEY")
        if not fred_api_key:
            raise Exception("FRED API Key not set.")
        
        data = {}
        for code in series_codes:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={fred_api_key}&file_type=json"
            response = requests.get(url)
            if response.status_code == 200:
                observations = response.json().get("observations", [])
                dates = [obs["date"] for obs in observations]
                values = [float(obs["value"]) if obs["value"] != '.' else np.nan for obs in observations]
                series = pd.Series(values, index=pd.to_datetime(dates))
                series = series.asfreq('MS')  # Set frequency to Month Start for FRED data
                data[code] = series
            else:
                raise Exception(f"FRED API error for {code}: {response.status_code}")

        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error fetching macro data: {e}")
        return None

# --- Simple Macro Regime Detection ---
def detect_macro_regime():
    try:
        data = fetch_macro_data(["CPIAUCSL", "GDPC1", "UNRATE", "FEDFUNDS"]).dropna()
        latest = data.iloc[-1]

        cpi = latest["CPIAUCSL"]
        gdp = latest["GDPC1"]
        unemp = latest["UNRATE"]
        fedfunds = latest["FEDFUNDS"]

        if cpi > 300 and gdp < 20000:
            return "Stagflation", "Defensive: Bonds, Utilities, Low Volatility Stocks"
        elif gdp > 21000 and unemp < 4:
            return "Growth", "Aggressive: Tech, Consumer Discretionary"
        else:
            return "Neutral", "Balanced Allocation: SPY + Macro Hedge"
    except Exception:
        return "Unknown", "Hold Cash"

# --- Forecast Prices Using Exponential Smoothing ---
def forecast_prices(series, forecast_days=5):
    try:
        series = series.asfreq('B')  # Set frequency to Business Day for stock price forecasts
        model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
        fitted = model.fit()
        forecast = fitted.forecast(forecast_days)
        return forecast
    except Exception as e:
        raise Exception(f"Forecasting failed: {e}")
